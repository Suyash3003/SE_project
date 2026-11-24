# MODERN COLOURS

<p align="center">
  <img src="./mark.svg" alt="Modern Colours mark" width="76" />
</p>

<h3 align="center">Intelligent Manufacturing. Connected Operations.</h3>

<p align="center">
  A unified digital operations platform for modern manufacturing
  <br />
  Designed &amp; engineered by <a href="https://leorit.xyz"><strong>Leorit</strong></a>
  <br />
  Kohara, Ludhiana, Punjab, India
</p>

<p align="center">
  <img src="https://img.shields.io/badge/MANUFACTURING-OPERATIONS%20PLATFORM-8802C9?style=flat-square" alt="Manufacturing operations platform" />
  <img src="https://img.shields.io/badge/ARCHITECTURE-MODULAR-EB0102?style=flat-square" alt="Modular architecture" />
  <img src="https://img.shields.io/badge/DEPLOYMENT-VERCEL-111111?style=flat-square&logo=vercel&logoColor=white" alt="Vercel deployment" />
</p>

<p align="center">
  <strong>PRODUCTION INTELLIGENCE</strong> &nbsp;·&nbsp;
  <strong>SALES OPERATIONS</strong> &nbsp;·&nbsp;
  <strong>LEAD INTELLIGENCE</strong>
</p>

---

## Platform overview

**Modern Colours** brings production visibility, sales coordination, order management, and lead intelligence into one unified software environment.

Designed and engineered by **Leorit**, the platform is organized as three focused frontend applications. Each module has its own operational workspace while sharing a common visual language, reference data conventions, and deployment pipeline.

The platform is designed to make key manufacturing and commercial workflows easier to explore through a consistent, connected interface.

## Platform modules

| Module | Application path | Purpose |
|---|---|---|
| **Production & Machine** | `/machine-module` · `machine_prod_extended/` | Production visibility, machine views, operator workspaces, and batch tracking |
| **Sales & Order Management** | `/sales-module` · `sales_crm/` | Customer relationships, sales pipeline, and order lifecycle views |
| **Lead Intelligence** | `/lead-module` · `lead_system/` | Lead tracking, prospect management, and business development workflows |

### Production & Machine

A factory-floor focused workspace for presenting production activity and machine-related operational information.

- Production monitoring views
- Machine-level operational screens
- Operator-specific workspaces
- Batch and production tracking
- Scripted operational scenarios

### Sales & Order Management

A commercial operations workspace that brings customer and order information into a structured interface.

- Customer relationship views
- Sales pipeline visibility
- Order lifecycle management
- Product and raw-material references
- Customer-specific workspaces

### Lead Intelligence

A business development workspace for organizing prospective customer information and lead activity.

- Lead and prospect tracking
- Business development workflows
- Lead intelligence views
- Structured opportunity information

---

## Shared design system

All three applications follow a common design system to maintain a consistent experience across the platform.

The shared design resources are maintained centrally:

- `DESIGN_SYSTEM.md` — design principles and specifications.
- `design-system-kit copy/` — shared component and design references.

The system covers colour, typography, spacing, elevation, motion, and reusable interface patterns. Individual modules consume these shared conventions rather than establishing separate visual systems.

## Shared business conventions

The modules use common reference conventions so that information remains recognizable across the platform.

| Data area | Convention |
|---|---|
| Customers | Eight shared customer records |
| Products | Common product references |
| Raw materials | Common material references |
| Geography | Consistent city references |
| Production batches | `B-2280` through `B-2299` |
| Currency | Indian Rupee (₹) |
| Number formatting | Indian digit grouping |
| Date formatting | `DD MMM YYYY` |

## Operational walkthrough

The applications include scripted scenarios and a simulated clock to present repeatable changes in interface state. This makes the environment suitable for demonstrations, walkthroughs, and unattended display screens.

### Presenter console

Use **Ctrl + Shift + D** to reveal the presenter console.

| Control | Behaviour |
|---|---|
| Play / Pause | Start or pause the scripted timeline |
| 1× | Normal playback |
| 5× | Accelerated playback |
| 20× | Fast-forward playback |
| Jump | Move to a predefined moment |
| Reset | Return to the initial scenario state |

The presenter console is hidden during the normal application experience.

### Open a module in a user context

The `as` query parameter opens a module in a predefined user context.

```text
/machine-module/?as=U-106
```

### Continuous playback

Each module loops its scripted timeline approximately every four minutes, allowing a display to continue cycling through the prepared scenarios.

---

## Architecture

The repository contains three standalone Vite applications assembled into a single deployment.

```text
SE_project/
├── machine_prod_extended/   # Production & Machine application
├── sales_crm/               # Sales & Order Management application
├── lead_system/             # Lead Intelligence application
├── design-system-kit copy/  # Shared design references
├── DESIGN_SYSTEM.md         # Design system specifications
├── build.mjs                # Unified build orchestrator
├── vercel.json              # Vercel deployment and routing
├── mark.svg                 # Modern Colours brand mark
└── README.md
```

### Unified build pipeline

The root `build.mjs` script:

1. Builds each module that is present in the repository.
2. Applies the module-specific base path.
3. Collects the generated application assets.
4. Assembles the applications and landing page into one `dist/` directory.
5. Skips modules that are not yet present, allowing the suite to build incrementally.

Each module retains its own Vite project configuration and dependencies.

---

## Local development

### Requirements

- Node.js
- npm
- Git

### Clone the repository

```bash
git clone https://github.com/Suyash3003/SE_project.git
cd SE_project
```

### Run an individual module

Each development command starts the corresponding standalone Vite application. On first run, the module's dependencies are installed.

**Production & Machine**

```bash
npm run dev:machine
```

Open `http://localhost:5173/machine-module/`.

**Sales & Order Management**

```bash
npm run dev:sales
```

Open `http://localhost:5173/sales-module/`.

**Lead Intelligence**

```bash
npm run dev:leads
```

Open `http://localhost:5173/lead-module/`.

### Build the complete platform

From the repository root:

```bash
node build.mjs
```

The combined build output is written to:

```text
dist/
```

---

## Deployment

The repository is configured for a unified deployment on **Vercel**. Import the repository and use the configuration already defined in `vercel.json`.

| Vercel setting | Value |
|---|---|
| Build command | `node build.mjs` |
| Output directory | `dist` |
| Install command | `npm install --no-audit --no-fund` |
| Routing configuration | `vercel.json` |

**One repository. Three applications. One deployment.**

The modules are built independently and delivered together through the shared deployment output.

---

## Runtime and integration scope

The current deployed frontend environment runs on prepared seed data and a simulated clock. It does **not** connect to the factory's live ERP, production database, authentication infrastructure, or external backend services.

The environment is isolated from the live production ERP. Changes and activity within this frontend environment do not modify actual factory operations.

This distinction is important: the platform provides a realistic, navigable software experience, while its current data and scenario playback are self-contained.

---

## About Leorit

**Leorit builds digital infrastructure for industry.**

Leorit develops technology-driven solutions for businesses modernizing complex operational workflows, spanning manufacturing software, digital operations, intelligent automation, and digital twins.

[**Visit leorit.xyz**](https://leorit.xyz)

---

<p align="center">
  <img src="./mark.svg" alt="Modern Colours mark" width="34" />
  <br />
  <strong>MODERN COLOURS</strong>
  <br />
  Intelligent Manufacturing. Connected Operations.
  <br /><br />
  <sub>Designed &amp; engineered by Leorit · Kohara, Ludhiana, India</sub>
</p>
