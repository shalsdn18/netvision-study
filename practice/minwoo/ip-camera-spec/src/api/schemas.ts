const ipv4Pattern =
  '^(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])(\\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])){3}$';

export const cameraIdSchema = { type: 'string', minLength: 1 } as const;

export const cameraInputSchema = {
  type: 'object',
  required: ['cameraId', 'cameraName', 'ipAddress'],
  additionalProperties: false,
  properties: {
    cameraId: cameraIdSchema,
    cameraName: { type: 'string', minLength: 1 },
    ipAddress: { type: 'string', pattern: ipv4Pattern },
  },
} as const;

export const cameraUpdateSchema = {
  type: 'object',
  required: ['cameraName', 'ipAddress'],
  additionalProperties: false,
  properties: {
    cameraName: { type: 'string', minLength: 1 },
    ipAddress: { type: 'string', pattern: ipv4Pattern },
  },
} as const;

export const cameraSchema = cameraInputSchema;
export const cameraListSchema = { type: 'array', items: cameraSchema } as const;

export const tcpPortSchema = { type: 'integer', minimum: 1, maximum: 65535 } as const;

export const apiErrorSchema = {
  type: 'object',
  required: ['code', 'message'],
  additionalProperties: false,
  properties: {
    code: { type: 'string' },
    message: { type: 'string' },
    fieldErrors: {
      type: 'object',
      additionalProperties: { type: 'string' },
    },
  },
} as const;
