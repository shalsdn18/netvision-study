import { afterEach, describe, expect, it } from 'vitest';
import { createTestApp, type TestApp } from '../helpers/test-app.js';

describe('camera create and read contract', () => {
  let fixture: TestApp | undefined;
  afterEach(async () => fixture?.close());

  it('creates, lists, and retrieves a camera', async () => {
    fixture = await createTestApp();
    const camera = { cameraId: 'lobby-1', cameraName: 'Lobby', ipAddress: '192.168.10.20' };

    const created = await fixture.app.inject({ method: 'POST', url: '/cameras', payload: camera });
    expect(created.statusCode).toBe(201);
    expect(created.json()).toEqual(camera);

    const listed = await fixture.app.inject({ method: 'GET', url: '/cameras' });
    expect(listed.statusCode).toBe(200);
    expect(listed.json()).toEqual([camera]);

    const retrieved = await fixture.app.inject({ method: 'GET', url: '/cameras/lobby-1' });
    expect(retrieved.statusCode).toBe(200);
    expect(retrieved.json()).toEqual(camera);
  });

  it('returns an empty camera list', async () => {
    fixture = await createTestApp();
    const response = await fixture.app.inject({ method: 'GET', url: '/cameras' });
    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual([]);
  });

  it('rejects duplicate IDs without changing the existing camera', async () => {
    fixture = await createTestApp();
    const first = { cameraId: 'gate', cameraName: 'Gate A', ipAddress: '10.0.0.1' };
    await fixture.app.inject({ method: 'POST', url: '/cameras', payload: first });
    const duplicate = await fixture.app.inject({
      method: 'POST',
      url: '/cameras',
      payload: { ...first, cameraName: 'Replacement' },
    });
    expect(duplicate.statusCode).toBe(409);
    expect(duplicate.json()).toMatchObject({ code: 'DUPLICATE_CAMERA_ID' });
    const stored = await fixture.app.inject({ method: 'GET', url: '/cameras/gate' });
    expect(stored.json()).toEqual(first);
  });
});
