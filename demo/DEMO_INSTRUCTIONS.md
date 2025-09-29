# Globex Industrial Group - Document Processing Demo

## Company Overview
**Globex Industrial Group** is a leading multinational manufacturer of advanced equipment and solutions for heavy industry and infrastructure.

- **Logo**: Stylized globe with bold corporate typography
- **Tagline**: "Innovating Tomorrow's Infrastructure"
- **Description**: A leading multinational manufacturer of advanced equipment and solutions for heavy industry and infrastructure

## Product Lines
1. **Power Systems** - Advanced power distribution systems
2. **Automation & Controls** - Industrial automation control systems
3. **Material Handling** - Conveyor systems, AS/RS, robotic handling
4. **Construction Equipment** - Heavy construction machinery

## Demo Documents Available
1. `power-systems-specification.pdf` - Technical specifications for GX-PDS-2024 power distribution system
2. `automation-controls-manual.pdf` - User manual for GX-ACS-2024 automation control system
3. `material-handling-systems.pdf` - Product catalog for material handling solutions
4. `construction-equipment-catalog.pdf` - Heavy construction equipment catalog

## Demo Flow
1. **Upload Documents**: Drag and drop the PDF files from the demo-documents folder
2. **Watch Processing**: Observe the real-time status updates and toast notifications
3. **View Results**: Check the processing statistics and workflow IDs
4. **Access MinIO**: Click the "View in console" link to see uploaded files
5. **Monitor Workflows**: Use the workflow IDs to track processing in Temporal Web UI

## Key Features to Highlight
- **Real-time Processing**: Documents are processed through Temporal workflows
- **Intelligent Extraction**: Text extraction, embedding generation, and knowledge graph creation
- **Visual Feedback**: Toast notifications, progress bars, and status indicators
- **Scalable Architecture**: Microservices with Temporal orchestration
- **Industrial Focus**: Designed for enterprise document processing needs

## Technical Architecture
- **Frontend**: React + TypeScript with Vite
- **API**: FastAPI with Python
- **Workflow Engine**: Temporal for orchestration
- **Storage**: MinIO (S3-compatible)
- **Databases**: Weaviate (vector), Neo4j (graph)
- **Infrastructure**: Docker Compose for local development

## URLs for Demo
- **Frontend**: http://localhost:3000
- **API**: http://localhost:7001
- **Temporal Web UI**: http://localhost:8233
- **MinIO Console**: http://localhost:9001
- **Weaviate**: http://localhost:8080
- **Neo4j**: http://localhost:7474

## Demo Script
1. Start with company introduction and product lines
2. Show the branded frontend interface
3. Upload a document and explain the processing pipeline
4. Demonstrate real-time feedback and notifications
5. Show the infrastructure components and their roles
6. Highlight the scalability and enterprise-ready features
