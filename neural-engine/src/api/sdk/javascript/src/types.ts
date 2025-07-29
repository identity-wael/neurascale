/**
 * NeuraScale SDK Types
 */

export interface NeuraScaleConfig {
  apiKey: string;
  baseURL?: string;
  timeout?: number;
  maxRetries?: number;
}

export interface RequestOptions {
  signal?: AbortSignal;
}

export interface BatchOperation {
  operation: "create" | "update" | "delete";
  resource: string;
  id?: string;
  data?: any;
}

export interface GraphQLConfig {
  apiKey: string;
  endpoint?: string;
  timeout?: number;
}

export interface GraphQLQueryOptions {
  query: string;
  variables?: Record<string, any>;
  signal?: AbortSignal;
}

export interface WebSocketConfig {
  url: string;
  token: string;
  reconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export interface StreamFrame {
  timestamp: number;
  sessionId: string;
  channels: number[];
  data: number[][];
  samplingRate: number;
}
