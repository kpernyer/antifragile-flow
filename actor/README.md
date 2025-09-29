# 👥 Actor Personas

Actor personas represent the human participants in the organizational twin system. Each persona has distinct behavior patterns, decision-making styles, and interaction preferences that drive realistic human-AI collaboration scenarios.

## 📁 Actor Structure

Each actor follows a consistent structure:
```
persona_name/
├── persona.py          # Persona definition and behavior model
├── starter.py          # Workflow starters and interaction triggers
├── run_persona.sh     # Demo runner script
└── README.md          # Persona documentation
```

## 👥 Available Personas

### 👨‍💼 CEO (Chief Executive Officer) ✅ IMPLEMENTED
**Name**: Mary
**Implementation**: `ceo/starter.py` - Interactive strategic priority selection
**Features**:
- 5 predefined strategic priorities with urgency levels
- Interactive workflow initiation via Temporal
- Connects to StrategicDecisionWorkflow
- Real-time status monitoring

**Usage**:
```bash
cd actor/ceo
python starter.py  # Interactive priority selection
```

### 👩‍💻 VP Engineering ⏳ PLANNED
**Name**: Isac
**Status**: Architecture defined in shared utilities, implementation pending

### 💼 VP Sales ⏳ PLANNED
**Name**: John
**Status**: Architecture defined in shared utilities, implementation pending

### ⚖️ VP Legal ⏳ PLANNED
**Name**: Priya
**Status**: Architecture defined in shared utilities, implementation pending

### 🔧 Shared Utilities ✅ AVAILABLE
**Purpose**: Common persona patterns and interaction frameworks
**Implementation**: Complete base classes and utilities available in `shared/`
- `base_persona.py` - Base persona behavior patterns
- `user_client.py` - Client interface for persona interactions
- `user_profiles.py` - Persona profile definitions

## 🚧 Implementation Status

**Currently Available:**
- ✅ CEO persona with strategic priority workflow integration
- ✅ Base persona architecture and shared utilities
- ✅ Temporal workflow integration patterns

**Planned Features:**
- ⏳ VP Engineering persona implementation
- ⏳ VP Sales persona implementation
- ⏳ VP Legal persona implementation
- ⏳ Multi-persona consensus workflows
- ⏳ Crisis response scenarios
- ⏳ Quarterly planning simulations

The architecture and patterns are established - additional personas follow the same implementation approach as the CEO persona.

## 🚀 Running Actor Personas

### Start CEO Persona (Currently Available)
```bash
cd actor/ceo
python starter.py  # Interactive strategic priority selection
```

### Alternative CEO Mode (User Client Integration)
```bash
cd actor/ceo
./run_ceo.sh Mary  # Uses shared user_client.py
```

### Future Personas (Implementation Pending)
Other personas will follow similar patterns once implemented.

## 🎭 Persona Behavior Modeling

### 1. **Decision-Making Style**
```python
@dataclass
class CEOPersona:
    name: str = "Mary"
    decision_style: str = "strategic"
    risk_tolerance: float = 0.7  # High risk tolerance
    response_time: timedelta = timedelta(hours=2)  # Quick responses

    def generate_response(self, context: DecisionContext) -> str:
        if context.urgency == "high":
            return self._quick_strategic_response(context)
        return self._thoughtful_strategic_response(context)
```

### 2. **Communication Patterns**
```python
class VPEngineeringPersona:
    def format_response(self, decision: str, reasoning: str) -> str:
        return f"""
        Technical Analysis: {reasoning}

        Recommendation: {decision}

        Key Considerations:
        - System impact assessment needed
        - Resource allocation implications
        - Technical risk factors

        Next Steps: Suggest architecture review
        """
```

### 3. **Interaction Triggers**
```python
class PersonaStarter:
    async def daily_check_in(self):
        """Simulate daily persona activities"""
        priorities = await self.get_daily_priorities()

        for priority in priorities:
            if priority.requires_decision:
                await self.start_decision_workflow(priority)
            elif priority.needs_research:
                await self.request_research(priority.topic)
```

## 🎯 Demo Scenarios

### 1. **Strategic Decision Making**
```bash
# CEO initiates strategic decision
cd actors/ceo && python starter.py --scenario strategic_decision \
  --decision "acquire_techcorp" \
  --context "expand_ai_capabilities"
```

### 2. **Consensus Building**
```bash
# Multi-persona consensus scenario
cd actors && ./run_consensus_demo.sh \
  --participants "ceo,vp_engineering,vp_sales,vp_legal" \
  --topic "new_product_launch"
```

### 3. **Crisis Response**
```bash
# Simulate urgent response scenario
cd actors && ./run_crisis_demo.sh \
  --incident "security_breach" \
  --severity "high"
```

## 🏗️ Creating New Personas

### 1. **Define Persona Characteristics**
```python
# personas/new_role/persona.py
@dataclass
class NewRolePersona:
    name: str = "Alex"
    role: str = "VP Marketing"
    decision_style: str = "collaborative"
    communication_style: str = "persuasive"
    priorities: List[str] = field(default_factory=lambda: [
        "brand_awareness", "customer_acquisition", "market_positioning"
    ])

    def get_response_style(self, context: str) -> str:
        """Generate role-appropriate response patterns"""
        return f"From a marketing perspective, focusing on {context}..."
```

### 2. **Implement Behavior Patterns**
```python
class NewRoleStarter:
    def __init__(self, persona: NewRolePersona):
        self.persona = persona
        self.client = get_temporal_client()

    async def evaluate_market_opportunity(self, opportunity: dict):
        """Role-specific workflow triggers"""
        await self.client.start_workflow(
            "MarketAnalysisWorkflow",
            {
                "opportunity": opportunity,
                "evaluator": self.persona.name,
                "focus_areas": self.persona.priorities
            }
        )
```

### 3. **Create Demo Scripts**
```bash
# personas/new_role/run_new_role.sh
#!/bin/bash
echo "Starting VP Marketing persona demo..."
python starter.py --persona vp_marketing --mode interactive
```

## 🎪 Demo Integration

### Multi-Persona Workflows
```python
class OrgSimulation:
    def __init__(self):
        self.personas = {
            "ceo": CEOPersona(),
            "vp_eng": VPEngineeringPersona(),
            "vp_sales": VPSalesPersona(),
            "vp_legal": VPLegalPersona()
        }

    async def simulate_quarterly_planning(self):
        """Orchestrate multi-persona planning session"""
        # CEO sets strategic direction
        strategy = await self.personas["ceo"].set_quarterly_strategy()

        # VPs provide input in parallel
        responses = await asyncio.gather(
            self.personas["vp_eng"].evaluate_strategy(strategy),
            self.personas["vp_sales"].evaluate_strategy(strategy),
            self.personas["vp_legal"].evaluate_strategy(strategy)
        )

        # CEO makes final decisions
        return await self.personas["ceo"].finalize_strategy(responses)
```

## 🧪 Testing Personas

### Behavior Testing
```python
def test_ceo_decision_style():
    ceo = CEOPersona()
    context = DecisionContext(
        topic="market_expansion",
        urgency="medium",
        data_available=True
    )

    response = ceo.generate_response(context)

    assert "strategic" in response.lower()
    assert response.includes_risk_assessment()
```

### Interaction Testing
```python
async def test_consensus_building():
    participants = [CEOPersona(), VPEngineeringPersona()]
    decision = "implement_new_architecture"

    consensus = await simulate_consensus(participants, decision)

    assert consensus.has_all_responses()
    assert consensus.ceo_final_decision is not None
```

## 🔄 Best Practices

- **Realistic Behavior**: Model actual executive behavior patterns
- **Consistent Personality**: Maintain persona consistency across interactions
- **Domain Expertise**: Each persona should reflect their functional expertise
- **Interaction Patterns**: Design realistic multi-persona dynamics
- **Demo Value**: Create compelling scenarios that showcase system capabilities
- **Extensibility**: Design for easy addition of new personas and scenarios
- **Documentation**: Clear persona profiles and behavior explanations
