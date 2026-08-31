export interface Camera {
  cameraId: string;
  cameraName: string;
  ipAddress: string;
}

export interface CameraUpdate {
  cameraName: string;
  ipAddress: string;
}

export type DiagnosticType = 'ping' | 'tcp-port';
export type DiagnosticStatus = 'success' | 'failure' | 'timeout';

export interface NetworkDiagnosticResult {
  cameraId: string;
  diagnosticType: DiagnosticType;
  status: DiagnosticStatus;
  port?: number;
  latencyMs?: number;
  message?: string;
}

export interface ApiError {
  code: string;
  message: string;
  fieldErrors?: Record<string, string>;
}
