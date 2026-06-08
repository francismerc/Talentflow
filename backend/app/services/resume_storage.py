from supabase import AsyncClient

RESUME_BUCKET = "resumes"


class ResumeStorageService:
    def __init__(self, client: AsyncClient) -> None:
        self._bucket = client.storage.from_(RESUME_BUCKET)

    async def upload(
        self,
        *,
        storage_path: str,
        content: bytes,
        mime_type: str,
    ) -> None:
        await self._bucket.upload(
            storage_path,
            content,
            {
                "content-type": mime_type,
                "upsert": "false",
            },
        )

    async def remove(self, storage_path: str) -> None:
        await self._bucket.remove([storage_path])

    async def download(self, storage_path: str) -> bytes:
        return await self._bucket.download(storage_path)
