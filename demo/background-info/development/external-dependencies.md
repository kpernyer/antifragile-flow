# External Dependencies and Hardcoded Assumptions Analysis

## *Analysis of Living Twin monorepo - January 2025*

## Executive Summary

This document identifies all external URLs, email addresses, domain names, and other hardcoded assumptions throughout the Living Twin codebase that may need to be updated when deploying to different environments or organizations.

## Categories of External Dependencies

### 1. Development Environment URLs

#### Local Development Endpoints

- **Neo4j Browser**: `http://localhost:7474` (neo4j/password)
- **API Server**: `http://localhost:8000` or `http://localhost:8080`
- **Admin Web Interface**: `http://localhost:5173`
- **Firebase Emulator UI**: `http://localhost:4000`
- **Auth Emulator**: `http://localhost:9099`
- **Firestore Emulator**: `http://localhost:8080`
- **Storage Emulator**: `http://localhost:9199`
- **Ollama Server**: `http://localhost:11434`
- **Neo4j Database**: `neo4j://localhost:7687`

#### Configuration Files Affected

- `.env` and `.env.example`
- `.env.local`
- `docker-compose.yml`
- `apps/admin_web/.env.example`
- `apps/api/app/config.py`
- `apps/mobile/lib/config/app_config.dart`

### 2. Production/Staging URLs

#### Mobile App API Endpoints

- **Development**: `http://localhost:8000`
- **Staging**: `https://api-staging.livingtwin.com`
- **Production**: `https://api.livingtwin.com`

#### Load Testing and Deployment

- **Staging Environment**: `https://living-twin-api-staging-abc123.a.run.app`
- **Cloud Run Health Check**: `https://your-service-url.a.run.app/healthz`

### 3. GitHub Repository References

#### Repository URLs

- **Main Repository**: `https://github.com/kpernyer/living-twin-monorep.git`
- **Project URLs in pyproject.toml**:
  - Homepage: `https://github.com/your-org/living-twin`
  - Repository: `https://github.com/your-org/living-twin.git`
  - Issues: `https://github.com/your-org/living-twin/issues`

#### GitHub Actions and CI/CD

- **Workload Identity Federation**: References to GitHub repository paths
- **Service Account Bindings**: GitHub-specific IAM configurations

### 4. Mock Organization Data

#### Demo Organizations (Hardcoded in `apps/api/app/adapters/local_mock_repo.py`)

#### **Acme Corporation (`aprio_org_acme`)**

- Domain: `acme.com`
- Website: `https://acme.com`
- Logo: `https://acme.com/logo.png`
- Admin Portal: `https://admin.acme.aprioone.com`
- Tech Contact: `tech@acme.com`
- Business Contact: `hr@acme.com`
- Sample Users: `john@acme.com`, `admin@acme.com`

**TechCorp Industries (`aprio_org_techcorp`)**

- Domain: `techcorp.io`
- Website: `https://techcorp.io`
- Logo: `https://techcorp.io/logo.png`
- Admin Portal: `https://admin.techcorp.aprioone.com`
- Tech Contact: `it@techcorp.io`
- Business Contact: `admin@techcorp.io`
- Sample Users: `bob@techcorp.io`

**BIG Corp Solutions (`aprio_org_bigcorp`)**

- Domain: `bigcorp.com`
- Website: `https://bigcorp.com`
- Logo: `https://bigcorp.com/assets/logo.png`
- Admin Portal: `https://admin.bigcorp.aprioone.com`
- Tech Contact: `it@bigcorp.com`
- Business Contact: `hr@bigcorp.com`
- 40+ Sample Users: `sarah.chen@bigcorp.com`, `marcus.johnson@bigcorp.com`, etc.

#### **Demo Organization**

- Domain: `aprioone.com`
- Website: `https://demo.aprioone.com`
- Logo: `https://demo.aprioone.com/logo.png`
- Admin Portal: `https://demo.aprioone.com`
- Contacts: `demo@aprioone.com`
- Sample Users: `demo@example.com`

### 5. Third-Party Service URLs

#### External APIs and Services

- **OpenAI API**: `https://api.openai.com/v1`
- **Google Services**:
  - Firebase Token Issuer: `https://securetoken.google.com/PROJECT_ID`
  - Service Account JWKs: `https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com`
- **Notification Webhooks**: `https://hooks.example.com/services/YOUR/WEBHOOK`
- **Prometheus**: `http://localhost:9090` (for local monitoring)
- **Jira API**: `https://your-org.atlassian.net/rest/api/3`
- **Linear API**: `https://api.linear.app/graphql`
- **Firecrawl API**: `https://api.firecrawl.dev`

#### Installation and Setup URLs

- **Homebrew Install**: `https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh`
- **Docker Install**: `https://get.docker.com`
- **Node.js Setup**: `https://deb.nodesource.com/setup_20.x`
- **Flutter Download**: `https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.16.0-stable.tar.xz`
- **VS Code Repository**: `https://packages.microsoft.com/repos/code`

### 6. Documentation and Reference URLs

#### External Documentation Links

- **GitHub Actions**: `https://docs.github.com/en/actions`
- **Branch Protection**: `https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches`
- **Workload Identity**: `https://cloud.google.com/iam/docs/workload-identity-federation`
- **Conventional Commits**: `https://www.conventionalcommits.org/`
- **Git Flow**: `https://nvie.com/posts/a-successful-git-branching-model/`
- **Semantic Versioning**: `https://semver.org/`

## Impact Assessment by Component

### High Impact (Requires Updates for Production)

#### 1. Mobile App Configuration

**File**: `apps/mobile/lib/config/app_config.dart`

- **Issue**: Hardcoded API URLs for staging and production
- **Action Required**: Update `_stagingApiUrl` and `_prodApiUrl` for your deployment

#### 2. Mock Data Repository

**File**: `apps/api/app/adapters/local_mock_repo.py`

- **Issue**: Contains extensive mock organization data with specific domains and email addresses
- **Action Required**: Replace with your actual organization data or make configurable

#### 3. Frontend Authentication

**Files**:

- `apps/admin_web/src/features/auth/AuthProvider.jsx`
- `apps/mobile/lib/services/auth.dart`
- **Issue**: Hardcoded organization mappings and domain bindings
- **Action Required**: Replace with dynamic configuration or environment variables

### Medium Impact (Environment-Specific)

#### 1. GitHub Repository References

**Files**: `apps/api/pyproject.toml`, various documentation

- **Issue**: References to specific GitHub repository
- **Action Required**: Update repository URLs when forking or moving

#### 2. Development Environment URLs

**Files**: Multiple configuration files

- **Issue**: Localhost URLs for development
- **Action Required**: Ensure proper environment variable overrides for different deployment environments

### Low Impact (Documentation/Examples)

#### 1. Documentation Examples

**Files**: Various `.md` files in `docs/`

- **Issue**: Example URLs and email addresses in documentation
- **Action Required**: Update examples to match your organization

## Recommendations for Production Deployment

### 1. Environment Variable Strategy

Create environment-specific configurations:

```bash
# Production Environment Variables
PRODUCTION_API_URL=https://api.yourcompany.com
STAGING_API_URL=https://api-staging.yourcompany.com
ADMIN_PORTAL_BASE_URL=https://admin.yourcompany.com

# Organization Configuration
DEFAULT_ORG_DOMAIN=yourcompany.com
DEFAULT_ORG_NAME="Your Company Name"
DEFAULT_TECH_CONTACT=tech@yourcompany.com
DEFAULT_BUSINESS_CONTACT=hr@yourcompany.com
```

### 2. Configuration Management

#### Replace Hardcoded Mock Data

- Move organization data to database or configuration files
- Implement dynamic organization registration
- Use environment variables for default values

#### Update Repository References

- Search and replace GitHub URLs with your repository
- Update CI/CD configurations
- Modify documentation examples

### 3. Domain and Email Configuration

#### Create Domain Mapping System

```python
# Example configuration structure
ORGANIZATION_DOMAINS = {
    "yourcompany.com": {
        "id": "org_yourcompany",
        "name": "Your Company",
        "admin_portal": f"https://admin.{os.getenv('BASE_DOMAIN')}",
        "tech_contact": f"tech@{os.getenv('BASE_DOMAIN')}",
        "business_contact": f"hr@{os.getenv('BASE_DOMAIN')}"
    }
}
```

### 4. Mobile App Deployment

#### Update API Endpoints

- Configure build-time variables for different environments
- Implement feature flags for environment-specific behavior
- Update app store metadata and descriptions

## Security Considerations

### 1. Remove Demo Data

- **Critical**: Remove all mock user accounts and organizations before production
- **Important**: Ensure no test email addresses remain in production code
- **Recommended**: Implement proper user registration and organization setup flows

### 2. URL Validation

- Validate all external URLs are accessible from production environment
- Ensure HTTPS is used for all production endpoints
- Implement proper CORS configuration for your domains

### 3. Email Configuration

- Configure proper SMTP settings for your domain
- Set up email templates with your branding
- Implement email verification for user registration

## Migration Checklist

### Pre-Deployment

- [ ] Update all API URLs in mobile app configuration
- [ ] Replace mock organization data with real data
- [ ] Update GitHub repository references
- [ ] Configure environment variables for all environments
- [ ] Update documentation with your organization's information

### During Deployment

- [ ] Verify all external URLs are accessible
- [ ] Test email functionality with your domain
- [ ] Validate organization domain binding works correctly
- [ ] Confirm mobile app connects to correct API endpoints

### Post-Deployment

- [ ] Monitor logs for any hardcoded URL references
- [ ] Test user registration and organization binding
- [ ] Verify all external integrations work correctly
- [ ] Update any remaining documentation references

## Conclusion

The Living Twin codebase contains numerous hardcoded references that need to be addressed for production deployment. The most critical areas are the mock organization data and API endpoint configurations. Implementing a proper environment variable strategy and configuration management system will make the application more flexible and production-ready.

Priority should be given to:

1. Replacing mock data with configurable organization settings
2. Updating API endpoints for mobile applications
3. Implementing proper environment variable management
4. Removing all demo/test data before production deployment

---

*This analysis was conducted in January 2025. Regular reviews should be performed as the codebase evolves.*
