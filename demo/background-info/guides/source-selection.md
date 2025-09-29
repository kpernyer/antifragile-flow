# Source Selection Strategy: Hybrid Phased Approach

## Overview

This document outlines our comprehensive strategy for selecting and managing intelligence sources for the Living Twin AI agents. We use a hybrid approach that combines curated sources with LLM-guided discovery and premium integrations.

## 🎯 **Strategy Summary**

**Approach**: Hybrid system with three phases
- **Phase 1**: Curated foundation sources (immediate)
- **Phase 2**: LLM-guided source discovery (deployment)
- **Phase 3**: Premium source integration (scale)

**Benefits**:
- ✅ Proven reliability with working sources
- ✅ Cost-effective scaling from free to premium
- ✅ Intelligent adaptation to tenant needs
- ✅ Flexible architecture for easy expansion

---

## 📊 **Phase 1: Curated Foundation Sources (Immediate)**

### **Current Working Sources**

#### **Free Tier Sources**
| Source | URL | Category | Coverage | Keywords |
|--------|-----|----------|----------|----------|
| **TechCrunch** | https://techcrunch.com | News | Startups, tech, AI, funding | startup, funding, AI, technology |
| **The Verge** | https://www.theverge.com | News | Tech, AI, consumer, policy | technology, AI, policy, consumer |
| **Wired** | https://www.wired.com | News | Tech, AI, cybersecurity, business | technology, AI, cybersecurity, business |
| **AI News** | https://artificialintelligence-news.com | News | AI, ML, deep learning | AI, artificial intelligence, machine learning |
| **ZDNet** | https://www.zdnet.com | News | Enterprise, tech, business, security | enterprise, technology, business, security |

#### **Low-Cost Tier Sources**
| Source | URL | Category | Coverage | Cost |
|--------|-----|----------|----------|------|
| **MIT Technology Review** | https://www.technologyreview.com | Research | AI, technology, research, innovation | Low |
| **CIO.com** | https://www.cio.com | News | Enterprise, IT, digital transformation | Free |
| **Crunchbase** | https://www.crunchbase.com | Competitive | Startups, funding, investments | Medium |
| **AngelList** | https://angel.co | Competitive | Startups, jobs, investments | Free |

### **Source Characteristics**
- **Update Frequency**: Real-time to daily
- **Access Method**: Web scraping, RSS feeds
- **Rate Limits**: 10-30 requests/minute
- **Content Quality**: High relevance, good sentiment analysis
- **Coverage**: Technology, AI, startups, enterprise

---

## 🤖 **Phase 2: LLM-Guided Source Discovery (Deployment)**

### **Implementation**

When a new tenant is onboarded, the system uses LLM to recommend industry-specific sources:

```python
# LLM Prompt for Source Discovery
prompt = f"""
You are a strategic intelligence expert. Recommend 5-10 high-quality sources for monitoring
{industry} industry with focus on {strategic_focus}.

Budget tier: {budget_tier}

For each source, provide:
- name: Source name
- url: Website URL
- category: news/research/financial/social/competitive
- relevance_score: 0.0-1.0
- cost_tier: free/low/medium/high
- update_frequency: real_time/daily/weekly/monthly
- coverage_areas: List of topics covered
- description: Brief description
- recommended_keywords: List of keywords to monitor

Focus on sources that provide:
1. Industry-specific news and analysis
2. Competitive intelligence
3. Market research and trends
4. Financial performance data
5. Regulatory and policy updates

Return as JSON array of source objects.
"""
```

### **Industry-Specific Recommendations**

#### **Fintech Companies**
- **CoinDesk** - Cryptocurrency and blockchain news
- **Finextra** - Financial technology news
- **American Banker** - Banking industry insights
- **PaymentsSource** - Payment industry coverage

#### **Healthcare Technology**
- **Healthcare IT News** - Healthcare technology
- **MedCity News** - Healthcare innovation
- **FierceBiotech** - Biotechnology news
- **HealthTech Magazine** - Health technology trends

#### **Manufacturing**
- **IndustryWeek** - Manufacturing industry news
- **Manufacturing Today** - Manufacturing insights
- **Automation World** - Industrial automation
- **Plant Engineering** - Plant operations

### **Source Discovery Process**
1. **Tenant Onboarding**: Industry + strategic focus + budget tier
2. **LLM Analysis**: Generate source recommendations
3. **Source Validation**: Check availability and access methods
4. **Agent Configuration**: Create agents with discovered sources
5. **Performance Monitoring**: Track source effectiveness

---

## 💎 **Phase 3: Premium Source Integration (Scale)**

### **Perplexity's High-Impact Sources**

#### **Industry News & Analysis Platforms**
| Source | Type | Coverage | Cost |
|--------|------|----------|------|
| **Moody's NewsEdge** | News | Industry news, strategic moves | High |
| **Dow Jones Factiva** | News | Comprehensive business news | High |
| **LexisNexis** | Research | Legal and business research | High |

#### **Market Research Reports**
| Source | Type | Coverage | Cost |
|--------|------|----------|------|
| **Gartner** | Research | IT market research, trends | High |
| **Forrester** | Research | Technology and business insights | High |
| **IDC** | Research | Market size, forecasts | High |

#### **Competitive Intelligence Tools**
| Source | Type | Coverage | Cost |
|--------|------|----------|------|
| **SimilarWeb** | Competitive | Web traffic, digital presence | Medium |
| **SEMrush** | Competitive | SEO, marketing intelligence | Medium |
| **Kompyte** | Competitive | Competitor tracking | Medium |
| **AlphaSense** | Financial | Financial documents, earnings | High |

#### **Financial Performance Data**
| Source | Type | Coverage | Cost |
|--------|------|----------|------|
| **SEC Filings** | Financial | Public company data | Free |
| **Annual Reports** | Financial | Company performance | Free |
| **Investor Presentations** | Financial | Strategic insights | Free |

### **Integration Strategy**
1. **Budget-Based Access**: Premium sources based on tenant subscription tier
2. **API Integration**: Direct API access for real-time data
3. **Data Enrichment**: Combine premium data with web-scraped content
4. **Advanced Analytics**: Enhanced insights from premium sources

---

## 🔧 **Technical Implementation**

### **Source Discovery Service**

```python
class SourceDiscoveryService:
    """Intelligent source discovery for AI agents."""

    def __init__(self, llm_service):
        self.llm_service = llm_service
        self.curated_sources = {...}  # Phase 1 sources
        self.tenant_sources_cache = {}

    async def discover_sources_for_tenant(
        self,
        tenant_id: str,
        industry: str,
        strategic_focus: List[str],
        budget_tier: str = "low"
    ) -> List[SourceRecommendation]:
        """Discover relevant sources for a specific tenant."""

        # 1. Check cache
        # 2. Get LLM recommendations
        # 3. Combine with curated sources
        # 4. Rank and filter by budget
        # 5. Cache results
```

### **Agent Configuration**

```python
# Example agent configuration with discovered sources
agent_config = AgentConfig(
    keywords=["AI", "machine learning", "startup funding"],
    sources=["https://techcrunch.com", "https://artificialintelligence-news.com"],
    update_frequency_minutes=60,
    max_results_per_update=10,
    isolation_mode=False,
)
```

### **Source Ranking Algorithm**

```python
def _calculate_strategic_alignment_score(
    self,
    source: SourceRecommendation,
    strategic_focus: List[str]
) -> float:
    """Calculate how well a source aligns with strategic focus."""

    score = source.relevance_score

    # Bonus for coverage area overlap
    overlap = len(set(focus_lower) & set(coverage_lower))
    if overlap > 0:
        score += overlap * 0.1

    # Bonus for real-time updates
    if source.update_frequency == "real_time":
        score += 0.1

    # Bonus for API availability
    if source.api_available:
        score += 0.2

    return min(1.0, score)
```

---

## 📈 **Performance Metrics**

### **Source Effectiveness Tracking**
- **Relevance Score**: How well content matches keywords
- **Update Frequency**: How often new content is found
- **Content Quality**: Sentiment analysis, readability scores
- **Cost Efficiency**: Cost per relevant article found

### **Tenant-Specific Metrics**
- **Strategic Alignment**: How well sources match tenant focus
- **Coverage Gaps**: Missing areas that need additional sources
- **Budget Utilization**: Cost vs. value of sources used

---

## 🚀 **Deployment Roadmap**

### **Phase 1: Foundation (Current)**
- ✅ Curated sources implemented
- ✅ Source discovery service created
- ✅ Agent integration working
- ✅ Basic ranking and filtering

### **Phase 2: Intelligence (Next)**
- 🔄 LLM-guided source discovery
- 🔄 Industry-specific source databases
- 🔄 Advanced source ranking
- 🔄 Performance monitoring

### **Phase 3: Premium (Scale)**
- 📋 Premium source integration
- 📋 API-based data collection
- 📋 Advanced analytics
- 📋 Multi-tier pricing

---

## 💡 **Best Practices**

### **Source Selection**
1. **Start with proven sources**: Use our curated list as foundation
2. **Validate before adding**: Test new sources before production use
3. **Monitor performance**: Track source effectiveness regularly
4. **Respect rate limits**: Implement proper rate limiting for each source

### **Content Quality**
1. **Relevance filtering**: Only process content that matches keywords
2. **Sentiment analysis**: Track positive/negative/neutral sentiment
3. **Entity extraction**: Identify companies, products, technologies
4. **Theme detection**: Categorize content by themes

### **Cost Management**
1. **Budget-aware filtering**: Respect tenant budget constraints
2. **Efficient scraping**: Minimize requests while maximizing coverage
3. **Caching**: Cache source recommendations and content
4. **Performance monitoring**: Track cost per relevant article

---

## 🔍 **Monitoring & Maintenance**

### **Regular Tasks**
- **Weekly**: Review source performance metrics
- **Monthly**: Update curated source list
- **Quarterly**: Evaluate premium source ROI
- **Annually**: Comprehensive source strategy review

### **Alert Conditions**
- Source availability drops below 90%
- Content quality scores decline
- Rate limiting issues increase
- Cost per article exceeds thresholds

---

## 📚 **References**

### **Perplexity's Recommendations**
- Industry News: Moody's NewsEdge, Dow Jones Factiva, LexisNexis
- Market Research: Gartner, Forrester, IDC
- Competitive Intelligence: SimilarWeb, SEMrush, Kompyte, AlphaSense
- Financial Data: SEC filings, annual reports, investor presentations

### **Our Curated Sources**
- **TechCrunch**: Startup ecosystem and funding news
- **AI News**: Dedicated AI and machine learning coverage
- **MIT Technology Review**: Research and innovation insights
- **CIO.com**: Enterprise technology leadership
- **ZDNet**: Business technology news

---

*Last Updated: December 2024*
*Status: Phase 1 Complete, Phase 2 In Progress*

---

## 🎯 **Strategic Signal Detection & Knowledge Curation Framework**

### **Overview**

This section outlines our expert framework for identifying, extracting, and processing strategic signals from intelligence sources. The goal is to transform raw data into actionable strategic insights that impact organizational decision-making.

---

## 1. **What Are We Looking For?**

### **Strategic Signals Definition**

Focus extraction on **Strategic Signals**—events, trends, or data points with potential impact on your vision, mission, goals, or SWOT profile.

#### **Key Signal Categories**
- **Market disruptions** - New entrants, business model changes
- **Emerging technologies** - Breakthrough innovations, adoption trends
- **Regulatory shifts** - Policy changes, compliance requirements
- **Competitive moves** - Product launches, acquisitions, strategic pivots
- **Major economic changes** - Market conditions, funding environment
- **Customer preference shifts** - Behavior changes, demand patterns
- **Demographic changes** - Workforce trends, market composition

#### **Strategic Framework Mapping**
Each signal should be mapped against strategic frameworks:
- **SWOT Analysis** (Strengths, Weaknesses, Opportunities, Threats)
- **Porter's Five Forces** (Competition, new entrants, substitutes, suppliers, buyers)
- **McKinsey 7S** (Strategy, Structure, Systems, Shared Values, Skills, Style, Staff)

**Purpose**: Determine if a signal is actionable or merely interesting.

---

## 2. **What to Extract, How to Score and Connect Data**

### **a. Signal Identification: Similarity & Linking**

#### **Semantic Similarity Scoring**
```python
# Example implementation
def calculate_signal_similarity(signal1, signal2, threshold=0.8):
    """Calculate semantic similarity between two signals."""
    embedding1 = embed_text(signal1.content)
    embedding2 = embed_text(signal2.content)
    similarity = cosine_similarity(embedding1, embedding2)
    return similarity > threshold
```

#### **Clustering Strategy**
- **Topic Clustering**: Group similar signals by semantic similarity
- **Temporal Clustering**: Group signals by time proximity
- **Source Clustering**: Group signals by source credibility
- **Impact Clustering**: Group signals by potential strategic impact

#### **Strategic Categorization**
```python
# Map signals to strategic frameworks
strategic_categories = {
    "swot": ["strengths", "weaknesses", "opportunities", "threats"],
    "porters": ["competition", "new_entrants", "substitutes", "suppliers", "buyers"],
    "mckinsey_7s": ["strategy", "structure", "systems", "shared_values", "skills", "style", "staff"]
}
```

### **b. Signal Strengthening**

#### **Frequency of Mention**
- **Independent Sources**: Multiple sources reporting the same signal
- **Cross-Platform Validation**: Same signal across different media types
- **Geographic Distribution**: Signal appearing in multiple regions
- **Industry Spread**: Signal relevant across multiple industries

#### **Source Quality Weighting**
```python
source_credibility_scores = {
    "government": 1.0,
    "academic": 0.9,
    "industry_report": 0.8,
    "major_news": 0.7,
    "specialist_blog": 0.5,
    "social_media": 0.3
}
```

#### **Recency Scoring**
- **Immediate Impact**: Signals from last 24-48 hours
- **Short-term**: Signals from last week
- **Medium-term**: Signals from last month
- **Long-term**: Persistent signals over months

#### **Sentiment Analysis Integration**
```python
sentiment_impact_scores = {
    "urgent_negative": 1.0,    # Immediate threat
    "urgent_positive": 0.9,    # Immediate opportunity
    "negative": 0.7,           # General threat
    "positive": 0.6,           # General opportunity
    "neutral": 0.5,            # Informational
    "mixed": 0.4               # Uncertain impact
}
```

### **c. Hot List and Evolution Over Time**

#### **Hot List Algorithm**
```python
def calculate_hot_list_score(signal):
    """Calculate hot list score for signal ranking."""
    base_score = signal.relevance_score

    # Frequency bonus
    frequency_bonus = min(signal.mention_count / 10, 0.3)

    # Recency bonus
    hours_old = (datetime.now() - signal.first_seen).total_seconds() / 3600
    recency_bonus = max(0, 0.2 - (hours_old / 24) * 0.1)

    # Source quality bonus
    source_bonus = signal.source_credibility * 0.2

    # Sentiment bonus
    sentiment_bonus = signal.sentiment_impact_score * 0.1

    return base_score + frequency_bonus + recency_bonus + source_bonus + sentiment_bonus
```

#### **Time-Series Tracking**
- **Signal Evolution**: Track how signals change over time
- **Trend Detection**: Identify emerging patterns
- **Signal Decay**: Monitor when signals lose relevance
- **Correlation Analysis**: Find relationships between different signals

---

## 3. **What Else Should You Store?**

### **Data Storage Strategy**

#### **Raw Data & Extracted Features**
```python
signal_data_structure = {
    "raw_content": "Full article text",
    "summary": "AI-generated summary",
    "entities": ["companies", "people", "technologies"],
    "keywords": ["extracted", "relevant", "terms"],
    "topics": ["categorized", "themes"],
    "similarity_scores": {"signal_id": 0.85},
    "sentiment": {"score": 0.7, "label": "positive"},
    "timestamp": "2024-12-19T10:30:00Z",
    "source_metadata": {
        "url": "https://example.com/article",
        "domain": "example.com",
        "credibility": 0.8
    }
}
```

#### **Relationships Between Signals**
```python
# Graph structure for signal relationships
signal_relationships = {
    "co_occurrence": ["signal_a", "signal_b"],  # Signals mentioned together
    "similarity": {"signal_a": 0.85, "signal_b": 0.92},  # Semantic similarity
    "temporal": {"signal_a": "2024-12-19", "signal_b": "2024-12-20"},  # Time proximity
    "causal": {"signal_a": "causes", "signal_b": "effect"}  # Cause-effect relationships
}
```

#### **Counter-Signals Tracking**
- **Contradicting Information**: Track signals that contradict each other
- **Confidence Scoring**: Assess reliability of conflicting signals
- **Resolution Tracking**: Monitor how contradictions are resolved over time

---

## 4. **System Onboarding Process**

### **Strategic Foundation Setup**

#### **Required Inputs**
1. **SWOT Analysis**: Strengths, Weaknesses, Opportunities, Threats
2. **Porter's Five Forces**: Industry structure analysis
3. **McKinsey 7S**: Organizational framework
4. **Strategic Goals**: Short-term and long-term objectives
5. **Risk Tolerance**: How aggressive to be with signal detection

#### **Onboarding Workflow**
```python
def setup_strategic_framework(tenant_id, strategic_data):
    """Set up strategic framework for signal detection."""

    # 1. Validate strategic inputs
    validate_swot_analysis(strategic_data["swot"])
    validate_porters_analysis(strategic_data["porters"])
    validate_7s_framework(strategic_data["mckinsey_7s"])

    # 2. Create signal detection rules
    create_signal_rules(strategic_data)

    # 3. Set up monitoring categories
    setup_monitoring_categories(strategic_data)

    # 4. Initialize hot list
    initialize_hot_list(tenant_id)

    # 5. Configure alert thresholds
    configure_alert_thresholds(strategic_data["risk_tolerance"])
```

### **Signal Filtering & Categorization**

#### **Automated Categorization**
```python
def categorize_signal(signal, strategic_framework):
    """Categorize signal according to strategic frameworks."""

    categories = {
        "swot": [],
        "porters": [],
        "mckinsey_7s": []
    }

    # Analyze signal content against each framework
    for framework, elements in strategic_framework.items():
        for element in elements:
            if element_relevance_score(signal, element) > 0.7:
                categories[framework].append(element)

    return categories
```

---

## 5. **Strategic Takeaways**

### **Automation Strategy**

#### **AI Agent Responsibilities**
- **Similarity Scoring**: Calculate semantic similarity between signals
- **Frequency Analysis**: Track mention frequency across sources
- **Sentiment Analysis**: Analyze tone and urgency
- **Source Credibility**: Assess source reliability
- **Trend Detection**: Identify emerging patterns

#### **Human + Machine Judgment**
```python
def human_override_system(signal_id, user_action, user_role):
    """Allow human override of machine-generated scores."""

    override_weight = {
        "executive": 1.0,      # Full override authority
        "manager": 0.8,        # High override authority
        "analyst": 0.6,        # Moderate override authority
        "viewer": 0.2          # Limited override authority
    }

    weight = override_weight.get(user_role, 0.5)

    if user_action == "upvote":
        signal.score *= (1 + weight)
    elif user_action == "downvote":
        signal.score *= (1 - weight)

    log_human_override(signal_id, user_action, user_role, weight)
```

### **Continuous Improvement**

#### **Regular Reviews**
- **Weekly**: Review hot list and signal performance
- **Monthly**: Update strategic frameworks and detection rules
- **Quarterly**: Evaluate signal detection accuracy and relevance
- **Annually**: Comprehensive strategic framework refresh

#### **Visualization & Reporting**
```python
def generate_strategic_dashboard(tenant_id, timeframe="30d"):
    """Generate strategic intelligence dashboard."""

    return {
        "hot_list": get_hot_list(tenant_id, limit=20),
        "signal_evolution": get_signal_evolution(tenant_id, timeframe),
        "category_distribution": get_category_distribution(tenant_id),
        "source_effectiveness": get_source_effectiveness(tenant_id),
        "trend_analysis": get_trend_analysis(tenant_id, timeframe),
        "alert_summary": get_alert_summary(tenant_id, timeframe)
    }
```

---

## 6. **Implementation Roadmap**

### **Phase 1: Foundation (Current)**
- ✅ Basic signal detection and storage
- ✅ Source integration and content analysis
- 🔄 Strategic framework mapping
- 📋 Hot list algorithm implementation

### **Phase 2: Intelligence (Next)**
- 📋 Advanced similarity scoring
- 📋 Human override system
- 📋 Signal evolution tracking
- 📋 Dashboard and visualization

### **Phase 3: Optimization (Scale)**
- 📋 Machine learning signal prediction
- 📋 Advanced trend detection
- 📋 Automated strategic recommendations
- 📋 Cross-tenant signal correlation

---

## 7. **Success Metrics**

### **Signal Quality Metrics**
- **Relevance Score**: How well signals match strategic frameworks
- **Accuracy Rate**: Percentage of signals that prove actionable
- **Response Time**: Time from signal detection to action
- **Coverage Gaps**: Areas where signal detection is weak

### **Strategic Impact Metrics**
- **Decision Influence**: How often signals influence decisions
- **Risk Mitigation**: Number of threats identified early
- **Opportunity Capture**: Number of opportunities identified
- **Strategic Alignment**: How well signals align with goals

---

*This framework ensures your Organizational Twin spots, amplifies, and acts on truly strategic signals, not just noise.*
