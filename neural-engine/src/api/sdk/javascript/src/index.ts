/**
 * NeuraScale TypeScript/JavaScript SDK
 */

export { NeuraScaleClient } from "./client";
export { GraphQLClient } from "./graphql";
export * from "./models";
export * from "./exceptions";
export { StreamClient } from "./streaming";

// Re-export types
export type {
  Device,
  DeviceType,
  DeviceStatus,
  DeviceCreate,
  DeviceUpdate,
  Session,
  SessionStatus,
  SessionCreate,
  Patient,
  PatientCreate,
  NeuralData,
  Analysis,
  MLModel,
  PaginatedResponse,
} from "./models";

export type { NeuraScaleConfig, RequestOptions, BatchOperation } from "./types";

// Version
export const VERSION = "2.0.0";
