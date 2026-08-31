import Database from 'better-sqlite3';

export type SqliteDatabase = Database.Database;

export function openDatabase(databasePath: string): SqliteDatabase {
  const database = new Database(databasePath);
  database.pragma('journal_mode = WAL');
  database.pragma('foreign_keys = ON');
  database.exec(`
    CREATE TABLE IF NOT EXISTS cameras (
      camera_id TEXT PRIMARY KEY,
      camera_name TEXT NOT NULL CHECK (length(camera_name) > 0),
      ip_address TEXT NOT NULL
    )
  `);
  return database;
}

export function inTransaction<T>(database: SqliteDatabase, operation: () => T): T {
  return database.transaction(operation)();
}
