# Current Architecture — Scientific Diagram Set

This folder contains **17 formal engineering diagrams** for the three-module Modern Colours platform. They are redrawn in a monochrome academic-report style with numbered processes, nested boundaries, UML-style component groups, DFD entities and data stores, decision nodes, message sequences, state transitions and mathematical annotations.

## Figure register

1. [System Context / Use-Case Boundary](./platform-context.svg) — Actors, module routes and system boundary.
2. [Layered Three-Application Architecture](./module-architecture.svg) — Independent Vite module boundaries and shared dependencies.
3. [Production & Machine Activity Model](./production-machine.svg) — Operator context, monitoring, machine workspace and batch tracking.
4. [Sales & Order Management Process](./sales-order-management.svg) — Customer workspace, sales pipeline, order lifecycle and analytics.
5. [Lead Intelligence Prioritization Workflow](./lead-intelligence.svg) — Lead records, prospect context, weighted lead score and follow-up.
6. [Shared Design-System Dependency Model](./shared-design-system.svg) — Central specification, reference kit and consuming frontend modules.
7. [Shared Business Conventions Model](./shared-business-data.svg) — Common customer, product, raw material, geography, batch and formatting domains.
8. [Deployment / Build Node Diagram](./build-and-deployment.svg) — Independent Vite builds, build.mjs, dist output and Vercel.
9. [Scenario Activity / Presenter State Model](./scenario-timeline.svg) — Simulated clock, presenter controls and repeatable timeline.
10. [DFD Level 0 — Context](./dfd-level-0.svg) — External actors and central Modern Colours process.
11. [DFD Level 1 — Functional Decomposition](./dfd-level-1.svg) — Six logical processes and conceptual data stores.
12. [Component Diagram — Detailed Decomposition](./component-architecture.svg) — Module views, shared packages and runtime support.
13. [Activity Diagram — Cross-Module Journey](./activity-workflow.svg) — Landing, module choice, initialization and presenter path.
14. [Sequence Diagram — Platform Boot](./sequence-platform-boot.svg) — Numbered messages across seven lifelines.
15. [Collaboration Diagram — Object Dependencies](./collaboration-map.svg) — Numbered object relationships and shared references.
16. [State Machine — Application Lifecycle](./state-machine.svg) — Module and simulated scenario transitions.
17. [Mathematical Model Sheet](./mathematical-models.svg) — OEE, commercial KPIs, lead score and scenario equation.

## Modelling conventions

- Three independent Vite applications: Production & Machine (`machine_prod_extended/`, `/machine-module`), Sales & Order Management (`sales_crm/`, `/sales-module`) and Lead Intelligence (`lead_system/`, `/lead-module`).
- Shared design resources: `DESIGN_SYSTEM.md` and `design-system-kit copy/`.
- Build and deployment: independent module builds assembled by root `build.mjs` into `dist/` for Vercel static hosting.
- Prepared data and simulated time: the diagrams model scripted demonstration states, not live machine telemetry.
- No live integrations: no live ERP, factory database, external CRM or backend API is represented.
- DFD stores and logical data domains are conceptual documentation groupings, not physical database tables or a shared database service.
- Formula-driven KPI and prioritization models are distinguished from trained machine-learning models.

The historical diagram collection remains separated under [`../old/`](../old/README.md) and marked OLD / ARCHIVED.
