import type { FastifyInstance } from 'fastify';
import type { Camera, CameraUpdate } from '../domain/camera.js';
import type { CameraService } from '../domain/camera-service.js';
import {
  apiErrorSchema,
  cameraIdSchema,
  cameraInputSchema,
  cameraListSchema,
  cameraSchema,
  cameraUpdateSchema,
} from './schemas.js';

interface CameraParams {
  cameraId: string;
}

export async function registerCameraRoutes(
  app: FastifyInstance,
  cameraService: CameraService,
): Promise<void> {
  app.post<{ Body: Camera }>('/cameras', {
    schema: {
      body: cameraInputSchema,
      response: { 201: cameraSchema, 400: apiErrorSchema, 409: apiErrorSchema },
    },
    handler: async (request, reply) => reply.status(201).send(cameraService.create(request.body)),
  });

  app.get('/cameras', {
    schema: { response: { 200: cameraListSchema } },
    handler: async () => cameraService.list(),
  });

  app.get<{ Params: CameraParams }>('/cameras/:cameraId', {
    schema: {
      params: {
        type: 'object',
        required: ['cameraId'],
        properties: { cameraId: cameraIdSchema },
      },
      response: { 200: cameraSchema, 404: apiErrorSchema },
    },
    handler: async (request) => cameraService.get(request.params.cameraId),
  });

  app.put<{ Params: CameraParams; Body: CameraUpdate }>('/cameras/:cameraId', {
    schema: {
      params: {
        type: 'object',
        required: ['cameraId'],
        properties: { cameraId: cameraIdSchema },
      },
      body: cameraUpdateSchema,
      response: { 200: cameraSchema, 400: apiErrorSchema, 404: apiErrorSchema },
    },
    handler: async (request) => cameraService.update(request.params.cameraId, request.body),
  });

  app.delete<{ Params: CameraParams }>('/cameras/:cameraId', {
    schema: {
      params: {
        type: 'object',
        required: ['cameraId'],
        properties: { cameraId: cameraIdSchema },
      },
      response: { 404: apiErrorSchema },
    },
    handler: async (request, reply) => {
      cameraService.delete(request.params.cameraId);
      return reply.status(204).send();
    },
  });
}
