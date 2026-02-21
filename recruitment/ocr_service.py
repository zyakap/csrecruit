"""
OCR and Application Summary Service
Extracts text from uploaded documents and generates structured summaries for HR review.
"""
import os
import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


# ---------- Text Extraction ----------

def extract_text_from_pdf(file_path):
    """Extract text from a PDF. Tries digital text first, then OCR fallback."""
    text = ""

    # Attempt 1: Extract embedded text (fast, works for text-based PDFs)
    try:
        import PyPDF2
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            pages_text = []
            for page in reader.pages:
                page_text = page.extract_text() or ""
                pages_text.append(page_text)
            text = "\n".join(pages_text).strip()
    except Exception as e:
        logger.warning(f"PyPDF2 extraction failed for {file_path}: {e}")

    # Attempt 2: OCR fallback for scanned/image PDFs
    if len(text) < 50:
        try:
            from pdf2image import convert_from_path
            import pytesseract
            images = convert_from_path(file_path, dpi=200, first_page=1, last_page=10)
            ocr_parts = []
            for img in images:
                ocr_parts.append(pytesseract.image_to_string(img, lang='eng'))
            text = "\n".join(ocr_parts).strip()
        except Exception as e:
            logger.warning(f"PDF OCR fallback failed for {file_path}: {e}")

    return text


def extract_text_from_image(file_path):
    """Extract text from an image using Tesseract OCR."""
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img, lang='eng')
        return text.strip()
    except Exception as e:
        logger.warning(f"Image OCR failed for {file_path}: {e}")
        return ""


def extract_text_from_docx(file_path):
    """Extract text from a Word document."""
    try:
        from docx import Document
        doc = Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs).strip()
    except Exception as e:
        logger.warning(f"DOCX extraction failed for {file_path}: {e}")
        return ""


def extract_text_from_document(file_path):
    """
    Route a file to the appropriate extractor based on extension.
    Returns (extracted_text, method_used).
    """
    ext = Path(str(file_path)).suffix.lower()
    if ext == '.pdf':
        text = extract_text_from_pdf(str(file_path))
        return text, 'pdf'
    elif ext in ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif', '.webp'):
        text = extract_text_from_image(str(file_path))
        return text, 'image_ocr'
    elif ext in ('.docx', '.doc'):
        text = extract_text_from_docx(str(file_path))
        return text, 'docx'
    else:
        return "", 'unsupported'


# ---------- Text Analysis Helpers ----------

def _extract_keywords(text):
    """Extract potential qualification/skill keywords from OCR text."""
    text_lower = text.lower()
    found = []

    qualifications = [
        'bachelor', 'degree', 'diploma', 'certificate', 'master', 'phd',
        'grade 12', 'grade 10', 'form 6', 'form 4', 'postgraduate',
    ]
    for q in qualifications:
        if q in text_lower:
            found.append(q.title())

    skills = [
        'management', 'leadership', 'communication', 'teamwork', 'microsoft office',
        'excel', 'word', 'powerpoint', 'accounting', 'finance', 'law', 'legal',
        'nursing', 'health', 'engineering', 'it', 'information technology',
        'correctional', 'security', 'administration', 'procurement', 'audit',
    ]
    for s in skills:
        if s in text_lower:
            found.append(s.title())

    return list(set(found))


def _count_words(text):
    return len(text.split()) if text else 0


def _truncate(text, max_chars=500):
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(' ', 1)[0] + '…'


# ---------- Application Summary Generator ----------

def generate_application_summary(application):
    """
    Generate a rich text summary of an application for HR review.
    Combines form-filled data with OCR-extracted document text.
    Returns a formatted string ready for display.
    """
    lines = []
    sep = "─" * 60

    # --- Header ---
    lines.append(f"APPLICATION SUMMARY — #{application.pk}")
    lines.append(sep)

    # --- Personal Details ---
    lines.append("PERSONAL DETAILS")
    lines.append(f"  Name          : {application.full_name()}")
    lines.append(f"  Gender        : {application.gender}")
    age = application.get_age()
    lines.append(f"  Age           : {age} years")
    lines.append(f"  Province      : {application.province}")
    lines.append(f"  Nationality   : {application.nationality}")
    lines.append(f"  Contact       : {application.phone} | {application.email}")
    lines.append("")

    # --- Position Applied For ---
    lines.append("POSITION APPLIED FOR")
    lines.append(f"  Vacancy       : {application.vacancy.title}")
    lines.append(f"  Reference     : {application.vacancy.reference_number}")
    lines.append(f"  Department    : {application.vacancy.department}")
    lines.append(f"  Province      : {application.vacancy.province}")
    lines.append("")

    # --- Education ---
    lines.append("EDUCATION")
    lines.append(f"  Qualification : {application.get_highest_qualification_display()}")
    lines.append(f"  Institution   : {application.institution}")
    lines.append(f"  Year          : {application.year_completed}")
    lines.append(f"  Result/Grade  : {application.grade_result}")
    lines.append("")

    # --- Work Experience ---
    lines.append("WORK EXPERIENCE")
    lines.append(f"  Years         : {application.years_experience}")
    if application.current_employer:
        lines.append(f"  Current Employer: {application.current_employer}")
    if application.current_position:
        lines.append(f"  Current Position: {application.current_position}")
    if application.work_history.strip():
        lines.append(f"  History       : {_truncate(application.work_history, 300)}")
    lines.append("")

    # --- Cover Letter (excerpt) ---
    if application.cover_letter.strip():
        lines.append("COVER LETTER (EXCERPT)")
        lines.append(f"  {_truncate(application.cover_letter, 400)}")
        lines.append("")

    # --- References ---
    lines.append("REFERENCES")
    lines.append(f"  1. {application.reference1_name} — {application.reference1_position} ({application.reference1_phone})")
    if application.reference2_name:
        lines.append(f"  2. {application.reference2_name} — {application.reference2_position} ({application.reference2_phone})")
    lines.append("")

    # --- Documents + OCR Highlights ---
    documents = application.documents.all()
    if documents.exists():
        lines.append("UPLOADED DOCUMENTS & OCR ANALYSIS")
        for doc in documents:
            lines.append(f"  [{doc.get_doc_type_display()}] {doc.filename}")
            if doc.ocr_text:
                word_count = _count_words(doc.ocr_text)
                keywords = _extract_keywords(doc.ocr_text)
                lines.append(f"    → {word_count} words extracted via OCR")
                if keywords:
                    lines.append(f"    → Key terms found: {', '.join(keywords[:10])}")
                # Show first meaningful snippet
                snippet = _truncate(doc.ocr_text, 250)
                lines.append(f"    → Preview: {snippet}")
            else:
                lines.append(f"    → No OCR text extracted")
            lines.append("")

    # --- Auto Score ---
    lines.append("AUTOMATED SCREENING SCORE")
    if application.total_score is not None:
        score = application.total_score
        lines.append(f"  Total Score   : {score}/100")
        if score >= 80:
            rating = "EXCELLENT — Strongly recommended for interview"
        elif score >= 65:
            rating = "GOOD — Recommended for shortlisting"
        elif score >= 50:
            rating = "AVERAGE — Consider based on vacancy demand"
        else:
            rating = "BELOW AVERAGE — Review carefully before shortlisting"
        lines.append(f"  Rating        : {rating}")
    else:
        lines.append("  Score not yet computed — run auto-screening.")
    lines.append("")

    # --- HR Notes ---
    if application.hr_notes.strip():
        lines.append("HR NOTES")
        lines.append(f"  {application.hr_notes}")
        lines.append("")

    lines.append(sep)
    lines.append(f"Summary generated on {_today_str()}")

    return "\n".join(lines)


def _today_str():
    from django.utils import timezone
    return timezone.now().strftime("%d %B %Y, %H:%M")


# ---------- Batch OCR ----------

def run_ocr_on_document(document):
    """
    Run OCR on a Document model instance, save extracted text.
    Returns the extracted text string.
    """
    try:
        file_path = document.file.path
    except Exception:
        return ""

    if not os.path.exists(str(file_path)):
        logger.warning(f"Document file not found: {file_path}")
        return ""

    text, method = extract_text_from_document(file_path)
    document.ocr_text = text
    document.save(update_fields=['ocr_text'])
    logger.info(f"OCR complete for doc #{document.pk} via {method}: {_count_words(text)} words")
    return text


def run_ocr_on_application(application):
    """
    Run OCR on ALL documents for an application, then regenerate the full summary.
    Returns the updated summary string.
    """
    for doc in application.documents.all():
        if not doc.ocr_text:  # skip already-processed docs
            run_ocr_on_document(doc)

    # Re-generate full summary (includes document OCR content)
    summary = generate_application_summary(application)
    application.ai_summary = summary
    application.save(update_fields=['ai_summary'])
    return summary


def run_ocr_on_application_force(application):
    """
    Force re-run OCR on ALL documents for an application (even if already done).
    Then regenerate the full summary.
    """
    for doc in application.documents.all():
        run_ocr_on_document(doc)

    summary = generate_application_summary(application)
    application.ai_summary = summary
    application.save(update_fields=['ai_summary'])
    return summary
