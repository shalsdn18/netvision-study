import { mkdtemp, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import type { FastifyInstance } from 'fastify';
import { buildApp } from '../../src/app.js';

export interface TestApp {
  app: FastifyInstance;
  databasePath: string;
  close: () => Promise<void>;
}

export async function createTestApp(databasePath?: string): Promise<TestApp> {
  const directory = databasePath ? undefined : await mkdtemp(join(tmpdir(), 'ip-camera-test-'));
  const resolvedPath = databasePath ?? join(directory!, 'cameras.db');
  const app = await buildApp({ databasePath: resolvedPath });

  return {
    app,
    databasePath: resolvedPath,
    close: async () => {
      await app.close();
      if (directory) await rm(directory, { recursive: true, force: true });
    },
  };
}
