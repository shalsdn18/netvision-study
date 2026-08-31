import type { Camera, CameraUpdate } from '../domain/camera.js';
import { inTransaction, type SqliteDatabase } from './database.js';

interface CameraRow {
  camera_id: string;
  camera_name: string;
  ip_address: string;
}

function toCamera(row: CameraRow): Camera {
  return {
    cameraId: row.camera_id,
    cameraName: row.camera_name,
    ipAddress: row.ip_address,
  };
}

export class CameraRepository {
  constructor(private readonly database: SqliteDatabase) {}

  create(camera: Camera): Camera {
    return inTransaction(this.database, () => {
      this.database
        .prepare('INSERT INTO cameras (camera_id, camera_name, ip_address) VALUES (?, ?, ?)')
        .run(camera.cameraId, camera.cameraName, camera.ipAddress);
      return camera;
    });
  }

  list(): Camera[] {
    const rows = this.database
      .prepare('SELECT camera_id, camera_name, ip_address FROM cameras ORDER BY camera_id')
      .all() as CameraRow[];
    return rows.map(toCamera);
  }

  findById(cameraId: string): Camera | undefined {
    const row = this.database
      .prepare('SELECT camera_id, camera_name, ip_address FROM cameras WHERE camera_id = ?')
      .get(cameraId) as CameraRow | undefined;
    return row ? toCamera(row) : undefined;
  }

  update(cameraId: string, update: CameraUpdate): Camera | undefined {
    return inTransaction(this.database, () => {
      const result = this.database
        .prepare('UPDATE cameras SET camera_name = ?, ip_address = ? WHERE camera_id = ?')
        .run(update.cameraName, update.ipAddress, cameraId);
      return result.changes === 0 ? undefined : this.findById(cameraId);
    });
  }

  delete(cameraId: string): boolean {
    return inTransaction(
      this.database,
      () =>
        this.database.prepare('DELETE FROM cameras WHERE camera_id = ?').run(cameraId).changes > 0,
    );
  }
}
