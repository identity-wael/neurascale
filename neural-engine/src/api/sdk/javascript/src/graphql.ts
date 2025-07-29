/**
 * GraphQL Client for NeuraScale
 */

import axios, { AxiosInstance } from "axios";
import { GraphQLConfig, GraphQLQueryOptions } from "./types";
import { NeuraScaleError } from "./exceptions";

export class GraphQLClient {
  private client: AxiosInstance;
  private config: GraphQLConfig;

  constructor(config: GraphQLConfig) {
    this.config = {
      endpoint: "https://api.neurascale.com/graphql",
      timeout: 30000,
      ...config,
    };

    this.client = axios.create({
      baseURL: this.config.endpoint,
      timeout: this.config.timeout,
      headers: {
        Authorization: `Bearer ${this.config.apiKey}`,
        "Content-Type": "application/json",
      },
    });
  }

  async query<T = any>(options: GraphQLQueryOptions): Promise<T> {
    try {
      const response = await this.client.post(
        "",
        {
          query: options.query,
          variables: options.variables,
        },
        {
          signal: options.signal,
        },
      );

      if (response.data.errors) {
        throw new NeuraScaleError(
          response.data.errors[0]?.message || "GraphQL query failed",
          undefined,
          response.data.errors,
        );
      }

      return response.data.data;
    } catch (error: any) {
      if (error.response) {
        throw new NeuraScaleError(
          `GraphQL error: ${error.response.status}`,
          error.response.status,
          error.response.data,
        );
      }
      throw error;
    }
  }

  async mutation<T = any>(options: GraphQLQueryOptions): Promise<T> {
    return this.query<T>(options);
  }

  // Convenience methods
  async getDevice(deviceId: string): Promise<any> {
    const query = `
      query GetDevice($id: String!) {
        device(id: $id) {
          id
          name
          type
          status
          serialNumber
          firmwareVersion
          lastSeen
          channelCount
          samplingRate
        }
      }
    `;

    const result = await this.query({ query, variables: { id: deviceId } });
    return result.device;
  }

  async listDevices(
    filter?: Record<string, any>,
    first: number = 10,
    after?: string,
  ): Promise<any> {
    const query = `
      query ListDevices($filter: DeviceFilter, $first: Int, $after: String) {
        devices(filter: $filter, pagination: {first: $first, after: $after}) {
          edges {
            node {
              id
              name
              type
              status
              serialNumber
              lastSeen
            }
            cursor
          }
          pageInfo {
            hasNextPage
            hasPreviousPage
            startCursor
            endCursor
          }
          totalCount
        }
      }
    `;

    const variables: any = { first };
    if (filter) variables.filter = filter;
    if (after) variables.after = after;

    const result = await this.query({ query, variables });
    return result.devices;
  }

  async getSessionWithData(sessionId: string): Promise<any> {
    const query = `
      query GetSessionWithData($id: String!) {
        session(id: $id) {
          id
          patientId
          deviceId
          startTime
          endTime
          duration
          status
          channelCount
          samplingRate
          device {
            id
            name
            type
          }
          patient {
            id
            externalId
          }
          neuralData(channels: [0, 1, 2, 3]) {
            startTime
            endTime
            samplingRate
            dataShape
          }
        }
      }
    `;

    const result = await this.query({ query, variables: { id: sessionId } });
    return result.session;
  }

  async startAnalysis(
    sessionId: string,
    analysisType: string,
    parameters?: Record<string, any>,
  ): Promise<any> {
    const mutation = `
      mutation StartAnalysis($input: StartAnalysisInput!) {
        startAnalysis(input: $input) {
          analysis {
            id
            sessionId
            type
            status
            createdAt
          }
          success
          message
        }
      }
    `;

    const variables = {
      input: {
        sessionId,
        type: analysisType,
        parameters: parameters || {},
      },
    };

    const result = await this.mutation({ query: mutation, variables });
    return result.startAnalysis;
  }

  // Subscription support would require WebSocket implementation
  subscribe(subscription: string, variables?: Record<string, any>): void {
    throw new Error(
      "Subscriptions not yet implemented. Use StreamClient for real-time data.",
    );
  }
}
