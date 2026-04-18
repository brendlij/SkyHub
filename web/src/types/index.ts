// Config Types
export interface ConfigValue {
  type: 'string' | 'integer' | 'float' | 'boolean';
  default: any;
  description?: string;
  min?: number;
  max?: number;
  allowed_values?: any[];
  unit?: string;
}

export interface ConfigSchema {
  [key: string]: ConfigValue;
}

export interface SystemConfig {
  observer_name?: string;
  storage_policy?: string;
  auto_cleanup_days?: number;
  max_storage_gb?: number;
  image_format?: string;
  compression_level?: number;
}

export interface CameraConfig {
  exposure?: number;
  gain?: number;
  resolution?: string;
  frame_rate?: number;
  enabled?: boolean;
  capture_interval?: number;
  white_balance?: string;
  iso?: number;
}

export interface NodeConfig {
  capture_enabled?: boolean;
  upload_enabled?: boolean;
  upload_interval?: number;
  max_retries?: number;
}

// Capture Types
export interface CaptureMetadata {
  exposure?: number;
  gain?: number;
  resolution?: string;
  frame_rate?: number;
  white_balance?: string;
  iso?: number;
}

export interface CaptureDetailResponse {
  id: string;
  node_id: string;
  camera_id: string;
  timestamp: string;
  file_path: string;
  file_size: number;
  image_format: string;
  day_phase: 'day' | 'night' | 'twilight';
  metadata?: CaptureMetadata;
}

export interface CaptureListResponse {
  date: string;
  captures: CaptureDetailResponse[];
}

// Event Types
export const EventType = {
  CONFIG_CHANGED: 'CONFIG_CHANGED',
  CAPTURE_STARTED: 'CAPTURE_STARTED',
  CAPTURE_COMPLETED: 'CAPTURE_COMPLETED',
  NODE_CONNECTED: 'NODE_CONNECTED',
  ERROR: 'ERROR',
} as const;

export type EventType = typeof EventType[keyof typeof EventType];

export interface Event {
  type: EventType | string;
  timestamp: string;
  scope: string;
  data: Record<string, any>;
}

// API Response Types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

export interface ApiError {
  message: string;
  status: number;
  details?: Record<string, any>;
}
