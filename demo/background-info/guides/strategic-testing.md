# Strategic Signal Detection: Complete Test Guide

## 🚀 **Immediate Round-Trip Testing**

This guide provides everything you need to test the SWOT + Porter's Five Forces signal detection system with real data immediately. The system now uses **YAML files** organized in a **hierarchical graph structure** for test data, making it easy to modify scenarios without touching code.

---

## 📋 **Quick Start: Test the Complete System**

### **1. Start the API Server**

```bash
cd apps/api
uvicorn app.main:app --reload --port 8000
```

### **2. View Available Test Scenarios**

```bash
# See what test scenarios are available
curl -X GET "http://localhost:8000/strategic-test/scenarios" \
  -H "Authorization: Bearer dev-token"
```

### **3. Test the Complete Round-Trip**

```bash
# Test the entire pipeline: setup → signal detection → analysis
curl -X POST "http://localhost:8000/strategic-test/round-trip" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-token"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Complete round-trip test successful",
  "data": {
    "setup": {
      "swot_elements": 16,
      "porters_elements": 12
    },
    "keyword_generation": {
      "strategic_keywords": 50,
      "sample_keywords": ["AI security", "market share", "emerging markets", "Apple Pay", "regulation", "partnership", "fintech", "digital payments", "competitive advantage", "innovation"]
    },
    "signal_detection": {
      "agent_results_processed": 8,
      "strategic_signals_detected": 7,
      "detection_rate": 0.875
    },
    "signal_analysis": {
      "analyses_created": 7,
      "average_implications": 2.3,
      "average_actions": 3.1
    },
    "performance": {
      "execution_time_ms": 245.6,
      "signals_per_second": 28.5
    }
  },
  "execution_time_ms": 245.6
}
```

---

## 🔍 **Individual Component Testing**

### **1. Test Data Setup**

```bash
# Setup with fintech scenario (default)
curl -X POST "http://localhost:8000/strategic-test/setup" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-token" \
  -d '{
    "tenant_id": "demo",
    "user_id": "dev",
    "industry": "fintech",
    "test_scenario": "fintech"
  }'

# Setup with healthcare scenario
curl -X POST "http://localhost:8000/strategic-test/setup" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-token" \
  -d '{
    "tenant_id": "demo",
    "user_id": "dev",
    "industry": "healthcare",
    "test_scenario": "healthcare"
  }'
```

### **2. Test Signal Detection**

```bash
curl -X POST "http://localhost:8000/strategic-test/signal-detection" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-token" \
  -d '{
    "tenant_id": "demo",
    "swot_analysis_id": "swot-123",
    "porters_analysis_id": "porters-123",
    "test_agent_results": true
  }'
```

### **3. View Test Sources**

```bash
curl -X GET "http://localhost:8000/strategic-test/sources" \
  -H "Authorization: Bearer dev-token"
```

### **4. View Test Agent Results**

```bash
curl -X GET "http://localhost:8000/strategic-test/agent-results" \
  -H "Authorization: Bearer dev-token"
```

---

## 📊 **Test Data Overview**

### **YAML File Structure**

The test data is now stored in YAML files for easy modification:

```
apps/api/app/data/test_scenarios/
├── fintech_swot.yaml          # Fintech SWOT analysis
├── fintech_porters.yaml       # Fintech Porter's analysis
├── healthcare_swot.yaml       # Healthcare SWOT analysis
├── test_agent_results.yaml    # Test news articles
└── strategic_sources.yaml     # Source configurations
```

**Benefits of YAML approach:**
- ✅ **Easy to modify** - No code changes needed
- ✅ **Version controlled** - Changes tracked in git
- ✅ **Business friendly** - Non-technical users can edit
- ✅ **Reusable** - Multiple test scenarios
- ✅ **Structured** - Clear data organization

### **SWOT Analysis (4x4 Structure)**

**Strengths (Priority 1-4):**
1. **AI-Powered Security** (Priority 1) - Advanced ML fraud detection
2. **User Experience Design** (Priority 2) - 4.8-star app rating
3. **Agile Development** (Priority 3) - 2-week sprint cycles
4. **Regulatory Compliance** (Priority 4) - PCI DSS, GDPR compliance

**Weaknesses (Priority 1-4):**
1. **Limited Market Share** (Priority 1) - Only 2% market share
2. **Brand Recognition** (Priority 2) - Low awareness vs Apple Pay
3. **Funding Constraints** (Priority 3) - Limited capital for expansion
4. **Geographic Concentration** (Priority 4) - Over-reliance on North America

**Opportunities (Priority 1-4):**
1. **Emerging Markets** (Priority 1) - Southeast Asia, Latin America
2. **Partnership Opportunities** (Priority 2) - Banks and retailers
3. **AI Innovation** (Priority 3) - Lead in AI financial services
4. **Regulatory Changes** (Priority 4) - Open banking opportunities

**Threats (Priority 1-4):**
1. **Big Tech Competition** (Priority 1) - Apple Pay, Google Pay, Amazon
2. **Regulatory Changes** (Priority 2) - Increasing compliance requirements
3. **Cybersecurity Threats** (Priority 3) - Sophisticated cyber attacks
4. **Economic Downturn** (Priority 4) - Recession impact on spending

### **Porter's Five Forces Analysis**

**Competitive Rivalry:**
- Big Tech Dominance (Apple Pay, Google Pay - 85% market share)
- Traditional Banks (Major banks launching digital solutions)
- Startup Competition (Numerous fintech startups)

**New Entrants:**
- Tech Giants (Amazon, Meta entering payments)
- International Players (Alipay, WeChat Pay expanding)

**Substitute Products:**
- Cryptocurrency Payments (Bitcoin, Ethereum, stablecoins)
- Traditional Payment Methods (Cash, credit cards, bank transfers)

**Supplier Power:**
- Payment Processors (Stripe, Square controlling infrastructure)
- Cloud Providers (AWS, Google Cloud, Azure)

**Buyer Power:**
- Large Merchants (Walmart, Amazon have bargaining power)
- Consumer Choice (Multiple payment options, low switching costs)

---

## 📰 **Test Agent Results**

The system includes 8 realistic test agent results:

1. **"Apple Pay Expands to 15 New Countries"** - Threat signal
2. **"New AI Security Regulations Proposed"** - Threat + Weakness signal
3. **"Digital Payment Adoption Soars in Emerging Markets"** - Opportunity signal
4. **"Stripe Raises Processing Fees"** - Threat signal (supplier power)
5. **"South Korea's Digital Payment Market Grows 60%"** - Opportunity signal
6. **"Amazon Launches New Payment Service"** - Threat signal (new entrant)
7. **"Open Banking Regulations Take Effect in Europe"** - Opportunity signal
8. **"Major Data Breach Affects Payment Processors"** - Threat signal (cybersecurity)

---

## 🎯 **Expected Signal Detection Results**

### **Signal Distribution**
- **Total Signals**: 7-8 (from 8 agent results)
- **Detection Rate**: ~87.5%
- **Critical Priority**: 1-2 signals
- **High Priority**: 3-4 signals
- **Medium Priority**: 1-2 signals

### **SWOT Category Distribution**
- **Threats**: 4-5 signals (Big Tech, regulations, cybersecurity)
- **Opportunities**: 2-3 signals (Emerging markets, open banking)
- **Weaknesses**: 1-2 signals (Regulatory compliance)
- **Strengths**: 0-1 signals

### **Impact Direction Distribution**
- **Negative**: 4-5 signals (threats and challenges)
- **Positive**: 2-3 signals (opportunities and growth)
- **Neutral**: 0-1 signals

---

## 🔧 **Strategic Sources by Update Frequency**

### **High Frequency (Real-time/Daily)**
- **TechCrunch** - Real-time tech news and startup coverage
- **Reuters Technology** - Real-time technology news and analysis
- **Financial Times Tech** - Daily technology and fintech coverage

### **Medium Frequency (Weekly)**
- **MIT Technology Review** - Weekly technology research and trends
- **Harvard Business Review** - Weekly business strategy and leadership insights
- **McKinsey Insights** - Weekly strategic insights and analysis

### **Low Frequency (Quarterly/Yearly)**
- **CIA World Factbook** - Annual geopolitical and demographic data
- **World Bank Data** - Quarterly economic and development data
- **UNESCO Statistics** - Annual demographic and cultural statistics

### **Megatrends (Monthly)**
- **Pew Research Center** - Monthly demographic and social trend analysis
- **Brookings Institution** - Weekly policy and economic trend analysis
- **World Economic Forum** - Monthly global trend analysis and future insights

---

## 📈 **Performance Benchmarks**

### **Expected Performance**
- **Setup Time**: < 100ms
- **Keyword Generation**: < 50ms
- **Signal Detection**: < 200ms
- **Signal Analysis**: < 100ms
- **Total Round-Trip**: < 500ms

### **Quality Metrics**
- **Signal Relevance**: > 85%
- **Detection Rate**: > 80%
- **Actionability**: > 90%
- **Strategic Alignment**: > 95%

---

## 🧪 **Advanced Testing Scenarios**

### **1. Test Different Industries**

```bash
# View available scenarios first
curl -X GET "http://localhost:8000/strategic-test/scenarios" \
  -H "Authorization: Bearer dev-token"

# Test with healthcare scenario
curl -X POST "http://localhost:8000/strategic-test/setup" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-token" \
  -d '{
    "tenant_id": "demo",
    "user_id": "dev",
    "industry": "healthcare",
    "test_scenario": "healthcare"
  }'

# Test with fintech scenario
curl -X POST "http://localhost:8000/strategic-test/setup" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-token" \
  -d '{
    "tenant_id": "demo",
    "user_id": "dev",
    "industry": "fintech",
    "test_scenario": "fintech"
  }'
```

### **2. Test Signal Evolution**

```bash
# Run multiple rounds to test signal evolution
for i in {1..5}; do
  echo "Round $i:"
  curl -X POST "http://localhost:8000/strategic-test/round-trip" \
    -H "Authorization: Bearer dev-token" | jq '.data.signal_detection'
  sleep 2
done
```

### **3. Test Performance Under Load**

```bash
# Test with multiple concurrent requests
for i in {1..10}; do
  curl -X POST "http://localhost:8000/strategic-test/round-trip" \
    -H "Authorization: Bearer dev-token" &
done
wait
```

---

## 🔍 **Debugging and Troubleshooting**

### **Common Issues**

1. **Import Errors**: Ensure all strategic modules are properly imported
2. **Authentication**: Use `Authorization: Bearer dev-token` for testing
3. **Performance**: Check execution times in response
4. **Signal Quality**: Review detection rates and relevance scores

### **Debug Endpoints**

```bash
# Check system health
curl -X GET "http://localhost:8000/healthz"

# View API documentation
open "http://localhost:8000/docs"
```

---

## 📊 **Success Criteria**

### **✅ Test Passes If:**

1. **Setup**: Creates SWOT (16 elements) + Porter's (12 elements) successfully
2. **Keyword Generation**: Generates 40-60 strategic keywords
3. **Signal Detection**: Detects 6-8 signals from 8 agent results (>75% rate)
4. **Signal Analysis**: Creates analyses with implications and actions
5. **Performance**: Complete round-trip < 500ms
6. **Quality**: High relevance and strategic alignment scores

### **🎯 Expected Signal Examples**

**Critical Signal:**
- "New AI Security Regulations Proposed" → Threat + Weakness → Critical Priority

**High Priority Signal:**
- "Apple Pay Expands to 15 New Countries" → Threat → High Priority

**Opportunity Signal:**
- "Digital Payment Adoption Soars in Emerging Markets" → Opportunity → High Priority

---

## 🚀 **Next Steps After Testing**

1. **Review Results**: Analyze signal quality and strategic relevance
2. **Modify Test Data**: Edit YAML files to test different scenarios
3. **Add New Scenarios**: Create new YAML files for different industries
4. **Tune Parameters**: Adjust thresholds and scoring algorithms
5. **Add Real Sources**: Integrate with actual news sources and APIs
6. **Scale Testing**: Test with larger datasets and multiple tenants
7. **Production Deployment**: Deploy to production environment

### **Creating New Test Scenarios**

To add a new industry scenario:

1. **Create SWOT YAML**: `apps/api/app/data/test_scenarios/{industry}_swot.yaml`
2. **Create Porter's YAML**: `apps/api/app/data/test_scenarios/{industry}_porters.yaml`
3. **Test the scenario**: Use the setup endpoint with your new scenario name

Example:
```bash
# After creating retail_swot.yaml and retail_porters.yaml
curl -X POST "http://localhost:8000/strategic-test/setup" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-token" \
  -d '{
    "tenant_id": "demo",
    "user_id": "dev",
    "industry": "retail",
    "test_scenario": "retail"
  }'
```

---

*This test system provides immediate validation of the SWOT + Porter's Five Forces signal detection capabilities with realistic data and comprehensive metrics.*
