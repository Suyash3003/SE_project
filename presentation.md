# PaintFlow.ai

## AI-powered supply-chain intelligence for paint distribution

PaintFlow.ai is a full-stack web platform for paint manufacturers, dealers,
and customers. It turns fragmented inventory, demand, and customer-order
information into one workflow: customers find a shade and request it from a
nearby dealer; dealers manage demand and leads; manufacturers monitor inventory,
forecast demand, and respond to disruptions.

## The problem it solves

Paint distribution has three connected problems:

1. Customers struggle to find a specific shade in stock near them.
2. Dealers risk stock-outs, excess inventory, and missed sales opportunities.
3. Manufacturers lack a single view of demand, inventory health, transfers,
   and disruption impact across their network.

PaintFlow.ai connects these groups through role-based portals, live inventory
signals, demand forecasts, smart recommendations, and an AI copilot.

## What the platform has now

### Customer portal

- Browse paint shades by family, category, and trending status.
- View shade details, available pack sizes, product information, and price.
- Use **Snap & Find** to match a wall/photo colour or HEX colour to the closest
  catalog shade.
- Find nearby authorised dealers and see stock availability.
- Place a paint order request by choosing a size, quantity, in-stock dealer,
  delivery address, and optional notes.
- View **My Orders**, including dealer, estimated amount, and the latest order
  status.

### Dealer portal

- See an inventory-health dashboard and dealer performance information.
- Receive smart order recommendations based on inventory conditions.
- Track dealer orders.
- View customer order requests assigned to the dealer and update their status.

### Manufacturer admin portal

- Monitor inventory health, stock-out risks, dead stock, and revenue exposure.
- View warehouse network and inter-warehouse transfer recommendations.
- Review demand forecasts and dealer performance.
- Manage the paint/shade catalog.
- Monitor customer leads across dealers.
- Run what-if supply-chain scenarios: truck strike, heatwave, and early monsoon.

### AI and forecasting

- **Gemini Copilot:** answers supply-chain questions using the current inventory
  context and can return safe structured UI widgets such as transfer cards.
- **Demand forecasting:** uses Prophet time-series models for SKU/region
  forecasts. A deterministic fallback forecast keeps the dashboard usable when
  trained models are unavailable.
- **Local AI analysis mode:** when no Gemini key is configured or Gemini is
  temporarily unavailable, the copilot still returns a local, context-aware
  inventory response instead of failing.

## AI models used

| Capability | Model / approach | Purpose |
| --- | --- | --- |
| Conversational copilot | Google Gemini, default gemini-2.5-flash | Answers operational questions using live inventory context |
| Demand forecast | Prophet 1.5 | Forecasts SKU-level, regional demand |
| Shade matching | RGB Euclidean-distance ranking | Finds the closest catalog paint shade from a HEX value or sampled image colour |
| Smart order / transfer suggestions | Inventory and demand rules | Flags stock risks and calculates practical replenishment/transfer recommendations |

The Gemini model name is configurable through GEMINI_MODEL. A valid
GEMINI_API_KEY is required for live Gemini responses.

## Technology stack

| Layer | Technology |
| --- | --- |
| Frontend | React 19, Vite, Tailwind CSS 4, React Router |
| API client | Axios |
| Visualisation | Recharts, react-simple-maps, Heroicons |
| Backend | Python, FastAPI, Pydantic, Uvicorn |
| Data store | SQLite with the project document-model layer |
| Forecasting | Prophet, CmdStanPy, Pandas, NumPy |
| Generative AI | Google GenAI SDK (google-genai) |
| Authentication | Role-based JWT authentication with scrypt password hashing |
| Quality checks | Pytest backend tests and Vite production build |

## Recent fixes and completed work

- Replaced the retired Gemini client with the current Google GenAI SDK.
- Made the Gemini model configurable instead of hard-coding it.
- Added timeout handling and a data-aware local copilot fallback.
- Added the complete customer order-request interface and customer order-history
  screen.
- Restricted customer order history to the signed-in customer's own requests.
- Added Lab Evaluation I diagrams: use case, activity, swimlane, and DFD
  Levels 0, 1, and 2.
- Verified the backend test suite (**21 passing tests**) and a production
  frontend build.

## What is intentionally incomplete

PaintFlow.ai is a working MVP/prototype. The following are planned
production-grade extensions, not currently implemented:

- Online payment, invoices, refunds, and payment reconciliation.
- Delivery-partner integration, route optimisation, real-time shipment tracking,
  and delivery proof.
- Reservation/deduction of physical stock immediately after a customer request;
  the current flow creates a dealer lead, and the dealer confirms fulfillment.
- SMS, WhatsApp, push, or email notifications. Authentication has verification
  and reset flows, but an SMTP provider must be configured to send messages.
- A managed production database, backup strategy, migrations, caching, and
  horizontal scaling. The MVP uses SQLite.
- Automated deployment, CI/CD, monitoring, audit logging, and rate limiting.
- Continuous retraining and real sales-data ingestion for forecasting. The
  included seeded data and simulation date support demonstrations.

## Run locally

### Backend

~~~bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed_and_train.py
uvicorn app.main:app --reload --port 8001
~~~

Create backend/.env from backend/.env.example and configure at least:

~~~env
JWT_SECRET=use-a-random-secret-with-at-least-32-characters
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash
~~~

GEMINI_API_KEY is optional for local development; without it, the copilot
uses local analysis mode.

### Frontend

~~~bash
cd frontend
npm install
npm run dev
~~~

Open http://localhost:5173. The frontend proxies API requests to the backend
at port 8001.

## Lab evaluation diagrams

The rendered SVG diagrams are in [docs/diagrams](docs/diagrams):

- use-case.svg
- activity.svg
- swimlane.svg
- dfd-level-0.svg
- dfd-level-1.svg
- dfd-level-2.svg

The editable Mermaid source is in
[docs/Lab-Eval-I-Diagrams.md](docs/Lab-Eval-I-Diagrams.md).
