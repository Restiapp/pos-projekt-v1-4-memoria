"""
Translation Service - AI Translation with Vertex AI
Module 0: Terméktörzs és Menü - Alfeladat 7.1

Ez a service kezeli a termékek többnyelvű fordítását a Google Cloud Vertex AI
Translation API használatával. Automatikusan lefordítja a termékneveket és
leírásokat különböző nyelvekre.
"""

import logging
from typing import Dict, Optional, List
from google.cloud import translate_v3 as translate
from google.api_core import exceptions as google_exceptions

from backend.service_menu.config import settings

logger = logging.getLogger(__name__)


class TranslationService:
    """
    Service osztály az AI-alapú termék fordításhoz.

    A Vertex AI Translation API-t használja a terméknevek és leírások
    automatikus fordítására. Támogatja a következő nyelveket:
    - Magyar (hu) - forrás nyelv
    - Angol (en)
    - Német (de)
    - Francia (fr)
    - Olasz (it)
    - Spanyol (es)
    """

    # Célnyelvek (target languages) - magyarul írt termékeket fordítjuk le
    TARGET_LANGUAGES = ['en', 'de', 'fr', 'it', 'es']
    SOURCE_LANGUAGE = 'hu'

    def __init__(self):
        """
        TranslationService inicializálása.

        Létrehozza a Translation API klienst és beállítja a projekt paramétereket
        a config.py-ból.
        """
        self.client = translate.TranslationServiceClient()
        self.project_id = settings.gcp_project_id
        self.location = settings.vertex_ai_location
        self.parent = f"projects/{self.project_id}/locations/{self.location}"

        logger.info(
            f"TranslationService initialized with project: {self.project_id}, "
            f"location: {self.location}"
        )

    def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None
    ) -> Optional[str]:
        """
        Egyetlen szöveg fordítása egy célnyelvre.

        Args:
            text: A fordítandó szöveg
            target_language: Célnyelv kódja (pl. 'en', 'de')
            source_language: Forrásnyelv kódja (alapértelmezett: 'hu')

        Returns:
            Optional[str]: A lefordított szöveg vagy None hiba esetén
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for translation")
            return None

        source_lang = source_language or self.SOURCE_LANGUAGE

        try:
            # Vertex AI Translation API hívás
            response = self.client.translate_text(
                request={
                    "parent": self.parent,
                    "contents": [text],
                    "mime_type": "text/plain",
                    "source_language_code": source_lang,
                    "target_language_code": target_language,
                }
            )

            if response.translations:
                translated_text = response.translations[0].translated_text
                logger.debug(
                    f"Translation successful: {source_lang} -> {target_language}"
                )
                return translated_text
            else:
                logger.warning(f"No translation returned for text: {text[:50]}...")
                return None

        except google_exceptions.GoogleAPIError as e:
            logger.error(
                f"Google API error during translation to {target_language}: {str(e)}"
            )
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error during translation to {target_language}: {str(e)}"
            )
            return None

    def translate_product_text(
        self,
        name: str,
        description: Optional[str] = None,
        target_languages: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, str]]:
        """
        Termék név és leírás fordítása több nyelvre.

        Ez a fő metódus, amit a ProductService használ. Lefordítja a termék
        nevét és leírását a megadott célnyelvekre, és visszaadja a fordításokat
        olyan formátumban, ami közvetlenül menthető a Product.translations
        JSONB mezőbe.

        Args:
            name: Termék neve (forrás nyelven, magyar)
            description: Termék leírása (opcionális, forrás nyelven)
            target_languages: Célnyelvek listája (alapértelmezett: összes támogatott)

        Returns:
            Dict[str, Dict[str, str]]: Fordítások nyelvek szerint strukturálva
            Formátum: {
                'en': {'name': 'Product Name', 'description': 'Product Description'},
                'de': {'name': 'Produktname', 'description': 'Produktbeschreibung'},
                ...
            }

        Example:
            >>> service = TranslationService()
            >>> translations = service.translate_product_text(
            ...     name="Kávé",
            ...     description="Frissen pörkölt arabica kávé"
            ... )
            >>> translations['en']['name']
            'Coffee'
        """
        target_langs = target_languages or self.TARGET_LANGUAGES
        translations = {}

        logger.info(
            f"Starting translation for product: '{name}' to languages: {target_langs}"
        )

        for lang in target_langs:
            lang_translations = {}

            # Név fordítása (kötelező)
            translated_name = self.translate_text(name, lang)
            if translated_name:
                lang_translations['name'] = translated_name
            else:
                # Ha a fordítás sikertelen, használjuk az eredeti nevet
                lang_translations['name'] = name
                logger.warning(
                    f"Failed to translate name to {lang}, using original: {name}"
                )

            # Leírás fordítása (opcionális)
            if description and description.strip():
                translated_desc = self.translate_text(description, lang)
                if translated_desc:
                    lang_translations['description'] = translated_desc
                else:
                    # Ha a fordítás sikertelen, használjuk az eredeti leírást
                    lang_translations['description'] = description
                    logger.warning(
                        f"Failed to translate description to {lang}, "
                        f"using original: {description[:50]}..."
                    )
            else:
                # Ha nincs leírás, üres stringet mentünk
                lang_translations['description'] = ""

            translations[lang] = lang_translations

        logger.info(
            f"Translation completed for '{name}'. "
            f"Successfully translated to {len(translations)} languages."
        )

        return translations

    def update_translations(
        self,
        existing_translations: Optional[Dict[str, Dict[str, str]]],
        name: str,
        description: Optional[str] = None,
        languages_to_update: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, str]]:
        """
        Meglévő fordítások frissítése.

        Ha egy termék frissül, ez a metódus lehetővé teszi, hogy csak
        a megadott nyelveket frissítsük, a többit megőrizve.

        Args:
            existing_translations: Jelenlegi fordítások (JSONB mező tartalma)
            name: Új termék név (forrás nyelven)
            description: Új termék leírás (opcionális)
            languages_to_update: Mely nyelveket frissítsük (alapértelmezett: összes)

        Returns:
            Dict[str, Dict[str, str]]: Frissített fordítások
        """
        # Ha nincs meglévő fordítás, új fordítást készítünk
        if not existing_translations:
            return self.translate_product_text(name, description, languages_to_update)

        # Másolat készítése a meglévő fordításokról
        updated_translations = existing_translations.copy()

        # Új fordítások generálása
        new_translations = self.translate_product_text(name, description, languages_to_update)

        # Frissítés a meglévő fordításokkal való összefésüléssel
        for lang, translation in new_translations.items():
            updated_translations[lang] = translation

        logger.info(
            f"Updated translations for '{name}'. "
            f"Languages updated: {list(new_translations.keys())}"
        )

        return updated_translations

    def get_supported_languages(self) -> List[str]:
        """
        Támogatott nyelvek listájának lekérdezése.

        Returns:
            List[str]: Támogatott nyelv kódok listája
        """
        return self.TARGET_LANGUAGES.copy()

    def is_language_supported(self, language_code: str) -> bool:
        """
        Ellenőrzi, hogy egy nyelv támogatott-e.

        Args:
            language_code: Nyelv kód (pl. 'en', 'de')

        Returns:
            bool: True ha támogatott, különben False
        """
        return language_code in self.TARGET_LANGUAGES
