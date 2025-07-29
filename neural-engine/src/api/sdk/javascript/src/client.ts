/**
 * NeuraScale API Client
 */

import axios, { AxiosInstance, AxiosError } from "axios";
import {
  Device,
  DeviceCreate,
  DeviceUpdate,
  Session,
  SessionCreate,
  Patient,
  PatientCreate,
  NeuralData,
  Analysis,
  MLModel,
  PaginatedResponse,
} from "./models";
import {
  NeuraScaleError,
  AuthenticationError,
  NotFoundError,
  ValidationError,
  RateLimitError,
} from "./exceptions";
import { NeuraScaleConfig, RequestOptions } from "./types";

export class NeuraScaleClient {
  private client: AxiosInstance;
  private config: NeuraScaleConfig;

  constructor(config: NeuraScaleConfig) {
    this.config = {
      baseURL: "https://api.neurascale.com",
      timeout: 30000,
      maxRetries: 3,
      ...config,
    };

    this.client = axios.create({
      baseURL: this.config.baseURL,
      timeout: this.config.timeout,
      headers: {
        Authorization: `Bearer ${this.config.apiKey}`,
        "Content-Type": "application/json",
        "User-Agent": "NeuraScale-JS-SDK/2.0.0",
      },
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => this.handleError(error),
    );
  }

  private async handleError(error: AxiosError): Promise<never> {
    if (error.response) {
      const { status, data } = error.response;
      const errorData = data as any;

      switch (status) {
        case 401:
          throw new AuthenticationError(
            errorData?.error?.message || "Authentication failed",
          );
        case 404:
          throw new NotFoundError(
            errorData?.error?.message || "Resource not found",
          );
        case 422:
          throw new ValidationError(
            errorData?.error?.message || "Validation failed",
            errorData?.error?.details,
          );
        case 429:
          const retryAfter = parseInt(
            error.response.headers["retry-after"] || "60",
          );
          throw new RateLimitError("Rate limit exceeded", retryAfter);
        default:
          throw new NeuraScaleError(`API error: ${status}`, status, errorData);
      }
    } else if (error.request) {
      throw new NeuraScaleError("Network error: No response received");
    } else {
      throw new NeuraScaleError(`Request error: ${error.message}`);
    }
  }

  // Device methods
  async getDevice(deviceId: string, options?: RequestOptions): Promise<Device> {
    const response = await this.client.get<Device>(
      `/api/v2/devices/${deviceId}`,
      { signal: options?.signal },
    );
    return response.data;
  }

  async listDevices(
    params?: {
      status?: string;
      type?: string;
      search?: string;
      page?: number;
      size?: number;
    },
    options?: RequestOptions,
  ): Promise<PaginatedResponse<Device>> {
    const response = await this.client.get<PaginatedResponse<Device>>(
      "/api/v2/devices",
      { params, signal: options?.signal },
    );
    return response.data;
  }

  async createDevice(
    device: DeviceCreate,
    options?: RequestOptions,
  ): Promise<Device> {
    const response = await this.client.post<Device>("/api/v2/devices", device, {
      signal: options?.signal,
    });
    return response.data;
  }

  async updateDevice(
    deviceId: string,
    update: DeviceUpdate,
    options?: RequestOptions,
  ): Promise<Device> {
    const response = await this.client.patch<Device>(
      `/api/v2/devices/${deviceId}`,
      update,
      { signal: options?.signal },
    );
    return response.data;
  }

  async deleteDevice(
    deviceId: string,
    options?: RequestOptions,
  ): Promise<void> {
    await this.client.delete(`/api/v2/devices/${deviceId}`, {
      signal: options?.signal,
    });
  }

  async calibrateDevice(
    deviceId: string,
    parameters: Record<string, any>,
    options?: RequestOptions,
  ): Promise<Device> {
    const response = await this.client.post<Device>(
      `/api/v2/devices/${deviceId}/calibration`,
      parameters,
      { signal: options?.signal },
    );
    return response.data;
  }

  // Session methods
  async getSession(
    sessionId: string,
    options?: RequestOptions,
  ): Promise<Session> {
    const response = await this.client.get<Session>(
      `/api/v2/sessions/${sessionId}`,
      { signal: options?.signal },
    );
    return response.data;
  }

  async listSessions(
    params?: {
      patientId?: string;
      deviceId?: string;
      status?: string;
      startDate?: Date;
      endDate?: Date;
      page?: number;
      size?: number;
    },
    options?: RequestOptions,
  ): Promise<PaginatedResponse<Session>> {
    const queryParams = params
      ? {
          ...params,
          startDate: params.startDate?.toISOString(),
          endDate: params.endDate?.toISOString(),
        }
      : undefined;

    const response = await this.client.get<PaginatedResponse<Session>>(
      "/api/v2/sessions",
      { params: queryParams, signal: options?.signal },
    );
    return response.data;
  }

  async createSession(
    session: SessionCreate,
    options?: RequestOptions,
  ): Promise<Session> {
    const response = await this.client.post<Session>(
      "/api/v2/sessions",
      session,
      { signal: options?.signal },
    );
    return response.data;
  }

  async startSession(
    sessionId: string,
    options?: RequestOptions,
  ): Promise<Session> {
    const response = await this.client.post<Session>(
      `/api/v2/sessions/${sessionId}/start`,
      {},
      { signal: options?.signal },
    );
    return response.data;
  }

  async stopSession(
    sessionId: string,
    options?: RequestOptions,
  ): Promise<Session> {
    const response = await this.client.post<Session>(
      `/api/v2/sessions/${sessionId}/stop`,
      {},
      { signal: options?.signal },
    );
    return response.data;
  }

  async exportSession(
    sessionId: string,
    format: string,
    params?: {
      channels?: number[];
      startTime?: number;
      endTime?: number;
    },
    options?: RequestOptions,
  ): Promise<{ exportId: string; status: string; _links: any }> {
    const response = await this.client.post(
      `/api/v2/sessions/${sessionId}/export`,
      { format, ...params },
      { signal: options?.signal },
    );
    return response.data;
  }

  // Neural data methods
  async getNeuralData(
    sessionId: string,
    params?: {
      startTime?: number;
      endTime?: number;
      channels?: number[];
      downsample?: number;
    },
    options?: RequestOptions,
  ): Promise<NeuralData> {
    const queryParams = params
      ? {
          ...params,
          channels: params.channels?.join(","),
        }
      : undefined;

    const response = await this.client.get<NeuralData>(
      `/api/v2/neural-data/sessions/${sessionId}`,
      { params: queryParams, signal: options?.signal },
    );
    return response.data;
  }

  // Patient methods
  async getPatient(
    patientId: string,
    options?: RequestOptions,
  ): Promise<Patient> {
    const response = await this.client.get<Patient>(
      `/api/v2/patients/${patientId}`,
      { signal: options?.signal },
    );
    return response.data;
  }

  async createPatient(
    patient: PatientCreate,
    options?: RequestOptions,
  ): Promise<Patient> {
    const response = await this.client.post<Patient>(
      "/api/v2/patients",
      patient,
      { signal: options?.signal },
    );
    return response.data;
  }

  // Analysis methods
  async getAnalysis(
    analysisId: string,
    options?: RequestOptions,
  ): Promise<Analysis> {
    const response = await this.client.get<Analysis>(
      `/api/v2/analysis/${analysisId}`,
      { signal: options?.signal },
    );
    return response.data;
  }

  async startAnalysis(
    sessionId: string,
    analysisType: string,
    parameters?: Record<string, any>,
    options?: RequestOptions,
  ): Promise<Analysis> {
    const response = await this.client.post<Analysis>(
      "/api/v2/analysis",
      {
        sessionId,
        type: analysisType,
        parameters: parameters || {},
      },
      { signal: options?.signal },
    );
    return response.data;
  }

  // ML Model methods
  async getModel(modelId: string, options?: RequestOptions): Promise<MLModel> {
    const response = await this.client.get<MLModel>(
      `/api/v2/ml-models/${modelId}`,
      { signal: options?.signal },
    );
    return response.data;
  }

  async predict(
    modelId: string,
    data: Record<string, any>,
    options?: RequestOptions,
  ): Promise<any> {
    const response = await this.client.post(
      `/api/v2/ml-models/${modelId}/predict`,
      data,
      { signal: options?.signal },
    );
    return response.data;
  }

  // Batch operations
  async batchOperations(
    operations: Array<{
      operation: string;
      resource: string;
      data?: any;
    }>,
    options?: RequestOptions,
  ): Promise<any[]> {
    const response = await this.client.post("/api/v2/batch", operations, {
      signal: options?.signal,
    });
    return response.data;
  }
}
