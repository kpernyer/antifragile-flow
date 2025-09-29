# API Key and Budget Management Strategy

## Overview

This document outlines the comprehensive strategy for managing API keys, service accounts, and budgets across multiple environments (Development, CI/CD, Staging, Production) for the Living Twin platform.

## 1. Environment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     PRODUCTION                              │
│  • Dedicated GCP Project                                    │
│  • Separate API keys with high quotas                       │
│  • Budget alerts at 50%, 75%, 90%                          │
│  • Cost cap at $X,000/month                                │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      STAGING                                │
│  • Shared GCP Project with Dev                             │
│  • Limited API keys with medium quotas                      │
│  • Budget alerts at 75%, 90%                               │
│  • Cost cap at $500/month                                  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT                              │
│  • Shared GCP Project with Staging                         │
│  • Development API keys with low quotas                     │
│  • Budget alerts at 90%                                    │
│  • Cost cap at $100/month                                  │
│  • Local services preferred (local LLM, emulators)         │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      CI/CD                                  │
│  • Minimal API usage                                       │
│  • Mock services for testing                               │
│  • Test-specific keys with minimal quotas                  │
│  • Cost cap at $50/month                                   │
└─────────────────────────────────────────────────────────────┘
```

## 2. API Key Structure

### 2.1 OpenAI API Keys

| Environment | Key Naming | Monthly Budget | Rate Limits | Purpose |
|------------|------------|----------------|-------------|---------|
| Production | `OPENAI_API_KEY_PROD` | $2,000 | 1000 req/min | Customer queries |
| Staging | `OPENAI_API_KEY_STAGING` | $200 | 100 req/min | Testing & QA |
| Development | `OPENAI_API_KEY_DEV` | $50 | 20 req/min | Development |
| CI/CD | `OPENAI_API_KEY_TEST` | $10 | 5 req/min | Automated tests |
| Local Dev | Use Ollama/LM Studio | $0 | Unlimited | Local development |

### 2.2 Google Cloud Service Accounts

| Environment | Service Account | IAM Roles | Budget |
|------------|----------------|-----------|---------|
| Production | `living-twin-prod@{project}.iam` | Production roles | Per service |
| Staging | `living-twin-staging@{project}.iam` | Staging roles | Shared budget |
| Development | `living-twin-dev@{project}.iam` | Developer roles | Minimal |
| CI/CD | `living-twin-ci@{project}.iam` | CI/CD specific | Minimal |

### 2.3 Firebase Service Accounts

| Environment | Purpose | Permissions |
|------------|---------|-------------|
| Production | Customer authentication | Full Firebase Auth |
| Staging | Testing authentication | Limited Firebase Auth |
| Development | Local emulator | Emulator only |
| CI/CD | Test users | Mock authentication |

## 3. Environment-Specific Configuration Files

### 3.1 File Structure
```
.env/
├── .env.production    # Production API keys (encrypted)
├── .env.staging       # Staging API keys
├── .env.development   # Development API keys
├── .env.test         # CI/CD test keys
└── .env.local        # Local development (uses emulators)
```

### 3.2 Configuration Templates

#### Production (.env.production)
```bash
# OpenAI Configuration
OPENAI_API_KEY=${OPENAI_API_KEY_PROD}
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7
OPENAI_RATE_LIMIT=1000

# GCP Configuration
GCP_PROJECT_ID=living-twin-prod
GCP_REGION=europe-west1
GCP_SERVICE_ACCOUNT=living-twin-prod@living-twin-prod.iam.gserviceaccount.com

# Neo4j Configuration (Production Cluster)
NEO4J_URI=neo4j+s://prod-cluster.neo4j.io
NEO4J_USER=${NEO4J_PROD_USER}
NEO4J_PASSWORD=${NEO4J_PROD_PASSWORD}

# Firebase Configuration
FIREBASE_PROJECT_ID=living-twin-prod
FIREBASE_AUTH_DOMAIN=living-twin-prod.firebaseapp.com

# Cost Controls
MAX_MONTHLY_COST=5000
ALERT_THRESHOLDS=50,75,90
ENABLE_COST_CAPS=true
```

#### Staging (.env.staging)
```bash
# OpenAI Configuration
OPENAI_API_KEY=${OPENAI_API_KEY_STAGING}
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7
OPENAI_RATE_LIMIT=100

# GCP Configuration
GCP_PROJECT_ID=living-twin-staging
GCP_REGION=europe-west1
GCP_SERVICE_ACCOUNT=living-twin-staging@living-twin-staging.iam.gserviceaccount.com

# Neo4j Configuration (Staging Instance)
NEO4J_URI=neo4j://staging.neo4j.io
NEO4J_USER=${NEO4J_STAGING_USER}
NEO4J_PASSWORD=${NEO4J_STAGING_PASSWORD}

# Firebase Configuration
FIREBASE_PROJECT_ID=living-twin-staging
FIREBASE_AUTH_DOMAIN=living-twin-staging.firebaseapp.com

# Cost Controls
MAX_MONTHLY_COST=500
ALERT_THRESHOLDS=75,90
ENABLE_COST_CAPS=true
```

#### Development (.env.development)
```bash
# OpenAI Configuration (Limited)
OPENAI_API_KEY=${OPENAI_API_KEY_DEV}
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.7
OPENAI_RATE_LIMIT=20

# Local LLM Configuration (Preferred for Dev)
USE_LOCAL_LLM=true
LOCAL_LLM_ENDPOINT=http://localhost:11434
LOCAL_LLM_MODEL=llama2

# GCP Configuration
GCP_PROJECT_ID=living-twin-dev
GCP_REGION=europe-west1
GCP_SERVICE_ACCOUNT=living-twin-dev@living-twin-dev.iam.gserviceaccount.com

# Neo4j Configuration (Local)
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Firebase Configuration (Emulators)
FIREBASE_USE_EMULATOR=true
FIRESTORE_EMULATOR_HOST=localhost:8080
FIREBASE_AUTH_EMULATOR_HOST=localhost:9099

# Cost Controls
MAX_MONTHLY_COST=100
ALERT_THRESHOLDS=90
ENABLE_COST_CAPS=true
```

#### CI/CD (.env.test)
```bash
# Mock Services
USE_MOCK_SERVICES=true
MOCK_LLM_RESPONSES=true

# Minimal OpenAI (for integration tests only)
OPENAI_API_KEY=${OPENAI_API_KEY_TEST}
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=100
OPENAI_RATE_LIMIT=5

# Test Database
NEO4J_URI=neo4j://test-neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=test

# Firebase Test Mode
FIREBASE_USE_EMULATOR=true
FIREBASE_PROJECT_ID=demo-test

# Cost Controls
MAX_MONTHLY_COST=50
ENABLE_COST_CAPS=true
```

## 4. Budget Control Implementation

### 4.1 GCP Budget Alerts
```terraform
# terraform/modules/budgets/main.tf
resource "google_billing_budget" "environment_budget" {
  billing_account = var.billing_account
  display_name    = "living-twin-${var.environment}-budget"

  budget_filter {
    projects = ["projects/${var.project_id}"]
    services = var.monitored_services
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = var.monthly_budget
    }
  }

  threshold_rules {
    threshold_percent = 0.5
    spend_basis      = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 0.75
    spend_basis      = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 0.9
    spend_basis      = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 1.0
    spend_basis      = "FORECASTED_SPEND"
  }

  all_updates_rule {
    pubsub_topic = google_pubsub_topic.budget_alerts.id
  }
}
```

### 4.2 Cost Monitoring Script
```python
# tools/scripts/monitor_costs.py
import os
from google.cloud import billing_v1
from datetime import datetime, timedelta

class CostMonitor:
    def __init__(self, project_id: str, environment: str):
        self.project_id = project_id
        self.environment = environment
        self.client = billing_v1.CloudBillingClient()

    def get_current_costs(self):
        """Get current month's costs by service"""
        # Implementation details
        pass

    def check_budget_alerts(self):
        """Check if any budget thresholds are exceeded"""
        # Implementation details
        pass

    def generate_cost_report(self):
        """Generate detailed cost report"""
        # Implementation details
        pass
```

## 5. Secret Management

### 5.1 Google Secret Manager Structure
```
living-twin-secrets/
├── production/
│   ├── openai-api-key
│   ├── neo4j-credentials
│   └── firebase-service-account
├── staging/
│   ├── openai-api-key
│   ├── neo4j-credentials
│   └── firebase-service-account
├── development/
│   ├── openai-api-key
│   └── neo4j-credentials
└── ci-cd/
    └── test-api-keys
```

### 5.2 Access Control
```yaml
# IAM Bindings for Secret Access
production:
  - role: roles/secretmanager.secretAccessor
    members:
      - serviceAccount:living-twin-prod@project.iam.gserviceaccount.com

staging:
  - role: roles/secretmanager.secretAccessor
    members:
      - serviceAccount:living-twin-staging@project.iam.gserviceaccount.com
      - group:qa-team@company.com

development:
  - role: roles/secretmanager.secretAccessor
    members:
      - group:developers@company.com

ci-cd:
  - role: roles/secretmanager.secretAccessor
    members:
      - serviceAccount:github-actions@project.iam.gserviceaccount.com
```

## 6. Cost Optimization Strategies

### 6.1 Development Environment
- **Use Local Services**: Ollama, LM Studio for LLMs
- **Firebase Emulators**: Avoid cloud costs
- **Scale to Zero**: All services scale down when not in use
- **Shared Resources**: Share Neo4j instance among developers

### 6.2 CI/CD Pipeline
- **Mock Services**: Use mocked responses for most tests
- **Minimal API Calls**: Only integration tests use real APIs
- **Ephemeral Resources**: Spin up/down test resources
- **Cached Dependencies**: Reduce repeated downloads

### 6.3 Staging Environment
- **Scheduled Scaling**: Scale down during off-hours
- **Lower Tier Models**: Use gpt-3.5-turbo instead of gpt-4
- **Request Throttling**: Implement rate limiting
- **Resource Quotas**: Set hard limits on resource usage

### 6.4 Production Environment
- **Intelligent Caching**: Cache LLM responses where appropriate
- **Request Batching**: Batch API calls when possible
- **Model Selection**: Use appropriate models for each task
- **Cost-Based Routing**: Route to cheaper services when quality permits

## 7. Implementation Checklist

### 7.1 Initial Setup
- [ ] Create separate GCP projects for prod/staging
- [ ] Set up billing accounts and budgets
- [ ] Create service accounts for each environment
- [ ] Configure Secret Manager with all API keys
- [ ] Set up budget alerts and notifications

### 7.2 Development Setup
- [ ] Install local LLM (Ollama/LM Studio)
- [ ] Configure Firebase emulators
- [ ] Set up local Neo4j instance
- [ ] Create .env.local with local configurations
- [ ] Test local development workflow

### 7.3 CI/CD Configuration
- [ ] Create minimal test API keys
- [ ] Set up mock service responses
- [ ] Configure GitHub Actions secrets
- [ ] Implement cost monitoring in CI/CD
- [ ] Add budget checks to deployment pipeline

### 7.4 Monitoring & Alerting
- [ ] Set up cost monitoring dashboard
- [ ] Configure Slack/email alerts for budgets
- [ ] Create monthly cost reports
- [ ] Implement automatic scaling based on costs
- [ ] Set up anomaly detection for unusual spending

## 8. Makefile Targets for Cost Control

As mentioned, you already have cost control targets in your Makefile:

```bash
# Check current costs
make check-costs ENV=dev PROJECT=your-project

# Check resource configuration
make check-resources ENV=dev PROJECT=your-project

# Optimize costs for development
make cost-optimize-dev PROJECT=your-project

# Scale down staging during off-hours
make scale-down-staging PROJECT=your-project
```

## 9. Emergency Cost Control

### 9.1 Circuit Breakers
```python
# apps/api/app/middleware/cost_control.py
class CostControlMiddleware:
    async def __call__(self, request, call_next):
        if self.is_budget_exceeded():
            return JSONResponse(
                status_code=503,
                content={"error": "Service temporarily unavailable due to budget limits"}
            )
        return await call_next(request)
```

### 9.2 Automatic Scaling Down
```yaml
# Cloud Scheduler job to scale down services
schedule: "0 2 * * *"  # 2 AM daily
job:
  - scale Cloud Run instances to min=0
  - pause non-critical Pub/Sub subscriptions
  - notify ops team
```

## 10. Best Practices

### 10.1 API Key Rotation
- Rotate production keys quarterly
- Rotate staging keys monthly
- Use key versioning in Secret Manager
- Maintain audit logs of key access

### 10.2 Cost Attribution
- Tag all resources with environment labels
- Use separate billing accounts per environment
- Implement cost allocation by tenant/customer
- Track per-feature cost metrics

### 10.3 Developer Guidelines
1. Always use local services for development
2. Never commit API keys to version control
3. Request production access only when necessary
4. Monitor your personal development costs
5. Use the cheapest appropriate model for testing

## 11. Monitoring Dashboard

Create a monitoring dashboard that displays:
- Current month's spend by environment
- API usage by service
- Cost trends and projections
- Budget alert status
- Per-customer cost attribution

## 12. API Key Theft Detection & Security Monitoring

### 12.1 Security Monitoring System
A comprehensive security monitoring system (`tools/scripts/api_security_monitor.py`) detects potential API key theft through:

#### Detection Methods:
- **Usage Spikes**: Detects 10x normal usage patterns
- **Concurrent Usage**: Multiple IPs using same key simultaneously
- **Geographic Anomalies**: Requests from unusual countries
- **Pattern Anomalies**: Unusual times, suspicious user agents
- **Burst Detection**: 100+ requests per minute threshold

#### Threat Levels:
- **CRITICAL**: Definite compromise (immediate blocking)
- **HIGH**: Likely compromise (key rotation)
- **MEDIUM**: Suspicious activity (throttling)
- **LOW**: Unusual but explainable (monitoring)

#### Automatic Actions:
```python
# Immediate blocking for critical threats
if threat_level == CRITICAL:
    - Block API key immediately
    - Send SMS alert
    - Trigger PagerDuty
    - Email security team

# Key rotation for high threats
if threat_level == HIGH:
    - Initiate key rotation
    - Apply rate limiting
    - Send alerts to all channels

# Throttling for medium threats
if threat_level == MEDIUM:
    - Reduce rate limit to 10 req/min
    - Monitor closely
    - Send warning alerts
```

### 12.2 Running Security Monitoring

#### Continuous Monitoring:
```bash
# Start real-time monitoring
python tools/scripts/api_security_monitor.py --environment production --continuous

# Check specific API key
python tools/scripts/api_security_monitor.py --environment production --api-key "sk-xxxxx"

# Generate security report
python tools/scripts/api_security_monitor.py --environment production --report

# Test detection system
python tools/scripts/api_security_monitor.py --environment development --simulate
```

#### Integration with Middleware:
```python
# apps/api/app/middleware/security_monitor.py
from tools.scripts.api_security_monitor import APISecurityMonitor

class SecurityMiddleware:
    def __init__(self):
        self.monitor = APISecurityMonitor(os.getenv("ENVIRONMENT"))

    async def __call__(self, request, call_next):
        # Extract API key and request details
        api_key = request.headers.get("X-API-Key")
        ip = request.client.host
        user_agent = request.headers.get("User-Agent", "")

        # Check for threats
        events = self.monitor.check_all_threats(
            api_key, ip, user_agent, request.url.path
        )

        # Handle critical threats
        for event in events:
            if event.threat_level == ThreatLevel.CRITICAL:
                return JSONResponse(
                    status_code=403,
                    content={"error": "API key has been blocked for security reasons"}
                )
            elif event.threat_level == ThreatLevel.HIGH:
                # Apply rate limiting
                request.state.rate_limit = 10  # Reduce to 10 req/min

        return await call_next(request)
```

### 12.3 Alert Channels

Configure multiple alert channels for different threat levels:

#### Email Alerts (All levels):
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@company.com
SECURITY_EMAIL=security@company.com
```

#### Slack Alerts (Medium and above):
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/yyy/zzz
SLACK_CHANNEL=#security-alerts
```

#### SMS Alerts (Critical only):
```bash
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_FROM=+1234567890
SECURITY_PHONE=+0987654321
```

#### PagerDuty (Critical only):
```bash
PAGERDUTY_INTEGRATION_KEY=xxxxx
PAGERDUTY_SERVICE_ID=xxxxx
```

### 12.4 Security Baselines

The system learns normal usage patterns and detects deviations:

```python
# Normal baseline example
baseline = {
    "avg_requests_per_hour": 100,
    "typical_hours": [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
    "typical_countries": ["United States", "United Kingdom"],
    "typical_ips": ["192.168.1.1", "10.0.0.1"],
    "max_concurrent_ips": 2
}
```

### 12.5 Security Dashboard

Monitor security events in real-time:

```bash
# Create security dashboard
make security-dashboard

# View blocked keys
redis-cli SMEMBERS blocked_keys

# View throttled keys
redis-cli KEYS throttled:*

# Check security audit log
tail -f security_audit_production.log
```

### 12.6 Incident Response Playbook

When API key theft is detected:

1. **Immediate Actions** (0-5 minutes):
   - API key automatically blocked
   - Security team notified via all channels
   - Audit log preserved

2. **Investigation** (5-30 minutes):
   - Review security event evidence
   - Identify attack pattern
   - Check for data exfiltration

3. **Remediation** (30-60 minutes):
   - Rotate affected API keys
   - Update security baselines
   - Patch any vulnerabilities

4. **Post-Incident** (within 24 hours):
   - Generate incident report
   - Update security policies
   - Notify affected customers if needed

## 13. Regular Reviews

### Monthly Reviews
- Review cost reports for each environment
- Analyze security events and patterns
- Identify cost optimization opportunities
- Update budgets based on usage patterns
- Review and rotate API keys

### Quarterly Reviews
- Evaluate model selection strategy
- Review infrastructure scaling settings
- Update cost allocation models
- Audit security baselines
- Plan capacity for next quarter

## Conclusion

This comprehensive API key and budget management strategy ensures:
- **Security**: Isolated keys per environment with theft detection
- **Cost Control**: Hard limits and alerts
- **Flexibility**: Easy to adjust budgets
- **Visibility**: Clear cost attribution
- **Protection**: Real-time threat detection and automatic response
- **Optimization**: Continuous improvement

The addition of the security monitoring system provides peace of mind that your API keys are protected against theft and abuse, with automatic detection and response capabilities that can block suspicious activity within seconds.

Remember to regularly review and update these configurations as your usage patterns evolve.
