
# MODERN COLOURS
### Intelligent Manufacturing. Connected Operations.

<p align="center">
  <img src="./mark.svg" alt="Modern Colours Logo" width="110" />
</p>

<p align="center">
  <strong>A Unified Digital Operations Platform for Modern Manufacturing</strong>
  <br />
  Designed & Engineered by <a href="https://leorit.xyz">Leorit</a>
  <br />
  Kohara, Ludhiana, Punjab, India
</p>

<p align="center">
  <img src="https://img.shields.io/badge/PLATFORM-Manufacturing%20OS-8802C9?style=for-the-badge" />
  <img src="https://img.shields.io/badge/DEPLOYMENT-Vercel-111111?style=for-the-badge&logo=vercel" />
  <img src="https://img.shields.io/badge/ARCHITECTURE-Modular-EB0102?style=for-the-badge" />
  <img src="https://img.shields.io/badge/INTERFACE-Enterprise%20UI-FEEF03?style=for-the-badge" />
</p>

---

## Overview

**Modern Colours** is a digitally enabled manufacturing operations environment designed to bring production visibility, sales coordination, order management, and lead intelligence into one unified software experience.

Developed by **Leorit**, the platform brings together three interconnected operational modules under a consistent design system and shared business vocabulary.

The objective is simple: create a structured digital layer across manufacturing operations, connecting the information that moves between customers, orders, production teams, and business development.

Instead of fragmented operational interfaces, Modern Colours presents a unified environment for understanding and managing the manufacturing lifecycle.

## Platform Architecture

The platform consists of three specialized operational modules.

| Module | Route | Operational Focus |
|---|---|---|
| Production & Machine Intelligence | `/machine-module` | Production visibility and machine operations |
| Sales & Order Management | `/sales-module` | Customer relationships and order lifecycle |
| Lead Intelligence | `/lead-module` | Lead tracking and business development |

### 01 — Production & Machine Intelligence

`machine_prod_extended/`

A production-focused operational interface designed to provide visibility into factory-floor activities.

- Production monitoring interface
- Machine-level operational views
- Operator-specific workspaces
- Batch and production tracking
- Time-driven operational scenarios

### 02 — Sales & Order Management

`sales_crm/`

A centralized commercial operations interface connecting customer relationships with order management.

- Customer relationship management
- Sales pipeline visibility
- Order lifecycle management
- Product and raw-material references
- Customer-specific operational views

### 03 — Lead Intelligence

`lead_system/`

A business development interface designed to structure lead information and provide visibility into prospective business opportunities.

- Lead management
- Prospect tracking
- Business development workflows
- Lead intelligence interfaces
- Structured sales opportunity views

---

## Unified Design Architecture

All three modules follow a shared design language to maintain visual and operational consistency.

The shared design system is the single source of truth for the entire platform.

**Core design principles**

- Consistent colour architecture
- Unified typography and hierarchy
- Standardized spacing and layout
- Reusable interface components
- Consistent elevation and surfaces
- Motion and interaction guidelines
- Responsive operational interfaces

**Design resources**

- `DESIGN_SYSTEM.md` — Core design specifications.
- `design-system-kit copy/` — Shared component and design references.

Individual modules consume the shared design language without redefining its foundations.

---

## Shared Business Data Model

The platform maintains consistent business terminology and reference data across all three modules.

| Data Domain | Shared Convention |
|---|---|
| Customers | 8 common customer records |
| Products | Unified product references |
| Raw Materials | Shared material references |
| Geography | Consistent city references |
| Production Batches | `B-2280` – `B-2299` |
| Currency | Indian Rupee (₹) |
| Number Formatting | Indian numbering conventions |
| Date Formatting | `DD MMM YYYY` |

This consistency enables the modules to be presented together as one connected operational environment.

---

## Operational Experience

### Scenario-driven Interfaces

The platform incorporates a scripted operational timeline to demonstrate how information and interface states evolve over time.

A simulated clock drives the predefined scenarios, allowing the applications to present changing operational states without requiring a live backend.

### Presenter Console

The built-in presenter console provides control over the operational timeline.

**Keyboard shortcut:** `CTRL + SHIFT + D`

Available controls:

- Play / Pause
- 1× — Normal playback
- 5× — Accelerated playback
- 20× — Fast-forward playback
- Jump to predefined moments
- Reset scenario

The console remains hidden during normal presentation.

### Contextual User Access

Modules support direct entry into predefined user contexts through URL parameters.

Example:

`/machine-module/?as=U-106`

This opens the machine module in the context of the specified user.

### Continuous Operation

Each module automatically cycles through its scripted operational timeline approximately every four minutes.

This supports unattended displays, presentations, and continuous product walkthroughs.

---

## Technology & Deployment Architecture

Modern Colours is organized as three independent frontend applications assembled into one unified deployment.

Each module maintains its own Vite configuration, dependencies, and application structure.

### Deployment Architecture

```text
MODERN COLOURS
│
├── Landing Page
│
├── Production & Machine
│   └── machine_prod_extended/
│
├── Sales & Order Management
│   └── sales_crm/
│
├── Lead Intelligence
│   └── lead_system/
│
├── Shared Design System
│   ├── DESIGN_SYSTEM.md
│   └── design-system-kit copy/
│
├── build.mjs
├── vercel.json
└── dist/
    ├── index.html
    ├── machine-module/
    ├── sales-module/
    └── lead-module/
```

### Unified Build Pipeline

The custom `build.mjs` orchestrates the deployment process.

1. Builds each available application independently.
2. Applies the appropriate base path to each application.
3. Collects the generated assets.
4. Assembles the applications into a unified `dist/` directory.
5. Includes the central landing page.
6. Skips modules that are not yet present.

This architecture allows individual modules to evolve independently while maintaining a single deployment endpoint.

---

## Installation & Development

### Prerequisites

- Node.js
- npm
- Git

### Clone the Repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### Run Individual Modules

Each module can be developed independently.

**Production & Machine**

```bash
npm run dev:machine
```

`http://localhost:5173/machine-module/`

**Sales & Order Management**

```bash
npm run dev:sales
```

`http://localhost:5173/sales-module/`

**Lead Intelligence**

```bash
npm run dev:leads
```

`http://localhost:5173/lead-module/`

The first execution of an individual development command installs that application's dependencies.

### Build the Complete Platform

```bash
node build.mjs
```

The unified production bundle is generated in:

```text
dist/
```

---

## Production Deployment

The platform is configured for a unified deployment through **Vercel**.

Import the repository into Vercel and retain the repository's existing deployment configuration.

| Configuration | Value |
|---|---|
| Build Command | `node build.mjs` |
| Output Directory | `dist` |
| Install Command | `npm install --no-audit --no-fund` |
| Deployment Configuration | `vercel.json` |

The existing Vercel configuration handles the build output and SPA routing for the individual modules.

### Deployment Model

**One repository. Three applications. One deployment.**

Each application remains independently structured while being delivered through a unified platform.

---

## Environment & Integration Scope

The deployed environment uses prepared seed data and a simulated operational clock to provide a consistent, repeatable software experience.

The current frontend environment does not establish a connection to the factory's live ERP, production database, authentication infrastructure, or external backend services.

It operates independently of the existing live production ERP.

This separation ensures that the platform environment can be explored and presented without modifying or interfering with actual factory operations.

---

## About Leorit

**Built by Leorit — Engineering Digital Infrastructure for Industry.**

Leorit develops technology-driven solutions for businesses looking to modernize complex operational workflows.

From manufacturing software and digital operations to intelligent automation and digital twins, Leorit focuses on transforming fragmented business processes into structured, connected systems.

**Website:** https://leorit.xyz

---

<p align="center">
  <img src="./mark.svg" alt="Modern Colours" width="48" />
  <br />
  <strong>MODERN COLOURS</strong>
  <br />
  Intelligent Manufacturing. Connected Operations.
  <br /><br />
  <sub>Designed & Engineered by Leorit · Kohara, Ludhiana, India</sub>
</p>
