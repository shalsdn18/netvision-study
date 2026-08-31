import { resolve } from 'node:path';

export interface AppConfig {
  databasePath: string;
  host: string;
  port: number;
}

export function loadConfig(environment: NodeJS.ProcessEnv = process.env): AppConfig {
  const parsedPort = Number(environment.PORT ?? '3000');
  if (!Number.isInteger(parsedPort) || parsedPort < 1 || parsedPort > 65535) {
    throw new Error('PORT must be an integer between 1 and 65535');
  }

  return {
    databasePath: resolve(environment.DATABASE_PATH ?? 'data/ip-cameras.db'),
    host: environment.HOST ?? '127.0.0.1',
    port: parsedPort,
  };
}
