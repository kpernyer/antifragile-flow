# Living Twin Monorepo - System Overview

*Auto-generated system documentation*

Generated on: 2025-09-12T12:14:33.236284

## System Architecture

![System Architecture](https://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/kpernyer/living-twin-monorep/main/docs/v0.1/system/system_architecture.puml)

### Discovered Components (4 total)

#### API Services (2 services)
- **hello_world_api**: 0 routes, 0 classes
  - Path: `apps/hello_world_api`
- **api**: 7 routes, 42861 classes
  - Path: `apps/api`
  - Key routes: __ensure_cext(), _init_symbols(), _engine_uri()

#### Web Applications (1 apps)
- **admin_web**: 13 React components, 278 functions
  - Path: `apps/admin_web`
  - Key components: Alert (Component), LoadingSpinner (Component), NotificationToast (Component)

#### Infrastructure (1 packages)
- **gcp_firebase**: 38 resources
  - Path: `packages/gcp_firebase`

## Technology Stack

### Backend Technologies
- **FastAPI**
- **LangChain**
- **Neo4j**
- **OpenAI**
- **Redis**
- **Strawberry GraphQL**

### Frontend Technologies
- **Firebase**
- **React**
- **TypeScript**
- **Vite**

### Databases
- **Neo4j**
- **Redis**

### External Services
- **OpenAI API**
- **Firebase**
- **Google Cloud Platform**
- **Sentry**
- **OpenAI API**
- **Firebase**
- **Sentry**
- **OpenAI API**
- **Firebase**
- **Google Cloud Platform**
- **Sentry**
- **OpenAI API**
- **Firebase**
- **Google Cloud Platform**
- **Sentry**
- **OpenAI API**
- **Firebase**
- **Google Cloud Platform**
- **Sentry**
- **OpenAI API**
- **Firebase**
- **Sentry**
- **OpenAI API**
- **Firebase**
- **Sentry**

## API Flows

![API Flows](https://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/kpernyer/living-twin-monorep/main/docs/v0.1/system/api_flows.puml)

## Component Relationships

![Component Diagram](https://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/kpernyer/living-twin-monorep/main/docs/v0.1/system/component_diagram.puml)

## Identified Architecture Patterns

- **Microservices Architecture**: Separate API and web services
- **Polyglot Persistence**: Multiple database technologies
- **GraphQL API**: Modern API query language
- **SPA Architecture**: Single Page Application frontend
- **Async API**: High-performance async Python API

## PlantUML Source Files

- [System Architecture](./system_architecture.puml)
- [API Flows](./api_flows.puml)
- [Component Diagram](./component_diagram.puml)

---
*This documentation is automatically generated. To update, run: `make uml`*
