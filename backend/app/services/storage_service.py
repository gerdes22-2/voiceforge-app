import os
import shutil
import uuid
import hashlib
from typing import Tuple, Optional
from app.core.config import settings
import aioboto3

class StorageService:
    def __init__(self):
        self.provider = settings.STORAGE_PROVIDER.lower()
        self.base_path = "/app/storage"
        if self.provider == "local":
            os.makedirs(self.base_path, exist_ok=True)
            
        if self.provider in ["s3", "r2"]:
            self.session = aioboto3.Session()
            self.s3_config = {
                "endpoint_url": settings.S3_ENDPOINT_URL,
                "aws_access_key_id": settings.S3_ACCESS_KEY_ID,
                "aws_secret_access_key": settings.S3_SECRET_ACCESS_KEY,
                "region_name": settings.S3_REGION_NAME
            }
            self.bucket_name = settings.S3_BUCKET_NAME

    async def save_file(self, file_obj, original_filename: str) -> Tuple[str, str, int, str]:
        """
        Saves a file, returning (storage_path, mime_type, size, sha256)
        """
        file_ext = os.path.splitext(original_filename)[1].lower()
        new_filename = f"{uuid.uuid4()}{file_ext}"
        
        mime_type = "application/octet-stream"
        if file_ext == ".mp3": mime_type = "audio/mpeg"
        elif file_ext == ".wav": mime_type = "audio/wav"
        elif file_ext == ".flac": mime_type = "audio/flac"
        elif file_ext in [".m4a", ".aac"]: mime_type = "audio/aac"
        
        sha256_hash = hashlib.sha256()
        size = 0
        
        # Read file into memory for hashing and upload (or save locally and upload)
        # For simplicity, we write to a temp file, then upload
        temp_file_path = f"/tmp/{new_filename}"
        with open(temp_file_path, "wb") as f_out:
            while chunk := await file_obj.read(1024 * 1024): # 1MB chunks
                size += len(chunk)
                sha256_hash.update(chunk)
                f_out.write(chunk)
        
        if self.provider == "local":
            file_path = os.path.join(self.base_path, new_filename)
            shutil.move(temp_file_path, file_path)
            return file_path, mime_type, size, sha256_hash.hexdigest()
            
        elif self.provider in ["s3", "r2"]:
            s3_key = f"uploads/{new_filename}"
            async with self.session.client("s3", **self.s3_config) as s3_client:
                with open(temp_file_path, "rb") as f_in:
                    await s3_client.upload_fileobj(f_in, self.bucket_name, s3_key, ExtraArgs={"ContentType": mime_type})
            
            os.remove(temp_file_path)
            storage_path = f"s3://{self.bucket_name}/{s3_key}"
            return storage_path, mime_type, size, sha256_hash.hexdigest()
            
        else:
            raise NotImplementedError(f"Storage provider {self.provider} not implemented")

storage_service = StorageService()
