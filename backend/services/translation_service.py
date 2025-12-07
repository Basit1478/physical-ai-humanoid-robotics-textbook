from sqlalchemy.orm import Session
from typing import Optional
import asyncio
import json

from models.database import Translation, Chapter
from models.schemas import TranslationRequest, TranslationResponse


class TranslationService:
    def __init__(self):
        # In a real implementation, you would initialize a translation model or API client
        # For now, we'll simulate translation with basic mapping
        self.translation_cache = {}

    def get_cached_translation(self, content: str, target_lang: str) -> Optional[str]:
        """Check if translation is already cached"""
        cache_key = f"{content[:50]}-{target_lang}"  # Use first 50 chars as key
        return self.translation_cache.get(cache_key)

    def cache_translation(self, content: str, target_lang: str, translation: str):
        """Cache a translation"""
        cache_key = f"{content[:50]}-{target_lang}"
        self.translation_cache[cache_key] = translation

    def translate_text(self, text: str, target_lang: str = "ur", source_lang: str = "en") -> str:
        """Translate text to target language (simulated)"""
        # Check cache first
        cached = self.get_cached_translation(text, target_lang)
        if cached:
            return cached

        # In a real implementation, you would call a translation API like:
        # - Google Translate API
        # - Microsoft Translator API
        # - Hugging Face translation models
        # - OpenAI translation capabilities

        # For simulation purposes, return a placeholder translation
        # In a real implementation, you would have actual translation logic
        if target_lang == "ur":  # Urdu
            # This is a very basic simulation - in reality, you would use a proper translation API
            # Some common English to Urdu mappings for demonstration
            urdu_placeholders = {
                "robot": "روبوٹ",
                "ai": "مصنوعی ذہانت",
                "textbook": "کتاب",
                "chapter": "باب",
                "module": "ماڈیول",
                "artificial intelligence": "مصنوعی ذہانت",
                "robotics": "روبوٹکس",
                "embodied intelligence": "جسمانی ذہانت",
                "physical ai": "جسمانی مصنوعی ذہانت",
                "humanoid": "انسان نما",
                "nvidia": "این ویڈیا",
                "isaac": "آئزک",
                "ros": "آر او ایس",
                "gazebo": "گزیبو",
                "unity": "یونیٹی",
                "simulation": "شبیہ سازی",
                "vision": "دید",
                "language": "زبان",
                "action": "عمل",
                "learning": "سیکھنا",
                "perception": "ادراک",
                "planning": "منصوبہ بندی",
                "control": "کنٹرول",
                "navigation": "راہ نمائی",
                "manipulation": "ہاتھ سے کام لینا"
            }

            translated_text = text.lower()
            for eng, urdu in urdu_placeholders.items():
                translated_text = translated_text.replace(eng, urdu)

            # If no specific translations matched, return a placeholder indicating it's translated
            if translated_text == text.lower():
                translated_text = f"[URDU TRANSLATION] {text} [TRANSLATION_END]"

        else:
            # For other languages, return a placeholder
            translated_text = f"[TRANSLATED TO {target_lang.upper()}] {text} [TRANSLATION_END]"

        # Cache the translation
        self.cache_translation(text, target_lang, translated_text)
        return translated_text

    def translate_chapter(self, db: Session, chapter_id: int, target_lang: str = "ur") -> str:
        """Translate an entire chapter"""
        # Get the chapter content
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            raise ValueError(f"Chapter with id {chapter_id} not found")

        # Check if translation already exists in database
        existing_translation = db.query(Translation).filter(
            Translation.content_id == chapter_id,
            Translation.content_type == "chapter",
            Translation.language == target_lang
        ).first()

        if existing_translation:
            return existing_translation.translated_content

        # Translate the chapter content
        translated_content = self.translate_text(chapter.content, target_lang)

        # Save translation to database
        translation_record = Translation(
            content_id=chapter_id,
            content_type="chapter",
            language=target_lang,
            translated_content=translated_content
        )
        db.add(translation_record)
        db.commit()

        return translated_content

    def translate_content(self, db: Session, content: str, content_type: str, content_id: int, target_lang: str = "ur") -> str:
        """Translate any content (chapter, module, etc.)"""
        # Check if translation already exists in database
        existing_translation = db.query(Translation).filter(
            Translation.content_id == content_id,
            Translation.content_type == content_type,
            Translation.language == target_lang
        ).first()

        if existing_translation:
            return existing_translation.translated_content

        # Translate the content
        translated_content = self.translate_text(content, target_lang)

        # Save translation to database
        translation_record = Translation(
            content_id=content_id,
            content_type=content_type,
            language=target_lang,
            translated_content=translated_content
        )
        db.add(translation_record)
        db.commit()

        return translated_content

    def get_existing_translation(self, db: Session, content_id: int, content_type: str, target_lang: str) -> Optional[str]:
        """Get existing translation from database"""
        translation = db.query(Translation).filter(
            Translation.content_id == content_id,
            Translation.content_type == content_type,
            Translation.language == target_lang
        ).first()

        if translation:
            return translation.translated_content

        return None

    def batch_translate(self, texts: list, target_lang: str = "ur") -> list:
        """Translate multiple texts at once"""
        return [self.translate_text(text, target_lang) for text in texts]


# Global instance of the translation service
translation_service = TranslationService()