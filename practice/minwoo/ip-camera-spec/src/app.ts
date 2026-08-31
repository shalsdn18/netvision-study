import Fastify, { type FastifyInstance } from 'fastify';
import { registerCameraRoutes } from './api/camera-routes.js';
import { sendHttpError } from './api/errors.js';
import { CameraService } from './domain/camera-service.js';
import { CameraRepository } from './storage/camera-repository.js';
import { openDatabase } from './storage/database.js';

export interface BuildAppOptions {
  databasePath: string;
  logger?: boolean;
}

export async function buildApp(options: BuildAppOptions): Promise<FastifyInstance> {
  const app = Fastify({ logger: options.logger ?? false });
  const database = openDatabase(options.databasePath);
  const repository = new CameraRepository(database);
  const service = new CameraService(repository);

  app.setErrorHandler((error, _request, reply) => sendHttpError(error, reply));
  app.addHook('onClose', async () => database.close());
  await registerCameraRoutes(app, service);
  await app.ready();
  return app;
}
