# Security & Performance Testing Guide

> **Tools**: Trivy (Security Scanning) + K6 (Load Testing)
> **Integration**: GitHub Actions CI/CD Pipeline + Local Development

## 🔒 **Trivy Security Scanning**

### **What is Trivy?**

Trivy is a comprehensive security scanner that detects vulnerabilities in:

- **Container images** (OS packages, language-specific packages)
- **Filesystem** (source code dependencies)
- **Git repositories** (secrets, misconfigurations)
- **Kubernetes** (cluster configurations)

### **How We Use Trivy**

#### **1. Automated CI/CD Scanning**

```yaml
# .github/workflows/deploy-cloud-run.yml
security:
  runs-on: ubuntu-latest
  if: github.event_name == 'push'
  steps:
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: ${{ env.GAR_LOCATION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.REPOSITORY }}/${{ env.SERVICE }}:${{ github.sha }}
        format: 'sarif'
        output: 'trivy-results.sarif'

    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
```

**What This Does**:

- ✅ **Scans every Docker image** before deployment
- ✅ **Uploads results to GitHub Security tab** for tracking
- ✅ **Blocks deployment** if critical vulnerabilities found
- ✅ **SARIF format** for integration with security tools

#### **2. Local Security Scanning**

**Install Trivy locally**:

```bash
# macOS
brew install trivy

# Ubuntu/Debian
sudo apt-get install wget apt-transport-https gnupg lsb-release
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy
```

**Scan your local Docker images**:

```bash
# Build your image first
make docker-build

# Scan the API container
trivy image living_twin_monorepo-api:latest

# Scan with specific severity levels
trivy image --severity HIGH,CRITICAL living_twin_monorepo-api:latest

# Scan and output to JSON
trivy image --format json --output results.json living_twin_monorepo-api:latest

# Scan filesystem (source code dependencies)
trivy fs apps/api/

# Scan for secrets in git repo
trivy repo .
```

#### **3. Trivy Configuration**

**Create `.trivyignore` file** to ignore false positives:

```bash
# .trivyignore
CVE-2023-12345  # False positive - not applicable to our use case
CVE-2023-67890  # Fixed in our custom build
```

**Advanced scanning options**:

```bash
# Scan specific package types only
trivy image --pkg-types os,library your-image:tag

# Skip certain directories
trivy fs --skip-dirs node_modules,vendor apps/

# Custom policy with OPA Rego
trivy image --policy custom-policy.rego your-image:tag
```

### **4. Security Scanning Results**

**View results in GitHub**:

1. Go to **Security** tab in your GitHub repo
2. Click **Code scanning alerts**
3. Review Trivy findings with severity levels
4. Create issues for critical vulnerabilities

**Local results interpretation**:

```bash
# Example output
Total: 45 (UNKNOWN: 0, LOW: 20, MEDIUM: 15, HIGH: 8, CRITICAL: 2)

┌─────────────────────────────────────┬──────────────────┬──────────┬───────────────────┬───────────────┬─────────────────────────────────────┐
│                Library              │    Vulnerability │ Severity │ Installed Version │ Fixed Version │                Title                │
├─────────────────────────────────────┼──────────────────┼──────────┼───────────────────┼───────────────┼─────────────────────────────────────┤
│ openssl                            │ CVE-2023-12345   │ CRITICAL │ 1.1.1f            │ 1.1.1g        │ OpenSSL buffer overflow             │
│ python3.11                         │ CVE-2023-67890   │ HIGH     │ 3.11.0            │ 3.11.1        │ Python arbitrary code execution     │
└─────────────────────────────────────┴──────────────────┴──────────┴───────────────────┴───────────────┴─────────────────────────────────────┘
```

---

## ⚡ **K6 Load Testing**

### **What is K6?**

K6 is a modern load testing tool that uses JavaScript to define test scenarios and provides:

- **HTTP/WebSocket/gRPC** protocol support
- **Realistic load patterns** with virtual users
- **Rich metrics** and thresholds
- **CI/CD integration** for automated performance testing

### **How We Use K6**

#### **1. Automated Performance Testing**

```yaml
# .github/workflows/deploy-cloud-run.yml
performance:
  needs: deploy
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/staging'
  steps:
    - name: Run load tests
      run: |
        # Install k6
        sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
        echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
        sudo apt-get update
        sudo apt-get install k6

        # Run performance tests against staging
        k6 run --out json=results.json tools/scripts/load-test.js
```

**What This Does**:

- ✅ **Tests staging environment** after deployment
- ✅ **Validates performance thresholds** (95% < 500ms, error rate < 10%)
- ✅ **Prevents production deployment** if performance degrades
- ✅ **Stores results** as artifacts for analysis

#### **2. Local Performance Testing**

**Install K6 locally**:

```bash
# macOS
brew install k6

# Ubuntu/Debian
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6

# Windows
winget install k6
```

**Run load tests locally**:

```bash
# Test against local development server
make docker-up  # Start local environment
BASE_URL=http://localhost:8000 k6 run tools/scripts/load-test.js

# Test with different load patterns
k6 run --vus 50 --duration 30s tools/scripts/load-test.js

# Test with custom thresholds
k6 run --threshold http_req_duration=p(95)<200 tools/scripts/load-test.js

# Output results to different formats
k6 run --out json=results.json tools/scripts/load-test.js
k6 run --out csv=results.csv tools/scripts/load-test.js
```

#### **3. K6 Test Configuration**

**Our current test scenario** (`tools/scripts/load-test.js`):

```javascript
export let options = {
  stages: [
    { duration: '2m', target: 10 }, // Ramp up to 10 users
    { duration: '5m', target: 10 }, // Stay at 10 users
    { duration: '2m', target: 20 }, // Ramp up to 20 users
    { duration: '5m', target: 20 }, // Stay at 20 users
    { duration: '2m', target: 0 },  // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests must complete below 500ms
    http_req_failed: ['rate<0.1'],    // Error rate must be below 10%
    errors: ['rate<0.1'],             // Custom error rate must be below 10%
  },
};
```

**Test scenarios covered**:

- ✅ **Health checks** (`/healthz`)
- ✅ **RAG search queries** (`/search`)
- ✅ **Document ingestion** (`/ingest/text`)
- ✅ **Goals API** (`/goals`)
- ✅ **Users API** (`/users`)

#### **4. Advanced K6 Usage**

**Create custom test scenarios**:

```javascript
// Spike testing
export let options = {
  stages: [
    { duration: '10s', target: 100 }, // Fast ramp-up to a high point
    { duration: '1m', target: 100 },  // Stay at high point
    { duration: '10s', target: 0 },   // Quick ramp-down to 0 users
  ],
};

// Stress testing
export let options = {
  stages: [
    { duration: '2m', target: 100 }, // Ramp up to normal load
    { duration: '5m', target: 100 }, // Stay at normal load
    { duration: '2m', target: 200 }, // Ramp up to high load
    { duration: '5m', target: 200 }, // Stay at high load
    { duration: '2m', target: 300 }, // Ramp up to breaking point
    { duration: '5m', target: 300 }, // Stay at breaking point
    { duration: '2m', target: 0 },   // Ramp down
  ],
};
```

**Test with authentication**:

```javascript
// Add to your test script
import { authenticate } from './auth-helper.js';

export function setup() {
  // Get auth token for testing
  let authToken = authenticate('test-user@example.com', 'password');
  return { token: authToken };
}

export default function (data) {
  let params = {
    headers: {
      'Authorization': `Bearer ${data.token}`,
      'Content-Type': 'application/json',
    },
  };

  let response = http.get(`${BASE_URL}/protected-endpoint`, params);
  // ... rest of test
}
```

#### **5. Performance Metrics & Analysis**

**Key metrics K6 provides**:

```bash
# Example K6 output
     ✓ health check status is 200
     ✓ search response time < 2000ms
     ✓ ingest endpoint responds

     checks.........................: 100.00% ✓ 2847      ✗ 0
     data_received..................: 1.2 MB  6.4 kB/s
     data_sent......................: 486 kB  2.6 kB/s
     http_req_blocked...............: avg=1.15ms   min=1µs      med=5µs      max=367.36ms p(90)=11µs     p(95)=17µs
     http_req_connecting............: avg=580µs    min=0s       med=0s       max=128.73ms p(90)=0s       p(95)=0s
     http_req_duration..............: avg=159.52ms min=101.11ms med=148.31ms max=1.18s    p(90)=221.44ms p(95)=267.52ms
       { expected_response:true }...: avg=159.52ms min=101.11ms med=148.31ms max=1.18s    p(90)=221.44ms p(95)=267.52ms
     http_req_failed................: 0.00%   ✓ 0         ✗ 949
     http_req_receiving.............: avg=128µs    min=49µs     med=103µs    max=1.49ms   p(90)=182µs    p(95)=221µs
     http_req_sending...............: avg=43µs     min=17µs     med=36µs     max=264µs    p(90)=64µs     p(95)=81µs
     http_req_tls_handshaking.......: avg=0s       min=0s       med=0s       max=0s       p(90)=0s       p(95)=0s
     http_req_waiting...............: avg=159.35ms min=101.01ms med=148.14ms max=1.18s    p(90)=221.26ms p(95)=267.29ms
     http_reqs......................: 949     5.048025/s
     iteration_duration.............: avg=3.95s    min=3.61s    med=3.93s    max=5.18s    p(90)=4.22s    p(95)=4.37s
     iterations.....................: 188     1.000799/s
     vus............................: 1       min=1        max=20
     vus_max........................: 20      min=20       max=20
```

---

## 🔧 **Integration with Makefile**

Add these commands to your `Makefile` for easy local testing:

```makefile
# Security scanning
security-scan:
 @echo "🔒 Running security scan with Trivy..."
 trivy image --severity HIGH,CRITICAL living_twin_monorepo-api:latest

security-scan-all:
 @echo "🔒 Running comprehensive security scan..."
 trivy image living_twin_monorepo-api:latest
 trivy fs apps/api/
 trivy repo .

# Performance testing
load-test-local:
 @echo "⚡ Running load tests against local environment..."
 @if ! command -v k6 &> /dev/null; then echo "❌ k6 not installed. Run: brew install k6"; exit 1; fi
 BASE_URL=http://localhost:8000 k6 run tools/scripts/load-test.js

load-test-staging:
 @echo "⚡ Running load tests against staging..."
 @if [ -z "$(STAGING_URL)" ]; then echo "❌ STAGING_URL is required. Usage: make load-test-staging STAGING_URL=https://your-staging-url"; exit 1; fi
 BASE_URL=$(STAGING_URL) k6 run tools/scripts/load-test.js

# Combined security and performance validation
validate-deployment: security-scan load-test-local
 @echo "✅ Deployment validation complete"
```

**Usage**:

```bash
# Run security scan
make security-scan

# Run load tests locally
make docker-up
make load-test-local

# Test staging environment
make load-test-staging STAGING_URL=https://your-staging-url.run.app

# Full validation
make validate-deployment
```

---

## 📊 **Monitoring & Alerting**

### **GitHub Security Integration**

- **Security tab** shows all Trivy findings
- **Dependabot alerts** for dependency vulnerabilities
- **Code scanning alerts** with severity levels
- **Security advisories** for your repositories

### **Performance Monitoring**

- **K6 results** stored as GitHub Actions artifacts
- **Performance regression detection** via threshold failures
- **Notifications** for failed performance tests sent to the organization's communication platform
- **Historical performance data** tracking

### **Local Development Workflow**

```bash
# Before committing code
make security-scan          # Check for vulnerabilities
make load-test-local        # Validate performance
git commit -m "feature: ..."

# CI/CD will automatically:
# 1. Run Trivy security scan
# 2. Deploy to staging
# 3. Run K6 performance tests
# 4. Deploy to production (if all tests pass)
```

---

## 🎯 **Best Practices**

### **Security Scanning**

- ✅ **Scan early and often** - integrate into development workflow
- ✅ **Fix critical vulnerabilities** before deployment
- ✅ **Keep base images updated** - use latest stable versions
- ✅ **Use .trivyignore** for false positives, but document why
- ✅ **Monitor security advisories** for your dependencies

### **Performance Testing**

- ✅ **Test realistic scenarios** - use actual API endpoints and data
- ✅ **Set appropriate thresholds** - based on your SLA requirements
- ✅ **Test different load patterns** - normal, peak, spike, stress
- ✅ **Monitor resource usage** - CPU, memory, database connections
- ✅ **Test with authentication** - realistic user scenarios

### **CI/CD Integration**

- ✅ **Fail fast** - block deployment on security/performance issues
- ✅ **Test staging first** - validate before production
- ✅ **Store results** - track trends over time
- ✅ **Alert on failures** - immediate notification for issues
- ✅ **Automate everything** - no manual security/performance checks

---

## 🚀 **Next Steps**

### **Enhanced Security**

- **SAST scanning** with CodeQL for source code analysis
- **Dependency scanning** with Snyk or GitHub Dependabot
- **Infrastructure scanning** with Checkov for Terraform
- **Runtime security** with Falco for container monitoring

### **Advanced Performance Testing**

- **Browser testing** with K6 browser module
- **API contract testing** with Pact
- **Chaos engineering** with Litmus or Chaos Monkey
- **Real user monitoring** with synthetic transactions

Your current Trivy + K6 setup provides excellent security and performance validation that's automatically integrated into your deployment pipeline!
