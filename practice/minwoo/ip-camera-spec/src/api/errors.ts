import type { FastifyError, FastifyReply } from 'fastify';
import type { ApiError } from '../domain/camera.js';

export const errorCodes = {
  invalidInput: 'INVALID_INPUT',
  duplicateCamera: 'DUPLICATE_CAMERA_ID',
  cameraNotFound: 'CAMERA_NOT_FOUND',
  internalError: 'INTERNAL_ERROR',
} as const;

export class ApplicationError extends Error {
  constructor(
    readonly statusCode: number,
    readonly code: string,
    message: string,
    readonly fieldErrors?: Record<string, string>,
  ) {
    super(message);
  }
}

export function sendHttpError(error: unknown, reply: FastifyReply): void {
  if (error instanceof ApplicationError) {
    const body: ApiError = { code: error.code, message: error.message };
    if (error.fieldErrors) body.fieldErrors = error.fieldErrors;
    void reply.status(error.statusCode).send(body);
    return;
  }

  const fastifyError = error as FastifyError;
  if (fastifyError.validation) {
    const fieldErrors = Object.fromEntries(
      fastifyError.validation.map((issue) => [
        issue.instancePath || issue.params.missingProperty || 'request',
        issue.message ?? 'is invalid',
      ]),
    );
    void reply.status(400).send({
      code: errorCodes.invalidInput,
      message: 'Request validation failed',
      fieldErrors,
    } satisfies ApiError);
    return;
  }

  reply.log.error(error);
  void reply.status(500).send({
    code: errorCodes.internalError,
    message: 'An internal error occurred',
  } satisfies ApiError);
}
