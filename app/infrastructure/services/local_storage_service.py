import os

import aiofiles

from app.core.interfaces import StorageProvider


class LocalDiskStorage(StorageProvider):
    """Saves uploaded files directly to the local 'uploads' directory."""

    def __init__(self):
        self.upload_dir = "uploads"
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_file(self, filename: str, content: bytes) -> str:
        file_path = os.path.join(self.upload_dir, filename)

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        return file_path
