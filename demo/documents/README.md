# Demo Documents Catalog

This directory contains demo documents imported from the original hackathon project for the **Globex Industrial Group** demonstration scenario.

## Directory Structure

```
documents/
├── globex/                     # Globex company documents
│   ├── Globex_Annual_Report_2025.pdf
│   ├── Globex_Product_Brochure.pdf
│   ├── Globex_Profile.pdf
│   └── Globex_Sustainability_Report.pdf
├── technical/                  # Technical product documentation
│   ├── automation-controls-manual.pdf
│   ├── construction-equipment-catalog.pdf
│   ├── material-handling-systems.pdf
│   └── power-systems-specification.pdf
└── README.md                   # This file
```

## Globex Industrial Group - Company Documents

### Company Overview
**Globex Industrial Group** is a leading multinational manufacturer of advanced equipment and solutions for heavy industry and infrastructure.

- **Logo**: Stylized globe with bold corporate typography
- **Tagline**: "Innovating Tomorrow's Infrastructure"
- **Focus**: Heavy industry and infrastructure solutions

### Company Documents (globex/)
- **Globex_Profile.pdf** - Corporate profile and company overview
- **Globex_Product_Brochure.pdf** - Main product brochure and catalog
- **Globex_Annual_Report_2025.pdf** - Annual financial and operational report
- **Globex_Sustainability_Report.pdf** - Corporate sustainability initiatives

## Technical Product Documentation (technical/)

### Product Lines Covered
1. **Power Systems** - Advanced power distribution systems
2. **Automation & Controls** - Industrial automation control systems
3. **Material Handling** - Conveyor systems, AS/RS, robotic handling
4. **Construction Equipment** - Heavy construction machinery

### Technical Documents
- **power-systems-specification.pdf** - Technical specifications for GX-PDS-2024 power distribution system
- **automation-controls-manual.pdf** - User manual for GX-ACS-2024 automation control system
- **material-handling-systems.pdf** - Product catalog for material handling solutions
- **construction-equipment-catalog.pdf** - Heavy construction equipment catalog

## Usage in Demos

These documents are designed for demonstrating:
- **Document Processing Workflows** - Temporal-based document processing
- **LoRA Model Training** - Training organizational AI models with company-specific content
- **Knowledge Extraction** - Text extraction, embeddings, and knowledge graph creation
- **Enterprise AI** - Organization-specific AI customization and deployment

## Integration with Antifragile Flow

### Document Processing Workflow
Documents from this collection can be processed through the `DocumentProcessingWorkflow` which includes:
- Text extraction and analysis
- Embedding generation for vector search
- Knowledge graph creation
- Optional LoRA model training with organizational content

### Model Training Integration
These documents serve as training data for:
- **Organizational Values**: Sustainability, innovation, infrastructure focus
- **Domain Knowledge**: Industrial equipment, power systems, automation
- **Corporate Style**: Technical documentation, formal business communications
- **Use Cases**: Technical specifications, user manuals, corporate reports

The organized structure supports clean separation of corporate documents (globex/) from technical documentation (technical/), enabling targeted training scenarios and comprehensive organizational AI customization.
