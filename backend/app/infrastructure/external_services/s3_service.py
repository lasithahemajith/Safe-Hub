import boto3
import uuid
import os
from typing import Optional
from fastapi import UploadFile
from app.core.config import settings

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


class S3Service:
    def __init__(self):
        if settings.AWS_ACCESS_KEY_ID:
            self.s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
            )
        else:
            self.s3 = None
        self.bucket = settings.AWS_S3_BUCKET

    async def upload_image(self, file: UploadFile, folder: str = "incidents") -> Optional[str]:
        if not self.s3:
            return None

        # Validate file type
        if file.content_type not in ALLOWED_TYPES:
            raise ValueError(f"File type {file.content_type} not allowed")

        content = await file.read()

        # Validate file size
        if len(content) > MAX_FILE_SIZE:
            raise ValueError("File size exceeds 10MB limit")

        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
        key = f"{folder}/{uuid.uuid4()}.{ext}"

        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=content,
            ContentType=file.content_type,
            ACL="private",
        )

        url = f"https://{self.bucket}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
        return url

    def delete_image(self, url: str) -> bool:
        if not self.s3:
            return False
        try:
            key = url.split(f"{self.bucket}.s3.{settings.AWS_REGION}.amazonaws.com/")[1]
            self.s3.delete_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False


s3_service = S3Service()
