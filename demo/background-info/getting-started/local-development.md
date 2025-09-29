# 🚀 Local Development Guide

This guide explains how to set up and run the Living Twin monorepo locally with mock databases for development and testing.

## 🏗️ Architecture Overview

### **Data Storage Strategy**

#### **Neo4j** - Knowledge Graph & Vector Search

- **What**: Document chunks, embeddings, knowledge relationships
- **Why**: Built-in vector indexing for RAG + graph relationships
- **Local**: Docker container with demo data

#### **Firestore/Local Mock** - Organizations & Users

- **What**: Organization metadata, user accounts, tenant settings
- **Why**: Fast lookups, real-time updates, tenant isolation
- **Local Options**:
  - **Mock Database**: JSON files in `./local_data/` (no setup required)
  - **Firebase Emulator**: Full Firebase stack locally

## 🎯 Quick Start

### **Option 1: Mock Database (Recommended for Development)**

```bash
# Setup and run with local mock database
make dev-mock
```

This starts:

- 📊 **Neo4j**: <http://localhost:7474> (neo4j/password)
- 🌐 **API**: <http://localhost:8000>
- 💻 **Admin Web**: <http://localhost:5173>

### **Option 2: Full Firebase Emulator Stack**

```bash
# Setup and run with Firebase emulators
make dev-full
```

This starts everything above plus:

- 🔥 **Firebase UI**: <http://localhost:4000>
- 🔐 **Auth Emulator**: <http://localhost:9099>
- 📊 **Firestore Emulator**: <http://localhost:8080>
- 📁 **Storage Emulator**: <http://localhost:9199>

## 🏢 Demo Organizations & Users

### **Pre-loaded Organizations**

#### **Acme Corporation** (`aprio_org_acme`)

- **Domain**: `acme.com` (auto-binding enabled)
- **Users**:
  - `john@acme.com` - Employee (Engineering)
  - `admin@acme.com` - Admin (IT)
- **Features**: Chat, Pulse, Ingest, Analytics
- **Branding**: Corporate blue theme

#### **TechCorp Industries** (`aprio_org_techcorp`)

- **Domain**: `techcorp.io` (auto-binding enabled)
- **Users**:
  - `bob@techcorp.io` - Employee (Operations)
- **Features**: Chat, Pulse, Ingest
- **Branding**: Industrial orange theme

#### **Demo Organization** (`demo`)

- **Domain**: None (guest access)
- **Users**:
  - `demo@example.com` - Admin (Demo)
- **Features**: All features including Debug
- **Branding**: Purple demo theme

#### **BIG Corp Solutions** (`aprio_org_bigcorp`)

- **Domain**: `bigcorp.com` (auto-binding enabled)
- **Headquarters**: 1500 Technology Drive, San Jose, CA 95110
- **Employees**: 1,247 across multiple locations
- **Offices**: San Jose (HQ), Austin (Engineering), New York (Sales), Chicago (Regional)
- **Features**: Chat, Pulse, Ingest, Analytics, Reporting, Integrations
- **Branding**: Enterprise green theme

**Executive Leadership:**

- `sarah.chen@bigcorp.com` - CEO
- `marcus.johnson@bigcorp.com` - VP of Engineering
- `elena.rodriguez@bigcorp.com` - VP of Sales
- `david.kim@bigcorp.com` - VP of Marketing
- `fatima.al-zahra@bigcorp.com` - VP of Human Resources
- `james.oconnor@bigcorp.com` - VP of Operations

**Engineering Teams (40+ employees):**

- **Platform Engineering** (San Jose): `priya.patel@bigcorp.com` (Manager), `alex.petrov@bigcorp.com`, `maria.santos@bigcorp.com`, `yuki.tanaka@bigcorp.com`
- **Frontend Engineering** (San Jose): `ahmed.hassan@bigcorp.com` (Manager), `lisa.andersson@bigcorp.com`, `carlos.mendoza@bigcorp.com`
- **Backend Engineering** (San Jose): `raj.sharma@bigcorp.com` (Manager), `jennifer.wong@bigcorp.com`, `mikhail.volkov@bigcorp.com`
- **Austin Engineering** (Austin, TX): `robert.taylor@bigcorp.com` (Site Manager), `aisha.okafor@bigcorp.com`, `thomas.mueller@bigcorp.com`, `grace.liu@bigcorp.com`

**Sales Organization (15+ employees):**

- **Pre-Sales**: `michael.brown@bigcorp.com` (Director), `sofia.rossi@bigcorp.com`, `daniel.cohen@bigcorp.com`
- **Enterprise Sales**: `patricia.williams@bigcorp.com` (Director), `omar.ibrahim@bigcorp.com`, `anna.kowalski@bigcorp.com`
- **Key Account Management**: `kevin.nakamura@bigcorp.com` (Director), `rebecca.davis@bigcorp.com`
- **Regional Sales**: `stephanie.martin@bigcorp.com` (Midwest Manager), `hassan.ali@bigcorp.com`
- **Customer Success**: `linda.garcia@bigcorp.com` (Director), `benjamin.lee@bigcorp.com`, `nadia.popov@bigcorp.com`

**Support Functions:**

- **Marketing**: `jessica.thompson@bigcorp.com` (Director), `antonio.silva@bigcorp.com`, `rachel.goldberg@bigcorp.com`
- **Human Resources**: `michelle.jones@bigcorp.com` (Talent Director), `hiroshi.yamamoto@bigcorp.com`, `samantha.white@bigcorp.com`
- **Operations**: `christopher.anderson@bigcorp.com` (IT Director), `fatou.diallo@bigcorp.com`, `erik.larsson@bigcorp.com`

### **Demo Invitation Codes**

- `APRIO-ACME-INV123456789` - Join Acme Corporation as Employee
- `APRIO-TECHCORP-INVITE001` - Join TechCorp as Employee
- `APRIO-BIGCORP-ENG2024` - Join BIG Corp Engineering (100 uses)
- `APRIO-BIGCORP-SALES2024` - Join BIG Corp Sales (75 uses)
- `APRIO-BIGCORP-EXEC2024` - Join BIG Corp Executive (10 uses, admin access)

## 🔐 Authentication Flows

### **1. Email Domain Auto-Binding**

```bash
User signs in with john@acme.com
↓
System detects acme.com → Acme Corporation
↓
User automatically bound to organization
↓
Access to organization features & data
```

### **2. AprioOne Invitation Code**

```bash
User enters: APRIO-ACME-INV123456789
↓
System validates invitation code
↓
Creates account bound to Acme Corporation
↓
Assigns role/department from invitation
```

### **3. Guest Access**

```bash
User signs in as guest or personal email
↓
Access to basic demo features
↓
Can later join organization via invitation
```

## 🛠️ Development Commands

### **Quick Start**

```bash
make quick-start        # Complete setup and start all services
make dev-setup          # Setup dependencies and environment
```

### **Service Management**

```bash
make docker-up          # Start all Docker services
make docker-down        # Stop all Docker services
make docker-logs        # Show container logs
make docker-build       # Build all containers
```

### **Development Servers**

```bash
make api-dev            # Run API in development mode
make web-dev            # Run admin web interface
make mobile-dev         # Run Flutter mobile app
```

### **Database Management**

```bash
make seed-db            # Seed databases with demo data
make init-schema        # Initialize Neo4j schema and constraints
make validate-schema    # Validate Neo4j schema
make list-constraints   # List Neo4j constraints
make list-vector-indexes # List Neo4j vector indexes
```

### **Testing & Quality**

```bash
make test               # Run all tests
make test-unit          # Run unit tests only
make test-integration   # Run integration tests only
make lint               # Run code linters
make format             # Format code (black, isort)
```

### **Utilities**

```bash
make clean              # Clean up containers and build artifacts
make install-deps       # Install all dependencies
make status             # Check service status (production)
```

### **Cost Management**

```bash
make check-costs ENV=dev PROJECT=your-project
make cost-optimize-dev PROJECT=your-project
make scale-down-staging PROJECT=your-project
```

## 📁 Local Data Structure

When using mock database, data is stored in `./local_data/`:

```bash
local_data/
├── organizations.json   # Organization metadata
├── tenants.json        # Tenant settings (maps to orgs)
├── users.json          # User accounts by tenant
└── invitations.json    # Invitation codes
```

### **Example Organization Data**

```json
{
  "aprio_org_acme": {
    "id": "aprio_org_acme",
    "name": "Acme Corporation",
    "industry": "Technology",
    "emailDomains": ["acme.com"],
    "adminPortalUrl": "https://admin.acme.aprioone.com",
    "features": ["chat", "pulse", "ingest", "analytics"],
    "branding": {
      "primaryColor": "#1976D2",
      "theme": "corporate"
    }
  }
}
```

## ⚙️ Configuration

### **Environment Variables** (`.env`)

```bash
# Environment
ENVIRONMENT=development
USE_LOCAL_MOCK=true

# Neo4j (Docker)
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# OpenAI (Optional)
OPENAI_API_KEY=your-key-here

# Local alternatives
OLLAMA_BASE_URL=http://localhost:11434
SBERT_MODEL=all-MiniLM-L6-v2
```

### **Docker Compose Services**

- `neo4j` - Knowledge graph database
- `firebase-emulator` - Firebase services (optional)
- `api` - FastAPI backend
- `admin-web` - React admin interface

## 🧪 Testing Different Scenarios

### **Test Email Domain Binding**

1. Go to <http://localhost:5173>
2. Sign in with `john@acme.com` (any password)
3. Should automatically bind to Acme Corporation
4. See organization branding and context

### **Test Invitation Code Flow**

1. Go to <http://localhost:5173>
2. Click "Enter Invitation Code"
3. Enter `APRIO-ACME-INV123456789`
4. Should create account bound to Acme Corporation

### **Test Guest Access**

1. Sign in with any non-corporate email
2. Should get basic demo access
3. Can later use invitation code to join organization

### **Test Multi-Tenant Data Isolation**

1. Sign in as `john@acme.com`
2. Ingest some documents
3. Sign out and sign in as `bob@techcorp.io`
4. Should not see Acme's documents (tenant isolation)

### **Test API Endpoints**

```bash
# Health check
curl http://localhost:8000/healthz

# Ingest document
curl -X POST http://localhost:8000/ingest/text \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Doc","text":"Sample content","tenantId":"demo"}'

# Query knowledge
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the sample content?","tenantId":"demo"}'
```

### **Run Test Suite**

```bash
# Run all tests
make test

# Run specific test types
make test-unit          # Unit tests only
make test-integration   # Integration tests with database

# Run with coverage
cd apps/api && pytest tests/ -v --cov=app --cov-report=html
```

## 🔧 Customizing Mock Data

### **Add New Organization**

Edit `apps/api/app/adapters/local_mock_repo.py`:

```python
"your_org_id": {
    "id": "your_org_id",
    "name": "Your Company",
    "emailDomains": ["yourcompany.com"],
    "features": ["chat", "pulse", "ingest"],
    "branding": {"primaryColor": "#FF6B35"}
}
```

### **Add New Users**

```python
"your_org_id": {
    "user@yourcompany.com": {
        "email": "user@yourcompany.com",
        "roles": ["employee"],
        "department": "Engineering"
    }
}
```

### **Add Invitation Codes**

```python
"APRIO-YOURORG-INVITE123": {
    "organizationId": "your_org_id",
    "role": "employee",
    "department": "Engineering"
}
```

## 🚨 Troubleshooting

### **Port Conflicts**

If ports are in use, update `docker-compose.yml`:

```yaml
ports:
  - "7475:7474"  # Neo4j UI
  - "7688:7687"  # Neo4j Bolt
  - "8001:8000"  # API
  - "5174:5173"  # Admin Web
```

### **Data Reset**

```bash
make clean              # Remove all containers and data
rm -rf local_data       # Reset mock database
make dev-setup          # Recreate with fresh demo data
```

### **Container Issues**

```bash
docker compose down -v  # Stop and remove volumes
docker system prune -f  # Clean up Docker
make docker-up          # Restart services
```

### **Test Failures**

```bash
# Check test logs
make test-unit -v

# Run specific test file
cd apps/api && pytest tests/test_routes.py -v

# Check linting issues
make lint
```

### **Neo4j Schema Issues**

```bash
# Reinitialize schema
make init-schema NEO4J_URI=neo4j://localhost:7687 NEO4J_USER=neo4j NEO4J_PASSWORD=password

# Validate current schema
make validate-schema NEO4J_URI=neo4j://localhost:7687 NEO4J_USER=neo4j NEO4J_PASSWORD=password

# Check vector indexes
make list-vector-indexes NEO4J_URI=neo4j://localhost:7687 NEO4J_USER=neo4j NEO4J_PASSWORD=password
```

### **Performance Issues**

```bash
# Check resource usage
make check-costs ENV=dev PROJECT=your-project

# View service logs
make docker-logs

# Monitor API performance
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/healthz
```

## 🎯 Production vs Development

| Feature | Development (Mock) | Production |
|---------|-------------------|------------|
| **Organizations** | JSON files | Firestore |
| **Users** | JSON files | Firestore + Firebase Auth |
| **Knowledge Graph** | Local Neo4j | Cloud Neo4j |
| **Authentication** | Mock/bypass | Firebase Auth + JWT |
| **Data Isolation** | File-based | Firestore security rules |

## 📚 Next Steps

1. **Explore the API**: <http://localhost:8000/docs>
2. **Test Authentication**: Try different user flows
3. **Ingest Documents**: Upload PDFs/docs via admin interface
4. **Query Knowledge**: Ask questions about ingested content
5. **Run Tests**: `make test` to ensure everything works
6. **Customize Organizations**: Add your own demo data
7. **Deploy to Cloud**: Follow [Deployment Guide](DEPLOYMENT_SETUP.md)

## 🧪 Continuous Integration

The project includes GitHub Actions for:

- **Automated Testing**: Runs on every PR and push
- **Code Quality**: Linting, type checking, and formatting
- **Security Scanning**: Vulnerability detection with Trivy
- **Performance Testing**: Load tests with k6 on staging
- **Deployment**: Automated deployment to Google Cloud Run

### **Local CI Simulation**

```bash
# Run the same checks as CI
make lint               # Code quality checks
make test               # Full test suite
make format             # Code formatting

# Build Docker image (like CI)
make docker-build

# Run security scan (requires Docker image)
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image living_twin_monorepo_api:latest
```

The local development setup provides a complete, isolated environment for developing and testing the Living Twin platform without requiring external services or complex setup.
