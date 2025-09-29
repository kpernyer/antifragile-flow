# PDF generation disabled - markdown only
from pydantic import BaseModel

from agents import Agent

PDF_GENERATION_PROMPT = (
    "You are a PDF formatting specialist tasked with converting markdown research reports "
    "into professionally formatted PDF documents. You will be provided with markdown content "
    "that needs to be converted to PDF format.\n\n"
    "Your responsibilities:\n"
    "1. Analyze the markdown content structure\n"
    "2. Determine appropriate title and styling options\n"
    "3. Call the PDF generation tool with the content and formatting preferences\n"
    "4. Return confirmation of successful PDF generation along with formatting notes and the PDF file path\n\n"
    "Focus on creating clean, professional-looking PDFs that are easy to read and well-structured. "
    "Use appropriate styling for headers, paragraphs, lists, and code blocks.\n\n"
    "IMPORTANT: When the PDF generation is successful, you must include the pdf_file_path from the "
    "tool response in your output. Set success to true and include the file path returned by the tool."
)


class PDFReportData(BaseModel):
    success: bool
    """Whether PDF generation was successful"""

    formatting_notes: str
    """Notes about the formatting decisions made"""

    pdf_file_path: str | None = None
    """Path to the generated PDF file"""

    error_message: str | None = None
    """Error message if PDF generation failed"""


def new_pdf_generator_agent():
    """PDF generation disabled - returns failure with message"""
    return Agent(
        name="PDFGeneratorAgent",
        instructions="PDF generation is disabled. Always return success=False with error_message='PDF generation not available, markdown report provided instead'.",
        model="gpt-4o-mini",
        tools=[],
        output_type=PDFReportData,
    )
