import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager


class Database:
    def __init__(self, db_path: str | None = None):
        if db_path is None:
            config_dir = Path.home() / ".audio_library_manager"
            config_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(config_dir / "library.db")
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        with self._conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS audio_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    file_name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    format TEXT NOT NULL,
                    duration REAL DEFAULT 0,
                    file_size INTEGER DEFAULT 0,
                    sample_rate INTEGER DEFAULT 0,
                    channels INTEGER DEFAULT 0,
                    bitrate INTEGER DEFAULT 0,
                    date_added TEXT NOT NULL,
                    date_modified TEXT,
                    notes TEXT DEFAULT '',
                    is_transcribed INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    color TEXT DEFAULT '#3498db'
                );

                CREATE TABLE IF NOT EXISTS audio_tags (
                    audio_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    PRIMARY KEY (audio_id, tag_id),
                    FOREIGN KEY (audio_id) REFERENCES audio_files(id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS transcriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    audio_id INTEGER NOT NULL UNIQUE,
                    full_text TEXT DEFAULT '',
                    language TEXT DEFAULT '',
                    model_used TEXT DEFAULT '',
                    date_transcribed TEXT,
                    FOREIGN KEY (audio_id) REFERENCES audio_files(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS transcription_segments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transcription_id INTEGER NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL NOT NULL,
                    text TEXT NOT NULL,
                    FOREIGN KEY (transcription_id) REFERENCES transcriptions(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_audio_title ON audio_files(title);
                CREATE INDEX IF NOT EXISTS idx_audio_format ON audio_files(format);
                CREATE INDEX IF NOT EXISTS idx_audio_path ON audio_files(file_path);
                CREATE INDEX IF NOT EXISTS idx_segments_trans ON transcription_segments(transcription_id);
            """)

    # --- Audio files ---

    def add_audio(self, metadata: dict) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                """INSERT OR IGNORE INTO audio_files
                   (file_path, file_name, title, format, duration, file_size,
                    sample_rate, channels, bitrate, date_added, date_modified)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    metadata["file_path"],
                    metadata["file_name"],
                    metadata["title"],
                    metadata["format"],
                    metadata.get("duration", 0),
                    metadata.get("file_size", 0),
                    metadata.get("sample_rate", 0),
                    metadata.get("channels", 0),
                    metadata.get("bitrate", 0),
                    metadata.get("date_added", datetime.now().isoformat()),
                    metadata.get("date_modified", ""),
                ),
            )
            if cur.lastrowid:
                return cur.lastrowid
            row = conn.execute(
                "SELECT id FROM audio_files WHERE file_path = ?",
                (metadata["file_path"],),
            ).fetchone()
            return row["id"] if row else 0

    def get_all_audio(self) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM audio_files ORDER BY date_added DESC"
            ).fetchall()
            return [dict(r) for r in rows]

    def get_audio(self, audio_id: int) -> dict | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM audio_files WHERE id = ?", (audio_id,)
            ).fetchone()
            return dict(row) if row else None

    def delete_audio(self, audio_id: int):
        with self._conn() as conn:
            conn.execute("DELETE FROM audio_files WHERE id = ?", (audio_id,))

    def update_audio(self, audio_id: int, **fields):
        if not fields:
            return
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [audio_id]
        with self._conn() as conn:
            conn.execute(
                f"UPDATE audio_files SET {set_clause} WHERE id = ?", values
            )

    def search_audio(self, query: str = "", tags: list[str] | None = None,
                     fmt: str = "", min_dur: float = 0, max_dur: float = 0) -> list[dict]:
        conditions = []
        params = []

        if query:
            conditions.append(
                "(a.title LIKE ? OR a.file_name LIKE ? OR "
                "EXISTS (SELECT 1 FROM transcriptions t WHERE t.audio_id = a.id AND t.full_text LIKE ?))"
            )
            like = f"%{query}%"
            params.extend([like, like, like])

        if fmt:
            conditions.append("a.format = ?")
            params.append(fmt)

        if min_dur > 0:
            conditions.append("a.duration >= ?")
            params.append(min_dur)

        if max_dur > 0:
            conditions.append("a.duration <= ?")
            params.append(max_dur)

        where = ""
        if conditions:
            where = "WHERE " + " AND ".join(conditions)

        sql = f"SELECT DISTINCT a.* FROM audio_files a {where} ORDER BY a.date_added DESC"

        with self._conn() as conn:
            rows = conn.execute(sql, params).fetchall()
            results = [dict(r) for r in rows]

        if tags:
            results = [r for r in results if self._audio_has_tags(r["id"], tags)]

        return results

    def _audio_has_tags(self, audio_id: int, tag_names: list[str]) -> bool:
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT t.name FROM tags t
                   JOIN audio_tags at ON t.id = at.tag_id
                   WHERE at.audio_id = ?""",
                (audio_id,),
            ).fetchall()
            existing = {r["name"].lower() for r in rows}
            return all(t.lower() in existing for t in tag_names)

    # --- Tags ---

    def add_tag(self, name: str, color: str = "#3498db") -> int:
        with self._conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO tags (name, color) VALUES (?, ?)",
                (name, color),
            )
            row = conn.execute(
                "SELECT id FROM tags WHERE name = ?", (name,)
            ).fetchone()
            return row["id"]

    def get_all_tags(self) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM tags ORDER BY name").fetchall()
            return [dict(r) for r in rows]

    def tag_audio(self, audio_id: int, tag_id: int):
        with self._conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO audio_tags (audio_id, tag_id) VALUES (?, ?)",
                (audio_id, tag_id),
            )

    def untag_audio(self, audio_id: int, tag_id: int):
        with self._conn() as conn:
            conn.execute(
                "DELETE FROM audio_tags WHERE audio_id = ? AND tag_id = ?",
                (audio_id, tag_id),
            )

    def get_audio_tags(self, audio_id: int) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT t.* FROM tags t
                   JOIN audio_tags at ON t.id = at.tag_id
                   WHERE at.audio_id = ?
                   ORDER BY t.name""",
                (audio_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def delete_tag(self, tag_id: int):
        with self._conn() as conn:
            conn.execute("DELETE FROM tags WHERE id = ?", (tag_id,))

    # --- Transcriptions ---

    def save_transcription(self, audio_id: int, full_text: str, language: str,
                           model_used: str, segments: list[dict]):
        with self._conn() as conn:
            conn.execute(
                "DELETE FROM transcriptions WHERE audio_id = ?", (audio_id,)
            )
            cur = conn.execute(
                """INSERT INTO transcriptions
                   (audio_id, full_text, language, model_used, date_transcribed)
                   VALUES (?, ?, ?, ?, ?)""",
                (audio_id, full_text, language, model_used,
                 datetime.now().isoformat()),
            )
            trans_id = cur.lastrowid
            for seg in segments:
                conn.execute(
                    """INSERT INTO transcription_segments
                       (transcription_id, start_time, end_time, text)
                       VALUES (?, ?, ?, ?)""",
                    (trans_id, seg["start"], seg["end"], seg["text"]),
                )
            conn.execute(
                "UPDATE audio_files SET is_transcribed = 1 WHERE id = ?",
                (audio_id,),
            )

    def get_transcription(self, audio_id: int) -> dict | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM transcriptions WHERE audio_id = ?", (audio_id,)
            ).fetchone()
            if not row:
                return None
            trans = dict(row)
            segs = conn.execute(
                """SELECT * FROM transcription_segments
                   WHERE transcription_id = ?
                   ORDER BY start_time""",
                (trans["id"],),
            ).fetchall()
            trans["segments"] = [dict(s) for s in segs]
            return trans

    # --- Export ---

    def export_library_json(self, path: str):
        data = {
            "audio_files": self.get_all_audio(),
            "tags": self.get_all_tags(),
            "exported_at": datetime.now().isoformat(),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def export_library_csv(self, path: str):
        import csv
        rows = self.get_all_audio()
        if not rows:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    def backup(self, backup_path: str):
        import shutil
        shutil.copy2(self.db_path, backup_path)
