"""
GCS Service - Google Cloud Storage Integration
Module 0: Terméktörzs és Menü

Ez a service kezeli a Google Cloud Storage-ben történő képfeltöltést
signed URL-ek segítségével. A frontend közvetlenül a GCS-be tölti fel a képeket.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional
from google.cloud import storage
from backend.service_menu.config import settings


class GCSService:
    """
    Service osztály a Google Cloud Storage műveletekhez.

    Támogatja:
    - Signed URL generálást képfeltöltéshez
    - Biztonságos fájl név generálást
    - Tartalom típus validálást
    """

    # Engedélyezett MIME típusok
    ALLOWED_CONTENT_TYPES = {
        'image/jpeg',
        'image/png',
        'image/webp',
        'image/gif'
    }

    # Maximális fájlméret (MB)
    MAX_FILE_SIZE_MB = 10

    # Signed URL érvényességi idő (percekben)
    SIGNED_URL_EXPIRATION_MINUTES = 15

    def __init__(self):
        """GCS kliens inicializálása."""
        self.storage_client = storage.Client(project=settings.gcp_project_id)
        self.bucket = self.storage_client.bucket(settings.gcs_bucket_name)

    def generate_signed_upload_url(
        self,
        file_name: str,
        content_type: str,
        product_id: Optional[int] = None
    ) -> dict:
        """
        Signed URL generálása közvetlen GCS feltöltéshez.

        Args:
            file_name: Eredeti fájlnév (sanitizálásra kerül)
            content_type: MIME típus (pl. 'image/jpeg')
            product_id: Opcionális termék azonosító a fájl rendezéséhez

        Returns:
            dict: Signed URL adatok
                - upload_url: A feltöltési URL
                - gcs_url: A végső GCS URL (amit az ImageAsset-ben tárolunk)
                - expires_at: Lejárati időpont
                - max_file_size_mb: Maximális fájlméret MB-ban

        Raises:
            ValueError: Ha a content_type nem engedélyezett
        """
        # Tartalom típus validálása
        if content_type not in self.ALLOWED_CONTENT_TYPES:
            raise ValueError(
                f"Invalid content type '{content_type}'. "
                f"Allowed types: {', '.join(self.ALLOWED_CONTENT_TYPES)}"
            )

        # Biztonságos fájlnév generálása UUID-vel
        file_extension = self._get_file_extension(file_name, content_type)
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        # GCS blob path összeállítása
        blob_path = self._build_blob_path(unique_filename, product_id)

        # GCS blob létrehozása
        blob = self.bucket.blob(blob_path)

        # Lejárati idő számítása
        expiration = timedelta(minutes=self.SIGNED_URL_EXPIRATION_MINUTES)
        expires_at = datetime.utcnow() + expiration

        # Signed URL generálása feltöltéshez (PUT metódussal)
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=expiration,
            method="PUT",
            content_type=content_type,
            # Opcionális: fájlméret limit beállítása
            # Az alábbi headers segít biztosítani, hogy a frontend a helyes content-type-pal töltsön fel
            # És ez később segít a validálásban
        )

        # GCS URL összeállítása (amit később az ImageAsset táblába mentünk)
        gcs_url = f"gs://{settings.gcs_bucket_name}/{blob_path}"

        return {
            "upload_url": signed_url,
            "gcs_url": gcs_url,
            "expires_at": expires_at,
            "max_file_size_mb": self.MAX_FILE_SIZE_MB
        }

    def _get_file_extension(self, file_name: str, content_type: str) -> str:
        """
        Fájl extension meghatározása a fájlnév vagy content_type alapján.

        Args:
            file_name: Eredeti fájlnév
            content_type: MIME típus

        Returns:
            str: Fájl extension (pl. '.jpg', '.png')
        """
        # Próbálkozás a fájlnévből
        if '.' in file_name:
            extension = file_name.rsplit('.', 1)[-1].lower()
            # Validálás
            valid_extensions = {'jpg', 'jpeg', 'png', 'webp', 'gif'}
            if extension in valid_extensions:
                return f".{extension}"

        # Fallback: content_type alapján
        content_type_map = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/webp': '.webp',
            'image/gif': '.gif'
        }

        return content_type_map.get(content_type, '.jpg')

    def _build_blob_path(self, filename: str, product_id: Optional[int] = None) -> str:
        """
        GCS blob path összeállítása szervezetten.

        Struktúra:
        - products/original/{filename} - ha nincs product_id
        - products/original/product-{id}/{filename} - ha van product_id

        Args:
            filename: Egyedi fájlnév (UUID-vel)
            product_id: Opcionális termék azonosító

        Returns:
            str: Teljes blob path a bucket-en belül
        """
        base_path = "products/original"

        if product_id is not None:
            return f"{base_path}/product-{product_id}/{filename}"

        return f"{base_path}/{filename}"

    def delete_blob(self, gcs_url: str) -> bool:
        """
        Blob törlése GCS-ből.

        Args:
            gcs_url: GCS URL formátum (gs://bucket/path/to/file.jpg)

        Returns:
            bool: True ha sikeres, False ha a blob nem létezik
        """
        try:
            # GCS URL parsing: gs://bucket/path -> path
            if not gcs_url.startswith('gs://'):
                raise ValueError(f"Invalid GCS URL format: {gcs_url}")

            # Eltávolítjuk a gs://{bucket_name}/ részt
            blob_path = gcs_url.replace(f"gs://{settings.gcs_bucket_name}/", "")

            blob = self.bucket.blob(blob_path)
            blob.delete()
            return True

        except Exception:
            # Ha a blob nem létezik vagy más hiba történik, False-t adunk vissza
            return False

    def blob_exists(self, gcs_url: str) -> bool:
        """
        Ellenőrzi, hogy létezik-e a blob a GCS-ben.

        Args:
            gcs_url: GCS URL formátum (gs://bucket/path/to/file.jpg)

        Returns:
            bool: True ha létezik, különben False
        """
        try:
            if not gcs_url.startswith('gs://'):
                return False

            blob_path = gcs_url.replace(f"gs://{settings.gcs_bucket_name}/", "")
            blob = self.bucket.blob(blob_path)
            return blob.exists()

        except Exception:
            return False

    def get_public_url(self, gcs_url: str) -> str:
        """
        Publikus HTTPS URL generálása GCS blob-hoz.

        Args:
            gcs_url: GCS URL formátum (gs://bucket/path/to/file.jpg)

        Returns:
            str: Publikus HTTPS URL
        """
        if not gcs_url.startswith('gs://'):
            raise ValueError(f"Invalid GCS URL format: {gcs_url}")

        blob_path = gcs_url.replace(f"gs://{settings.gcs_bucket_name}/", "")
        return f"https://storage.googleapis.com/{settings.gcs_bucket_name}/{blob_path}"
