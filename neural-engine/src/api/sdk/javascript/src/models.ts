/**
 * NeuraScale SDK Models
 */

export enum DeviceType {
  EEG = "EEG",
  EMG = "EMG",
  ECG = "ECG",
  fNIRS = "fNIRS",
  TMS = "TMS",
  tDCS = "tDCS",
  HYBRID = "HYBRID",
}

export enum DeviceStatus {
  ONLINE = "ONLINE",
  OFFLINE = "OFFLINE",
  MAINTENANCE = "MAINTENANCE",
  ERROR = "ERROR",
}

export enum SessionStatus {
  PREPARING = "PREPARING",
  RECORDING = "RECORDING",
  PAUSED = "PAUSED",
  COMPLETED = "COMPLETED",
  FAILED = "FAILED",
}

export interface Device {
  id: string;
  name: string;
  type: DeviceType;
  status: DeviceStatus;
  serialNumber: string;
  firmwareVersion: string;
  lastSeen: Date;
  channelCount: number;
  samplingRate: number;
  calibration?: Record<string, any>;
  metadata: Record<string, any>;
}

export interface DeviceCreate {
  name: string;
  type: DeviceType;
  serialNumber: string;
  firmwareVersion: string;
  metadata?: Record<string, any>;
}

export interface DeviceUpdate {
  name?: string;
  status?: DeviceStatus;
  firmwareVersion?: string;
  metadata?: Record<string, any>;
}

export interface Session {
  id: string;
  patientId: string;
  deviceId: string;
  startTime: Date;
  endTime?: Date;
  duration?: number;
  status: SessionStatus;
  channelCount: number;
  samplingRate: number;
  metadata: Record<string, any>;
  dataSize?: number;
}

export interface SessionCreate {
  patientId: string;
  deviceId: string;
  channelCount: number;
  samplingRate: number;
  metadata?: Record<string, any>;
}

export interface Patient {
  id: string;
  externalId: string;
  createdAt: Date;
  metadata: Record<string, any>;
}

export interface PatientCreate {
  externalId: string;
  metadata: Record<string, any>;
}

export interface NeuralData {
  sessionId: string;
  startTime: number;
  endTime: number;
  channels: number[];
  samplingRate: number;
  dataShape: number[];
  dataUrl?: string;
  statistics?: Record<string, any>;
}

export interface Analysis {
  id: string;
  sessionId: string;
  type: string;
  status: string;
  createdAt: Date;
  completedAt?: Date;
  results?: Record<string, any>;
}

export interface MLModel {
  id: string;
  name: string;
  type: string;
  version: string;
  status: string;
  accuracy?: number;
  createdAt: Date;
  updatedAt: Date;
  metadata: Record<string, any>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
  hasNext?: boolean;
  hasPrev?: boolean;
  _links?: Record<string, any>;
}
