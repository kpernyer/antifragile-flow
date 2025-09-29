# PDF/DOCX Ingestion Guide

This guide explains how to add PDF and DOCX document ingestion to your RAG (Retrieval-Augmented Generation) system through the admin web interface.

## Overview

The system now supports uploading and processing the following document types:

- **PDF files** (.pdf) - Text extraction using PyPDF2
- **DOCX files** (.docx, .doc) - Text extraction using python-docx
- **Text files** (.txt, .md) - Direct text processing

## Backend Changes

### 1. Dependencies Added

The following Python packages were added to `rag/requirements.txt`:

- `python-multipart==0.0.6` - For handling file uploads in FastAPI
- `PyPDF2==3.0.1` - For PDF text extraction
- `python-docx==1.1.0` - For DOCX text extraction

### 2. New Functions in RAG API

- `_extract_text_from_pdf()` - Extracts text from PDF files
- `_extract_text_from_docx()` - Extracts text from DOCX files
- `_extract_text_from_file()` - Main dispatcher function that determines file type and calls appropriate extractor

### 3. Enhanced Upload Endpoint

The `/ingest/upload` endpoint now:

- Automatically detects file type based on extension
- Extracts text using the appropriate method
- Stores the file type as metadata in Neo4j
- Returns detailed information about the processed file

## Frontend Changes

### 1. New UI Section

Added a new "Upload documents" section with:

- File input with accept filter for supported formats
- Optional title input field
- File preview showing selected file name and size
- Upload button that's disabled until a file is selected

### 2. Upload Functionality

- Automatic title generation from filename (without extension)
- FormData-based file upload to backend
- Success/error feedback with detailed information
- Automatic refresh of recent documents list after upload

## Usage Instructions

### For End Users

1. **Access the Admin Interface**
   - Navigate to the React admin web interface
   - Look for the "Upload documents (PDF, DOCX, TXT)" section

2. **Upload a Document**
   - Click "Choose File" and select your PDF, DOCX, or text file
   - Optionally modify the document title (auto-generated from filename)
   - Click "Upload Document"
   - Wait for confirmation message with processing details

3. **Verify Upload**
   - Check the "Recently ingested" section to see your uploaded document
   - The document type will be shown (pdf, docx, text)
   - You can now query the RAG system about content from your uploaded document

### For Developers

1. **Install Dependencies**

   ```bash
   cd rag/
   pip install -r requirements.txt
   ```

2. **Start the RAG Service**

   ```bash
   cd rag/
   uvicorn app.main:app --reload --port 8080
   ```

3. **Start the Admin Frontend**

   ```bash
   cd frontend/react_admin/
   npm run dev
   ```

4. **Test the Upload**
   - Upload a test PDF or DOCX file
   - Check the Neo4j database to verify the document chunks were stored
   - Query the system to test retrieval from the uploaded document

## API Endpoints

### POST /ingest/upload

Upload and process a document file.

**Parameters:**

- `file`: The uploaded file (PDF, DOCX, or text)
- `title`: Optional title for the document
- `tenantId`: Tenant identifier (defaults to "demo")

**Response:**

```json
{
  "ok": true,
  "sourceId": "uuid-string",
  "chunks": 5,
  "embeddingProvider": "openai",
  "dim": 1536,
  "fileType": "pdf",
  "filename": "document.pdf"
}
```

## Error Handling

The system handles various error scenarios:

- **Unsupported file types**: Returns 400 error with file type information
- **Empty files**: Returns 400 error
- **Corrupted files**: Returns 400 error with specific processing error
- **No text extracted**: Returns 400 error if no readable text found

## Technical Details

### Text Extraction Process

1. File type detection based on extension
2. Appropriate extractor function called
3. Text chunked into overlapping segments (800 chars with 120 char overlap)
4. Each chunk embedded using configured embedding model
5. Chunks stored in Neo4j with relationships to source document

### Metadata Storage

- Source document stored with type, title, creation date, and tags
- Individual chunks linked to source via `HAS_CHUNK` relationship
- File type stored as both source type and tag for filtering

### Performance Considerations

- Large PDF files may take time to process
- Embedding generation depends on chunk count and embedding provider
- Consider implementing progress indicators for large file uploads

## Troubleshooting

### Common Issues

1. **"Unsupported file type" error**: Ensure file has correct extension (.pdf, .docx, .txt)
2. **"No text could be extracted"**: File may be image-based PDF or corrupted
3. **Upload timeout**: Large files may need increased timeout settings
4. **CORS errors**: Ensure RAG service allows requests from admin frontend

### Debugging

- Check browser network tab for upload request details
- Review RAG service logs for processing errors
- Use the "Debug RAG" feature to verify document chunks are searchable
