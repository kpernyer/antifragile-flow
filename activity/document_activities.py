"""
Pure technical document processing activities for Temporal workflows.
Handles document upload, text extraction, and basic file operations.
AI-powered activities are in agent_activity/ai_activities.py
"""

from dataclasses import dataclass
from pathlib import Path

from temporalio import activity


@dataclass
class DocumentInfo:
    """Information about an uploaded document"""

    file_path: str
    file_name: str
    file_size: int
    file_type: str
    extracted_text: str
    page_count: int | None = None


@dataclass
class DocumentSummaryResult:
    """Result from document summarization"""

    document_info: DocumentInfo
    short_summary: str
    key_takeaways: list[str]
    main_topics: list[str]
    markdown_report: str
    confidence_score: float  # 0-1, how confident we are in the analysis


@dataclass
class DocumentSummaryWorkflowResult:
    """Result from document summary activity - for admin UI display"""

    document_name: str
    document_type: str
    summary_text: str
    key_points: list[str]
    topics: list[str]
    processing_time: str
    success: bool
    error_message: str | None = None


@dataclass
class SimpleResearchResult:
    """Result from simple research activity"""

    query: str
    context: str | None
    findings: str
    key_insights: list[str]
    sources: list[str]
    confidence_score: float  # 0-1
    research_timestamp: str
    success: bool
    error_message: str | None = None


@activity.defn
async def process_document_upload(file_path: str) -> DocumentInfo:
    """Process uploaded document and extract text"""
    try:
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        # Get basic file info
        file_stats = file_path_obj.stat()
        file_name = file_path_obj.name
        file_size = file_stats.st_size
        file_type = file_path_obj.suffix.lower()

        activity.logger.info(
            f"Processing document: {file_name} ({file_size} bytes, type: {file_type})"
        )

        # Extract text based on file type
        extracted_text = await _extract_text_from_file(file_path, file_type)

        # Count pages if possible (rough estimate based on text length)
        page_count = max(1, len(extracted_text) // 2000) if extracted_text else 1

        return DocumentInfo(
            file_path=file_path,
            file_name=file_name,
            file_size=file_size,
            file_type=file_type,
            extracted_text=extracted_text,
            page_count=page_count,
        )

    except Exception as e:
        activity.logger.error(f"Document processing failed: {e}")
        # Return basic info even if text extraction fails
        file_path_obj = Path(file_path)
        return DocumentInfo(
            file_path=file_path,
            file_name=file_path_obj.name if file_path_obj.exists() else "unknown",
            file_size=0,
            file_type="unknown",
            extracted_text=f"Failed to extract text from document: {e}",
            page_count=0,
        )


async def _extract_text_from_file(file_path: str, file_type: str) -> str:
    """Extract text from various file formats"""
    try:
        if file_type in [".txt", ".md", ".csv"]:
            # Plain text files
            with open(file_path, encoding="utf-8") as f:
                return f.read()

        elif file_type == ".pdf":
            # Try to extract from PDF
            try:
                import PyPDF2

                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            except ImportError:
                activity.logger.warning("PyPDF2 not available for PDF extraction")
                return f"PDF file: {Path(file_path).name} (text extraction requires PyPDF2)"

        elif file_type in [".docx", ".doc"]:
            # Try to extract from Word documents
            try:
                import docx

                doc = docx.Document(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            except ImportError:
                activity.logger.warning("python-docx not available for Word extraction")
                return (
                    f"Word document: {Path(file_path).name} (text extraction requires python-docx)"
                )

        elif file_type in [".xlsx", ".xls"]:
            # Try to extract from Excel
            try:
                import pandas as pd

                df = pd.read_excel(file_path)
                return df.to_string()
            except ImportError:
                activity.logger.warning("pandas not available for Excel extraction")
                return f"Excel file: {Path(file_path).name} (text extraction requires pandas)"

        else:
            # Unsupported file type - try reading as plain text
            try:
                with open(file_path, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if content.strip():
                        return content
                    else:
                        return f"Binary or empty file: {Path(file_path).name}"
            except Exception:
                return f"Unsupported file type: {file_type}"

    except Exception as e:
        activity.logger.error(f"Text extraction failed for {file_path}: {e}")
        return f"Text extraction failed: {e!s}"
