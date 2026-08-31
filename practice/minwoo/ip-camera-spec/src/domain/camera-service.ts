import type { Camera, CameraUpdate } from './camera.js';
import { ApplicationError, errorCodes } from '../api/errors.js';
import type { CameraRepository } from '../storage/camera-repository.js';

export class CameraService {
  constructor(private readonly repository: CameraRepository) {}

  create(camera: Camera): Camera {
    try {
      return this.repository.create(camera);
    } catch (error) {
      if (error instanceof Error && error.message.includes('UNIQUE constraint failed')) {
        throw new ApplicationError(
          409,
          errorCodes.duplicateCamera,
          `Camera '${camera.cameraId}' already exists`,
        );
      }
      throw error;
    }
  }

  list(): Camera[] {
    return this.repository.list();
  }

  get(cameraId: string): Camera {
    const camera = this.repository.findById(cameraId);
    if (!camera) {
      throw new ApplicationError(
        404,
        errorCodes.cameraNotFound,
        `Camera '${cameraId}' was not found`,
      );
    }
    return camera;
  }

  update(cameraId: string, update: CameraUpdate): Camera {
    const camera = this.repository.update(cameraId, update);
    if (!camera) {
      throw new ApplicationError(
        404,
        errorCodes.cameraNotFound,
        `Camera '${cameraId}' was not found`,
      );
    }
    return camera;
  }

  delete(cameraId: string): void {
    if (!this.repository.delete(cameraId)) {
      throw new ApplicationError(
        404,
        errorCodes.cameraNotFound,
        `Camera '${cameraId}' was not found`,
      );
    }
  }
}
