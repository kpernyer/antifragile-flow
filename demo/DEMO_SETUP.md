# Antifragile Flow - Multi-User Temporal Demo Setup

## Overview

A complete multi-user workflow demonstration system built on Temporal, featuring realistic organizational decision-making with human-in-the-loop interactions. Each user has detailed personality profiles that influence their behavior patterns and communication styles.

## 🏢 Demo Organization: Globex Industrial Group

### Users & Personalities

#### Mary O'Keefe - CEO
- **Profile**: Decisive leader, 15 years experience
- **Style**: Direct communicator, fast responder (~5 min), strategic focus
- **Traits**: High delegation, calculated risk tolerance, confrontational conflict handling
- **Philosophy**: "Empower teams, make fast decisions, focus on results"

#### John Appelkvist - VP of Sales
- **Profile**: Collaborative team player, 12 years experience
- **Style**: Diplomatic communicator, moderate responder (~15 min), customer-focused
- **Traits**: High agreement tendency, moderate delegation, high risk tolerance
- **Philosophy**: "Customer first, data-driven decisions, team empowerment"

#### Isac "Happy" Ironsmith - VP of Engineering
- **Profile**: Analytical deep-thinker, 18 years experience
- **Style**: Detailed communicator, slow responder (~45 min), questions assumptions
- **Traits**: Low agreement tendency, hands-on approach, low risk tolerance
- **Philosophy**: "Measure twice, cut once. Quality over speed. Technical excellence drives business."

#### Priya Sharma - VP of Legal
- **Profile**: Risk-focused analyst, 14 years experience
- **Style**: Diplomatic communicator, slow responder (~35 min), legal precision
- **Traits**: Natural skeptic, formal communication, looks for compliance issues
- **Philosophy**: "Prevent problems before they occur. Every decision has legal implications."

#### Bob Greenland - IT Admin
- **Profile**: Technical problem-solver, 10 years experience
- **Style**: Direct communicator, fast responder (~10 min), security-focused
- **Traits**: Hands-on approach, avoids politics, focuses on what works
- **Philosophy**: "Keep it simple, secure, and reliable. Users should never notice good IT."

## 🔄 Demo Workflows

### 1. Strategic Decision Workflow
**Scenario**: CEO proposes major business decision → VPs provide input → CEO makes final decision

**Flow**:
1. CEO (Mary) starts workflow with business proposal
2. All VPs (John, Isac, Priya) receive notification
3. Each VP provides decision + reasoning based on their expertise
4. CEO reviews all input and makes final decision
5. Workflow completes with full decision audit trail

**Example**: "Acquire TechCorp for $50M to expand our AI capabilities"

### 2. Competitor Analysis Workflow
**Scenario**: Sales reports competitive threat → Engineering + Legal analyze → CEO decides strategy

**Flow**:
1. VP Sales (John) reports competitor threat with details
2. VP Engineering (Isac) analyzes technical implications
3. VP Legal (Priya) analyzes legal/regulatory risks
4. CEO (Mary) reviews analyses and decides response strategy
5. Workflow completes with comprehensive competitive response plan

**Example**: "RivalTech Corp launched AI-powered product competing with our flagship"

## 🚀 Running the Demo

### Prerequisites
```bash
# Ensure you have:
- Temporal server running (localhost:7233)
- Python environment with uv
- All dependencies installed
```

### Step 1: Start Core Services
```bash
# Terminal 1 - Temporal Server
make temporal

# Terminal 2 - Worker
cd python/src && uv run worker.py
```

### Step 2: Launch Demo Workflows
```bash
# Start Strategic Decision Demo
cd python && echo "1" | uv run demo_runner.py

# OR Start Competitor Analysis Demo
cd python && echo "2" | uv run demo_runner.py
```

### Step 3: Open User Terminals
Each user gets their own terminal window:

```bash
# Terminal 3 - CEO
cd python/src && uv run user_client.py mary

# Terminal 4 - VP Sales
cd python/src && uv run user_client.py john

# Terminal 5 - VP Engineering
cd python/src && uv run user_client.py isac

# Terminal 6 - VP Legal
cd python/src && uv run user_client.py priya

# Terminal 7 - IT Admin (if needed)
cd python/src && uv run user_client.py bob
```

### Step 4: Demo Interaction
Each user sees:
- **Personalized dashboard** with their role and personality profile
- **3-line personality summary** showing their decision style and traits
- **Pending tasks** relevant to their role in active workflows
- **Menu options** for starting workflows (role-dependent) or responding to existing ones

## 📋 User Interface Features

### Personality Display
When each user starts their client, they see:
```
👤 Mary O'Keefe | CEO | 15 years exp
🧠 Decisive decision-maker | fast responder | moderate agreement tendency
💬 Direct communicator | strategic detail focus | ~5min response time
```

### Menu Options
1. **📋 Check pending workflow tasks** - See what needs their input
2. **🚀 Start strategic decision** (CEO only)
3. **🎯 Start competitor analysis** (VP Sales only)
4. **📊 Query workflow status** - Check any workflow by ID
5. **🔄 Refresh tasks** - Update pending task list
6. **Type 'r' or 'respond'** - Respond to workflows directly

### Temporal Web UI
Monitor all workflows at: http://localhost:8233

## 📁 File Structure

```
demo-data/           # User personality profiles
├── mary.yaml       # CEO profile
├── john.yaml       # VP Sales profile
├── isac.yaml       # VP Engineering profile
├── priya.yaml      # VP Legal profile
└── bob.yaml        # IT Admin profile

python/src/
├── workflows.py     # StrategicDecisionWorkflow, CompetitorAnalysisWorkflow
├── user_client.py   # Interactive terminal client for each user
├── user_profiles.py # YAML profile loader and personality display
├── users.py        # Basic user data structure
├── demo_runner.py   # Workflow starter utility
└── worker.py       # Temporal worker

python/
└── demo_runner.py   # Main demo launcher
```

## 🎯 Demo Script Suggestions

### Scenario 1: Strategic Decision
1. **Mary (CEO)** starts strategic decision workflow
2. **John (Sales)** provides market perspective and customer impact analysis
3. **Isac (Engineering)** raises technical concerns and implementation timeline
4. **Priya (Legal)** identifies regulatory risks and compliance requirements
5. **Mary (CEO)** makes informed final decision considering all input

### Scenario 2: Competitive Response
1. **John (Sales)** reports urgent competitive threat from market
2. **Isac (Engineering)** analyzes technical feasibility of counter-response
3. **Priya (Legal)** reviews IP implications and potential legal actions
4. **Mary (CEO)** decides comprehensive competitive strategy

## 🔧 Customization

### Editing User Personalities
Modify any `demo-data/*.yaml` file to adjust:
- Response time patterns
- Agreement/disagreement tendencies
- Communication styles
- Decision-making factors
- Risk tolerance levels
- Management philosophies

### Adding New Workflows
1. Define workflow in `workflows.py` with signals and queries
2. Add to worker registration in `worker.py`
3. Update user client menus and response handlers
4. Add demo scenario to `demo_runner.py`

### Personality Integration
The `user_profiles.py` system provides behavioral modifiers that can be integrated with:
- AI-generated responses
- Automated decision delays
- Response style variations
- Conflict simulation patterns

## 🎪 Demo Tips

1. **Stagger responses** - Let users respond at different speeds to show personality differences
2. **Show conflicts** - Isac and Priya often disagree with proposals for realistic tension
3. **Use real scenarios** - Adapt workflows to your actual business context
4. **Monitor Temporal UI** - Show the workflow execution and state management
5. **Highlight human-in-the-loop** - Demonstrate how business processes wait for human input
6. **Show audit trail** - Review complete decision history and reasoning

This system demonstrates how Temporal can orchestrate complex organizational decision-making while preserving the human element in business processes.
