# DNS Setup Guide for aprio.one

## 🌐 DNS Configuration for Living Twin on aprio.one

### **Step 1: Deploy Infrastructure**
```bash
# Initialize and deploy Google Cloud infrastructure
make setup-gcp-project
make terraform-init
make terraform-apply

# Get the load balancer IP address
make get-load-balancer-ip
```

### **Step 2: Configure DNS Records**

After running the Terraform deployment, you'll get a **Global Load Balancer IP address**. Configure these DNS records in your `aprio.one` domain registrar:

#### **Required A Records:**
```
dev.aprio.one      A    [LOAD_BALANCER_IP]
staging.aprio.one  A    [LOAD_BALANCER_IP]
```

#### **Optional CNAME Records:**
```
www.dev.aprio.one     CNAME  dev.aprio.one
api.aprio.one         CNAME  dev.aprio.one
```

### **Step 3: SSL Certificate Verification**

Google Cloud will automatically provision SSL certificates for:
- `dev.aprio.one`
- `staging.aprio.one`

**⏱️ Certificate provisioning takes 10-60 minutes after DNS propagation.**

### **Step 4: Verify DNS Propagation**

```bash
# Check DNS propagation
dig dev.aprio.one A
dig staging.aprio.one A

# Check SSL certificate (after 10+ minutes)
curl -I https://dev.aprio.one/api/healthz
```

## 🛠️ Domain Registrar Instructions

### **If using Google Domains:**
1. Go to [domains.google.com](https://domains.google.com)
2. Select your `aprio.one` domain
3. Go to "DNS" tab
4. Add the A records as shown above

### **If using Namecheap:**
1. Log in to Namecheap
2. Go to Domain List → Manage
3. Advanced DNS tab
4. Add A Records:
   - Host: `dev`, Value: `[LOAD_BALANCER_IP]`
   - Host: `staging`, Value: `[LOAD_BALANCER_IP]`

### **If using Cloudflare:**
1. Log in to Cloudflare Dashboard
2. Select `aprio.one` domain
3. DNS → Records
4. Add A records (set proxy status to "DNS only" initially)

## 🚀 Complete Deployment Workflow

### **Full Production Deployment:**
```bash
# 1. Deploy infrastructure and get IP
make terraform-apply
make get-load-balancer-ip

# 2. Update DNS records with the IP (manual step)
# → Configure A records in your domain registrar

# 3. Wait for DNS propagation (5-15 minutes)
dig dev.aprio.one A

# 4. Deploy services
make deploy-production

# 5. Test endpoints
curl https://dev.aprio.one/api/healthz
curl https://dev.aprio.one/api/docs
```

### **Individual Service Deployment:**
```bash
# Deploy API only
make deploy-api

# Deploy web app only
make deploy-web

# Deploy Firebase hosting
firebase deploy --only hosting
```

## 📋 DNS Configuration Checklist

- [ ] **GCP Project Setup**: `make setup-gcp-project`
- [ ] **Infrastructure Deployed**: `make terraform-apply`
- [ ] **Load Balancer IP Obtained**: `make get-load-balancer-ip`
- [ ] **DNS A Records Added**: `dev.aprio.one` and `staging.aprio.one`
- [ ] **DNS Propagation Verified**: `dig dev.aprio.one A`
- [ ] **SSL Certificate Active**: Check after 10+ minutes
- [ ] **Services Deployed**: `make deploy-production`
- [ ] **Health Check Passes**: `curl https://dev.aprio.one/api/healthz`

## 🔍 Troubleshooting

### **DNS Not Propagating:**
```bash
# Check multiple DNS servers
nslookup dev.aprio.one 8.8.8.8
nslookup dev.aprio.one 1.1.1.1

# Check TTL
dig dev.aprio.one A +noall +answer
```

### **SSL Certificate Issues:**
```bash
# Check certificate status
gcloud compute ssl-certificates describe living-twin-ssl-cert --global

# Force certificate renewal
gcloud compute ssl-certificates create living-twin-ssl-cert-new \
  --domains dev.aprio.one,staging.aprio.one \
  --global
```

### **Load Balancer Issues:**
```bash
# Check load balancer status
gcloud compute url-maps describe living-twin-url-map

# Check backend services
gcloud compute backend-services list
```

## 🌍 Geographic Considerations

- **Load Balancer**: Global (multi-region)
- **Cloud Run**: `us-central1` (configurable)
- **Redis**: `us-central1-a`
- **DNS**: Global propagation

## 📞 Support Commands

```bash
# Get all infrastructure status
gcloud compute addresses list --global
gcloud run services list --region=us-central1
gcloud compute ssl-certificates list --global

# Monitor deployment
gcloud builds list --limit=5
gcloud logging read "projects/living-twin-aprio/logs/run.googleapis.com" --limit=50
```

---

## 🎯 Final Architecture

```
Internet → DNS (aprio.one) → Google Load Balancer → Cloud Run Services
                                     ↓
┌─────────────────────────────────────────────────┐
│               dev.aprio.one                     │
│  ┌─────────────────┐  ┌─────────────────────┐   │
│  │  Cloud Run API  │  │  Firebase Hosting   │   │
│  │  (FastAPI)      │  │  (React Web App)    │   │
│  │  Port 8000      │  │  Static Files       │   │
│  └─────────────────┘  └─────────────────────┘   │
│            ↓                     ↓               │
│  ┌─────────────────┐  ┌─────────────────────┐   │
│  │  Redis          │  │  Firebase Auth      │   │
│  │  (Memorystore)  │  │  User Management    │   │
│  └─────────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────┘
```

**Ready to deploy your Living Twin infrastructure to `aprio.one`! 🚀**
