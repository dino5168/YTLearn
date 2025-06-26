import sqlite3
from typing import Optional, Dict, Any


class VideoManager:
    def __init__(self, db_path: str = "c:/ytdb/database/videos.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS videos (
                id TEXT PRIMARY KEY,
                title TEXT,
                uploader TEXT,
                upload_date TEXT,
                view_count INTEGER,
                video_url TEXT,
                thumbnail_url TEXT,
                local_thumbnail_path TEXT,
                format TEXT,
                duration INTEGER
            )
        """
        )
        self.conn.commit()

    def add_or_update_video(self, video_data: Dict[str, Any]):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO videos (
                id, title, uploader, upload_date, view_count,
                video_url, thumbnail_url, local_thumbnail_path,
                format, duration
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                video_data["id"],
                video_data["title"],
                video_data["uploader"],
                video_data["upload_date"],
                video_data["view_count"],
                video_data["video_url"],
                video_data["thumbnail_url"],
                video_data["local_thumbnail_path"],
                video_data["format"],
                video_data["duration"],
            ),
        )
        self.conn.commit()

    def get_video(self, video_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
        row = cursor.fetchone()
        if row:
            keys = [
                "id",
                "title",
                "uploader",
                "upload_date",
                "view_count",
                "video_url",
                "thumbnail_url",
                "local_thumbnail_path",
                "format",
                "duration",
            ]
            return dict(zip(keys, row))
        return None

    def video_exists(self, video_id: str) -> bool:
        return self.get_video(video_id) is not None

    def delete_video(self, video_id: str):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM videos WHERE id = ?", (video_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()
