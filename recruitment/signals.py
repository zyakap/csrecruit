"""
Django signals for the recruitment app.
Automatically runs OCR when a new document is uploaded.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender='recruitment.Document')
def ocr_document_on_upload(sender, instance, created, **kwargs):
    """
    After a Document is created, run OCR on it in the background
    and update the parent application summary.
    Only runs for newly created documents that don't yet have OCR text.
    """
    if created and not instance.ocr_text:
        try:
            from recruitment.ocr_service import run_ocr_on_document, generate_application_summary
            run_ocr_on_document(instance)
            # Refresh application summary to include new document
            app = instance.application
            summary = generate_application_summary(app)
            app.ai_summary = summary
            app.save(update_fields=['ai_summary'])
        except Exception as e:
            logger.error(f"OCR signal failed for document #{instance.pk}: {e}")
