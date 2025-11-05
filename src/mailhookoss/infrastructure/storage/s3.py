"""S3 storage service for file storage (attachments, raw emails)."""

import hashlib
from datetime import datetime, timedelta

import aioboto3
from botocore.exceptions import ClientError

from mailhookoss.config import Settings


class S3StorageService:
    """Service for storing and retrieving files from S3-compatible storage."""

    def __init__(self, settings: Settings) -> None:
        """Initialize S3 storage service.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.bucket = settings.s3_bucket
        self.session = aioboto3.Session(
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
        )

    def _get_client(self):
        """Get S3 client with proper endpoint configuration."""
        client_kwargs = {
            "service_name": "s3",
            "region_name": self.settings.s3_region,
        }
        if self.settings.s3_endpoint:
            client_kwargs["endpoint_url"] = self.settings.s3_endpoint

        return self.session.client(**client_kwargs)

    def _build_key(
        self,
        tenant_id: str,
        mailbox_id: str,
        object_type: str,
        object_id: str,
        filename: str | None = None,
    ) -> str:
        """Build S3 object key.

        Format: {tenant_id}/{mailbox_id}/{object_type}/{object_id}/{filename}

        Args:
            tenant_id: Tenant ID
            mailbox_id: Mailbox ID
            object_type: Type of object (emails, attachments)
            object_id: Object ID
            filename: Optional filename

        Returns:
            S3 object key
        """
        if filename:
            return f"{tenant_id}/{mailbox_id}/{object_type}/{object_id}/{filename}"
        return f"{tenant_id}/{mailbox_id}/{object_type}/{object_id}"

    async def upload_attachment(
        self,
        tenant_id: str,
        mailbox_id: str,
        attachment_id: str,
        filename: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload an email attachment to S3.

        Args:
            tenant_id: Tenant ID
            mailbox_id: Mailbox ID
            attachment_id: Attachment ID
            filename: Filename
            content: File content bytes
            content_type: MIME content type

        Returns:
            S3 object key

        Raises:
            Exception: If upload fails
        """
        key = self._build_key(tenant_id, mailbox_id, "attachments", attachment_id, filename)

        async with self._get_client() as s3_client:
            await s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=content,
                ContentType=content_type,
                Metadata={
                    "tenant_id": tenant_id,
                    "mailbox_id": mailbox_id,
                    "attachment_id": attachment_id,
                    "original_filename": filename,
                },
            )

        return key

    async def download_attachment(
        self,
        tenant_id: str,
        mailbox_id: str,
        attachment_id: str,
        filename: str,
    ) -> bytes:
        """Download an email attachment from S3.

        Args:
            tenant_id: Tenant ID
            mailbox_id: Mailbox ID
            attachment_id: Attachment ID
            filename: Filename

        Returns:
            File content bytes

        Raises:
            FileNotFoundError: If attachment not found
            Exception: If download fails
        """
        key = self._build_key(tenant_id, mailbox_id, "attachments", attachment_id, filename)

        try:
            async with self._get_client() as s3_client:
                response = await s3_client.get_object(Bucket=self.bucket, Key=key)
                content = await response["Body"].read()
                return content
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise FileNotFoundError(f"Attachment not found: {key}") from e
            raise

    async def delete_attachment(
        self,
        tenant_id: str,
        mailbox_id: str,
        attachment_id: str,
        filename: str,
    ) -> None:
        """Delete an email attachment from S3.

        Args:
            tenant_id: Tenant ID
            mailbox_id: Mailbox ID
            attachment_id: Attachment ID
            filename: Filename

        Raises:
            Exception: If deletion fails
        """
        key = self._build_key(tenant_id, mailbox_id, "attachments", attachment_id, filename)

        async with self._get_client() as s3_client:
            await s3_client.delete_object(Bucket=self.bucket, Key=key)

    async def upload_raw_email(
        self,
        tenant_id: str,
        mailbox_id: str,
        email_id: str,
        raw_email: bytes,
    ) -> str:
        """Upload raw email (.eml file) to S3.

        Args:
            tenant_id: Tenant ID
            mailbox_id: Mailbox ID
            email_id: Email ID
            raw_email: Raw email bytes

        Returns:
            S3 object key

        Raises:
            Exception: If upload fails
        """
        key = self._build_key(tenant_id, mailbox_id, "emails", email_id, "raw.eml")

        # Calculate MD5 hash for integrity checking
        md5_hash = hashlib.md5(raw_email).hexdigest()

        async with self._get_client() as s3_client:
            await s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=raw_email,
                ContentType="message/rfc822",
                Metadata={
                    "tenant_id": tenant_id,
                    "mailbox_id": mailbox_id,
                    "email_id": email_id,
                    "md5": md5_hash,
                },
            )

        return key

    async def download_raw_email(
        self,
        tenant_id: str,
        mailbox_id: str,
        email_id: str,
    ) -> bytes:
        """Download raw email (.eml file) from S3.

        Args:
            tenant_id: Tenant ID
            mailbox_id: Mailbox ID
            email_id: Email ID

        Returns:
            Raw email bytes

        Raises:
            FileNotFoundError: If email not found
            Exception: If download fails
        """
        key = self._build_key(tenant_id, mailbox_id, "emails", email_id, "raw.eml")

        try:
            async with self._get_client() as s3_client:
                response = await s3_client.get_object(Bucket=self.bucket, Key=key)
                content = await response["Body"].read()
                return content
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise FileNotFoundError(f"Raw email not found: {key}") from e
            raise

    async def delete_raw_email(
        self,
        tenant_id: str,
        mailbox_id: str,
        email_id: str,
    ) -> None:
        """Delete raw email from S3.

        Args:
            tenant_id: Tenant ID
            mailbox_id: Mailbox ID
            email_id: Email ID

        Raises:
            Exception: If deletion fails
        """
        key = self._build_key(tenant_id, mailbox_id, "emails", email_id, "raw.eml")

        async with self._get_client() as s3_client:
            await s3_client.delete_object(Bucket=self.bucket, Key=key)

    async def generate_signed_url(
        self,
        tenant_id: str,
        mailbox_id: str,
        attachment_id: str,
        filename: str,
        expiration: int | None = None,
    ) -> str:
        """Generate a pre-signed URL for attachment download.

        Args:
            tenant_id: Tenant ID
            mailbox_id: Mailbox ID
            attachment_id: Attachment ID
            filename: Filename
            expiration: URL expiration in seconds (default from settings)

        Returns:
            Pre-signed URL

        Raises:
            Exception: If URL generation fails
        """
        key = self._build_key(tenant_id, mailbox_id, "attachments", attachment_id, filename)
        expiration = expiration or self.settings.signed_url_expiration

        async with self._get_client() as s3_client:
            url = await s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expiration,
            )
            return url

    async def check_attachment_exists(
        self,
        tenant_id: str,
        mailbox_id: str,
        attachment_id: str,
        filename: str,
    ) -> bool:
        """Check if an attachment exists in S3.

        Args:
            tenant_id: Tenant ID
            mailbox_id: Mailbox ID
            attachment_id: Attachment ID
            filename: Filename

        Returns:
            True if attachment exists
        """
        key = self._build_key(tenant_id, mailbox_id, "attachments", attachment_id, filename)

        try:
            async with self._get_client() as s3_client:
                await s3_client.head_object(Bucket=self.bucket, Key=key)
                return True
        except ClientError:
            return False

    async def list_mailbox_attachments(
        self,
        tenant_id: str,
        mailbox_id: str,
        limit: int = 100,
    ) -> list[str]:
        """List all attachments for a mailbox.

        Args:
            tenant_id: Tenant ID
            mailbox_id: Mailbox ID
            limit: Maximum number of attachments to list

        Returns:
            List of S3 object keys
        """
        prefix = f"{tenant_id}/{mailbox_id}/attachments/"

        async with self._get_client() as s3_client:
            response = await s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix,
                MaxKeys=limit,
            )

            if "Contents" not in response:
                return []

            return [obj["Key"] for obj in response["Contents"]]

    async def delete_all_mailbox_data(
        self,
        tenant_id: str,
        mailbox_id: str,
    ) -> int:
        """Delete all data for a mailbox (emails and attachments).

        Args:
            tenant_id: Tenant ID
            mailbox_id: Mailbox ID

        Returns:
            Number of objects deleted

        Raises:
            Exception: If deletion fails
        """
        prefix = f"{tenant_id}/{mailbox_id}/"
        deleted_count = 0

        async with self._get_client() as s3_client:
            # List all objects with prefix
            paginator = s3_client.get_paginator("list_objects_v2")
            async for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
                if "Contents" not in page:
                    continue

                # Delete in batches
                objects = [{"Key": obj["Key"]} for obj in page["Contents"]]
                if objects:
                    await s3_client.delete_objects(
                        Bucket=self.bucket,
                        Delete={"Objects": objects},
                    )
                    deleted_count += len(objects)

        return deleted_count

    async def get_storage_stats(
        self,
        tenant_id: str,
        mailbox_id: str,
    ) -> dict:
        """Get storage statistics for a mailbox.

        Args:
            tenant_id: Tenant ID
            mailbox_id: Mailbox ID

        Returns:
            Dictionary with storage stats (total_size, object_count)
        """
        prefix = f"{tenant_id}/{mailbox_id}/"
        total_size = 0
        object_count = 0

        async with self._get_client() as s3_client:
            paginator = s3_client.get_paginator("list_objects_v2")
            async for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
                if "Contents" not in page:
                    continue

                for obj in page["Contents"]:
                    total_size += obj["Size"]
                    object_count += 1

        return {
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "object_count": object_count,
        }
