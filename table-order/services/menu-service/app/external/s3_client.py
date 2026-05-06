"""S3 Presigned URL 발급"""

import uuid

import boto3

from app.core.config import settings


class S3Client:
    def __init__(self):
        self._client = boto3.client("s3", region_name=settings.s3_region)

    def generate_presigned_upload_url(
        self, menu_id: int, content_type: str
    ) -> tuple[str, str]:
        """
        Presigned URL 발급

        Returns:
            tuple[str, str]: (presigned_url, image_key)
        """
        extension = content_type.split("/")[1]
        image_key = f"menus/{menu_id}/{uuid.uuid4().hex}.{extension}"

        presigned_url = self._client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.s3_bucket_name,
                "Key": image_key,
                "ContentType": content_type,
            },
            ExpiresIn=settings.s3_presigned_url_expiry,
        )

        return presigned_url, image_key


s3_client = S3Client()
