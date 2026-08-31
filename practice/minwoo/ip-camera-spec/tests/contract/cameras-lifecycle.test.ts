import { afterEach, describe, expect, it } from 'vitest';
import { createTestApp, type TestApp } from '../helpers/test-app.js';

describe('camera update and delete contract', () => {
  let fixture: TestApp | undefined;
  afterEach(async () => fixture?.close());

  it('updates camera name and address while keeping its ID', async () => {
    fixture = await createTestApp();
    await fixture.app.inject({
      method: 'POST',
      url: '/cameras',
      payload: { cameraId: 'warehouse', cameraName: 'Old', ipAddress: '10.1.1.1' },
    });
    const response = await fixture.app.inject({
      method: 'PUT',
      url: '/cameras/warehouse',
      payload: { cameraName: 'Warehouse', ipAddress: '10.1.1.2' },
    });
    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual({
      cameraId: 'warehouse',
      cameraName: 'Warehouse',
      ipAddress: '10.1.1.2',
    });
  });

  it('deletes only the selected camera', async () => {
    fixture = await createTestApp();
    for (const cameraId of ['one', 'two']) {
      await fixture.app.inject({
        method: 'POST',
        url: '/cameras',
        payload: {
          cameraId,
          cameraName: cameraId,
          ipAddress: `10.0.0.${cameraId === 'one' ? 1 : 2}`,
        },
      });
    }
    const deleted = await fixture.app.inject({ method: 'DELETE', url: '/cameras/one' });
    expect(deleted.statusCode).toBe(204);
    expect(deleted.body).toBe('');
    expect((await fixture.app.inject({ method: 'GET', url: '/cameras/one' })).statusCode).toBe(404);
    expect((await fixture.app.inject({ method: 'GET', url: '/cameras/two' })).statusCode).toBe(200);
  });

  it('returns the common not-found error for unknown cameras', async () => {
    fixture = await createTestApp();
    for (const request of [
      { method: 'GET', url: '/cameras/missing' },
      {
        method: 'PUT',
        url: '/cameras/missing',
        payload: { cameraName: 'X', ipAddress: '10.0.0.1' },
      },
      { method: 'DELETE', url: '/cameras/missing' },
    ] as const) {
      const response = await fixture.app.inject(request);
      expect(response.statusCode).toBe(404);
      expect(response.json()).toMatchObject({ code: 'CAMERA_NOT_FOUND' });
    }
  });
});
