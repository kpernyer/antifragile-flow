# Fine-Tuning Experiment Extraction Plan

## Files to Extract for Standalone Repository

### Backend Components
```bash
# Core API
apps/api/app/routers/fine_tuning_experiment.py -> backend/app/routers/fine_tuning.py

# Supporting files needed
apps/api/pyproject.toml -> backend/pyproject.toml (simplified)
apps/api/Dockerfile -> backend/Dockerfile (simplified)

# Create new main.py with just fine-tuning routes
# Minimal FastAPI app focused on the experiment
```

### Frontend Components
```bash
# React Components
apps/admin_web/src/features/fine_tuning/FineTuningExperiment.tsx -> frontend/src/components/FineTuningExperiment.tsx
apps/admin_web/src/hooks/useFineTuning.ts -> frontend/src/hooks/useFineTuning.ts
apps/admin_web/src/services/fine-tuning.service.ts -> frontend/src/services/api.ts
apps/admin_web/src/types/fine-tuning.ts -> frontend/src/types/fine-tuning.ts

# Supporting components
apps/admin_web/src/components/ErrorBoundary.tsx -> frontend/src/components/ErrorBoundary.tsx
apps/admin_web/src/components/LoadingSpinner.tsx -> frontend/src/components/LoadingSpinner.tsx
apps/admin_web/src/components/Alert.tsx -> frontend/src/components/Alert.tsx
```

### Experiment Data
```bash
# Copy the experiments directory
experiments/fine-tuning/ -> experiments/fine-tuning/
```

### Configuration
```bash
# Create simplified docker-compose.yml (no Neo4j, just basic services)
# Create Makefile with demo commands
# Create .env.example with minimal config
```

## New Repository Structure Goals

1. **Self-contained**: No dependencies on main Living Twin monorepo
2. **Demo-focused**: Clear hackathon story and presentation
3. **Simple setup**: `make demo` should start everything
4. **Impressive visuals**: Before/after model comparisons
5. **Business story**: Organizational DNA learning narrative

## Key Simplifications for Hackathon

- Remove Neo4j dependency (use file storage for demo)
- Remove Firebase Auth (demo mode only)
- Include sample organizational documents
- Pre-generate some training examples for quick demos
- Focus on the core fine-tuning workflow

## Demo Script Integration

The new repo should include:
- Step-by-step demo instructions
- Sample strategic documents for different "company types"
- Pre-computed model responses for comparison
- Clear before/after examples
- Model size and performance metrics
