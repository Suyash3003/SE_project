# Current Architecture — Modern Colours

These nine diagrams document the **three-module Modern Colours project specification**:

1. Production & Machine — `machine_prod_extended/` at `/machine-module`
2. Sales & Order Management — `sales_crm/` at `/sales-module`
3. Lead Intelligence — `lead_system/` at `/lead-module`

The modules are specified as independent Vite applications assembled by the root `build.mjs` into one `dist/` deployment for Vercel. They share a design system and common business-reference conventions. The supplied project description also specifies prepared seed data and a simulated operational clock, rather than a live ERP/backend integration.

## Diagram register

1. [Platform context](./platform-context.svg) — Landing page, three module routes, shared design language and business conventions.
2. [Modular application architecture](./module-architecture.svg) — Three separate Vite apps, each retaining its own project configuration and dependencies.
3. [Production & Machine module](./production-machine.svg) — Production visibility, machine workspaces, operator context and batch-oriented scenarios.
4. [Sales & Order Management module](./sales-order-management.svg) — Customer views, sales pipeline, order lifecycle and shared product/material references.
5. [Lead Intelligence module](./lead-intelligence.svg) — Lead and prospect management, business-development workflows and opportunity views.
6. [Shared design-system architecture](./shared-design-system.svg) — Central design specification and component references consumed by all three applications.
7. [Shared business reference model](./shared-business-data.svg) — Common customer, product, raw material, geography, batch and formatting conventions.
8. [Unified build and deployment](./build-and-deployment.svg) — Independent module builds assembled into one Vercel deployment by build.mjs.
9. [Scenario timeline and presenter controls](./scenario-timeline.svg) — Simulated clock, repeated scenario playback, hidden presenter console and user-context entry.

## Important interpretation notes

- The diagrams are an **architecture and product-scope model** based on the three-app Modern Colours project specification retained in the earlier README history.
- Shared customer/product/material/geography/batch conventions do not establish a live database, API, or synchronization mechanism between the modules.
- The presenter timeline is simulated and uses prepared data; it is not evidence of live factory telemetry.
- The build/deployment diagram describes the documented target pipeline (`node build.mjs`, output `dist/`, Vercel). Verify that the corresponding module folders and configuration are present in a given checkout before treating the pipeline as executable there.
- Previous diagrams for the earlier PaintFlow / Admin–Dealer–Customer portal architecture are preserved under [`../old/`](../old/README.md) and are explicitly marked **OLD — ARCHIVED**.
