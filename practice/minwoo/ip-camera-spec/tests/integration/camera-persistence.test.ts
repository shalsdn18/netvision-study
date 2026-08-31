import { mkdtemp, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { afterEach, describe, expect, it } from 'vitest';
import { createTestApp, type TestApp } from '../helpers/test-app.js';

describe('camera persistence', () => {
  let fixture: TestApp | undefined;
  let directory: string | undefined;

  afterEach(async () => {
    await fixture?.close();
    if (directory) await rm(directory, { recursive: true, force: true });
  });

  it('preserves camera data after the application is restarted', async () => {
    directory = await mkdtemp(join(tmpdir(), 'ip-camera-persistence-'));
    const databasePath = join(directory, 'cameras.db');
    fixture = await createTestApp(databasePath);
    const camera = { cameraId: 'persistent', cameraName: 'Persistent', ipAddress: '172.16.0.5' };
    await fixture.app.inject({ method: 'POST', url: '/cameras', payload: camera });
    await fixture.app.close();

    fixture = await createTestApp(databasePath);
    const response = await fixture.app.inject({ method: 'GET', url: '/cameras/persistent' });
    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual(camera);
  });
});
