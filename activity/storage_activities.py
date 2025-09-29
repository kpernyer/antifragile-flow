"""
Storage activities with single responsibility for MinIO operations.
Maintains separation of concerns - only handles storage, not analysis.
"""

from datetime import datetime
from io import BytesIO
import logging
import os
from pathlib import Path
import tempfile
from typing import Any

from minio import Minio
from minio.error import S3Error
from temporalio import activity

logger = logging.getLogger(__name__)


class StorageActivities:
    """Storage activities focused solely on MinIO operations."""

    def __init__(self):
        # Initialize MinIO client
        self.minio_endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.minio_access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.minio_secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
        self.bucket_name = "documents"

        try:
            self.minio_client = Minio(
                self.minio_endpoint,
                access_key=self.minio_access_key,
                secret_key=self.minio_secret_key,
                secure=False,
            )
            # Ensure bucket exists
            if not self.minio_client.bucket_exists(self.bucket_name):
                self.minio_client.make_bucket(self.bucket_name)
                logger.info(f"Created MinIO bucket: {self.bucket_name}")

            logger.info(f"MinIO storage client initialized: {self.minio_endpoint}")
        except Exception as e:
            logger.warning(f"Failed to initialize MinIO client: {e}. Using temp files.")
            self.minio_client = None

    @activity.defn
    async def store_document_in_minio(
        self, document_data: bytes, filename: str, document_type: str
    ) -> dict[str, Any]:
        """
        Store document in MinIO with proper organization.
        Single responsibility: storage only, no analysis or processing.
        """
        logger.info(f"Storing document: {filename}")

        # Generate organized storage path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        storage_path = f"documents/{document_type}/{timestamp}_{filename}"
        document_size = len(document_data)

        if self.minio_client:
            try:
                # Store in MinIO
                data = BytesIO(document_data)
                result = self.minio_client.put_object(
                    bucket_name=self.bucket_name,
                    object_name=storage_path,
                    data=data,
                    length=document_size,
                    content_type=self._get_content_type(filename),
                )

                logger.info(f"✅ Document stored in MinIO: {storage_path} ({document_size} bytes)")

                return {
                    "storage_path": storage_path,
                    "bucket": self.bucket_name,
                    "size_bytes": document_size,
                    "etag": result.etag,
                    "stored_at": datetime.now().isoformat(),
                    "storage_type": "minio",
                    "file_path": f"minio://{self.bucket_name}/{storage_path}",  # For agent processing
                    "local_file_path": None,  # Will be set if we need local access
                }
            except S3Error as e:
                logger.error(f"MinIO storage error: {e}")
                raise
        else:
            # Fallback to temporary file storage for processing
            temp_dir = tempfile.mkdtemp()
            temp_file_path = Path(temp_dir) / filename

            with open(temp_file_path, "wb") as f:
                f.write(document_data)

            logger.info(f"✅ Document stored temporarily: {temp_file_path} ({document_size} bytes)")

            return {
                "storage_path": storage_path,
                "bucket": "temp",
                "size_bytes": document_size,
                "stored_at": datetime.now().isoformat(),
                "storage_type": "temp_file",
                "file_path": str(temp_file_path),  # Local path for agent processing
                "local_file_path": str(temp_file_path),
            }

    @activity.defn
    async def retrieve_document_from_minio(self, storage_path: str) -> bytes:
        """
        Retrieve document from MinIO.
        Single responsibility: retrieval only.
        """
        if self.minio_client:
            try:
                response = self.minio_client.get_object(self.bucket_name, storage_path)
                data = response.read()
                response.close()
                response.release_conn()

                logger.info(f"✅ Document retrieved from MinIO: {storage_path}")
                return data
            except S3Error as e:
                logger.error(f"MinIO retrieval error: {e}")
                raise
        else:
            raise RuntimeError("MinIO client not available for document retrieval")

    def _get_content_type(self, filename: str) -> str:
        """Determine content type based on file extension."""
        ext = Path(filename).suffix.lower()
        content_types = {
            ".pdf": "application/pdf",
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".csv": "text/csv",
        }
        return content_types.get(ext, "application/octet-stream")
