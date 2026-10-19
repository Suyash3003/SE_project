# PaintFlow.ai — Lab Evaluation I Diagrams

These diagrams cover the requirements listed in the UCS503 Lab Evaluation I
template. They are written in Mermaid so they remain editable before being
exported to PDF for the report.

## 2.1.1 Use-Case Diagram

~~~mermaid
flowchart LR
    customer[Customer]
    dealer[Dealer]
    admin[Manufacturer Admin]
    ai[Gemini AI Service]

    subgraph PaintFlow["PaintFlow.ai Platform"]
        auth([Register / Sign in])
        catalog([Browse shade catalog])
        match([Snap & Find shade])
        nearby([Find nearby dealer])
        order([Place paint order request])
        track([Track order status])
        leads([Manage customer leads])
        inventory([Monitor inventory])
        transfers([Approve stock transfers])
        forecast([View demand forecasts])
        recommendations([Review smart orders])
        copilot([Ask AI copilot])
        catalogAdmin([Manage paint catalog])
    end

    customer --> auth
    customer --> catalog
    customer --> match
    customer --> nearby
    customer --> order
    customer --> track

    dealer --> auth
    dealer --> leads
    dealer --> recommendations
    dealer --> inventory
    dealer --> copilot

    admin --> auth
    admin --> inventory
    admin --> transfers
    admin --> forecast
    admin --> catalogAdmin
    admin --> copilot

    order -. "creates lead" .-> leads
    inventory -. "provides live stock" .-> nearby
    inventory -. "provides context" .-> copilot
    forecast -. "drives" .-> recommendations
    ai <--> copilot
~~~

## 2.2 Activity Diagram — Customer Paint Order

~~~mermaid
flowchart TD
    start([Start]) --> login{Customer signed in?}
    login -- No --> signIn[Register or sign in]
    signIn --> catalog[Open shade catalog / Snap & Find]
    login -- Yes --> catalog
    catalog --> detail[View shade details]
    detail --> availability[Load nearby dealer availability]
    availability --> stock{An in-stock dealer found?}
    stock -- No --> alternate[Choose another shade or location]
    alternate --> catalog
    stock -- Yes --> form[Choose size, quantity, dealer and address]
    form --> valid{Details valid?}
    valid -- No --> form
    valid -- Yes --> request[Submit order request]
    request --> saved[Save request with Requested status]
    saved --> notify[Expose request to selected dealer]
    notify --> confirmation[Show order confirmation]
    confirmation --> finish([End])
~~~

## 2.2 Swimlane Diagram — Order Request Lifecycle

~~~mermaid
sequenceDiagram
    actor Customer
    participant App as PaintFlow Web App
    participant API as PaintFlow API
    participant DB as PaintFlow Database
    actor Dealer

    Customer->>App: Select shade, size, quantity and dealer
    App->>API: Get shade availability
    API->>DB: Read SKU and warehouse stock
    DB-->>API: Nearby dealer stock levels
    API-->>App: Orderable dealers
    Customer->>App: Submit order details
    App->>API: POST order request
    API->>DB: Validate dealer and shade
    API->>DB: Save customer order request (requested)
    API-->>App: Confirmation and request ID
    Dealer->>API: View assigned customer requests
    API->>DB: Read dealer's requests
    DB-->>API: Customer request list
    API-->>Dealer: Leads to contact or fulfill
    Dealer->>API: Update request status
    API->>DB: Save status change
    Customer->>API: View My Orders
    API->>DB: Read only customer's requests
    API-->>Customer: Updated order status
~~~

## 2.3.1 DFD Level 0 — Context Diagram

~~~mermaid
flowchart LR
    customer[Customer]
    dealer[Dealer]
    admin[Manufacturer Admin]
    gemini[Gemini AI Service]
    system((PaintFlow.ai))

    customer -->|Credentials, color, order details| system
    system -->|Shades, availability, order status| customer
    dealer -->|Order updates, fulfillment actions| system
    system -->|Customer leads, smart orders, inventory insight| dealer
    admin -->|Catalog, inventory and transfer actions| system
    system -->|Forecasts, analytics, alerts| admin
    system -->|Inventory context and questions| gemini
    gemini -->|Structured copilot response| system
~~~

## 2.3.2 DFD Level 1 — PaintFlow Core Processes

~~~mermaid
flowchart LR
    customer[Customer]
    dealer[Dealer]
    admin[Admin]
    gemini[Gemini]

    p1((1.0 Authentication))
    p2((2.0 Catalog and Shade Matching))
    p3((3.0 Customer Ordering))
    p4((4.0 Inventory and Dealer Operations))
    p5((5.0 Forecasting and AI Copilot))

    users[(D1 Users)]
    catalog[(D2 Products, Shades and SKUs)]
    inventory[(D3 Warehouses and Inventory)]
    orders[(D4 Customer Order Requests)]
    sales[(D5 Sales History and Forecast Models)]

    customer -->|credentials| p1
    p1 <--> users
    customer -->|color / catalog query| p2
    p2 <--> catalog
    customer -->|order request| p3
    p3 --> orders
    p3 -->|validate selected shade| catalog
    p3 -->|check dealer stock| inventory
    p3 -->|confirmation / status| customer

    dealer -->|fulfillment actions| p4
    admin -->|inventory / transfer actions| p4
    p4 <--> inventory
    p4 <--> orders
    p4 -->|leads and inventory information| dealer
    p4 -->|inventory information| admin

    admin -->|forecast / copilot request| p5
    dealer -->|copilot request| p5
    p5 <--> sales
    p5 -->|inventory context| gemini
    gemini -->|AI response| p5
    p5 -->|forecast or response| admin
    p5 -->|recommendation or response| dealer
~~~

## 2.3.3 DFD Level 2 — Customer Ordering Process

~~~mermaid
flowchart TD
    customer[Customer]
    catalog[(D2 Products, Shades and SKUs)]
    inventory[(D3 Warehouses and Inventory)]
    dealers[(D6 Dealers)]
    orders[(D4 Customer Order Requests)]
    dealer[Selected Dealer]

    p31((3.1 Select shade and SKU))
    p32((3.2 Find eligible dealers))
    p33((3.3 Validate order details))
    p34((3.4 Create order request))
    p35((3.5 Present status))

    customer -->|shade, size and quantity| p31
    p31 <--> catalog
    p31 -->|selected SKU| p32
    p32 -->|stock query| inventory
    p32 -->|nearby dealer query| dealers
    p32 -->|available dealer list| customer
    customer -->|dealer, contact and delivery details| p33
    p33 -->|validated request| p34
    p34 -->|new requested order| orders
    p34 -->|new lead| dealer
    p34 --> p35
    orders --> p35
    p35 -->|confirmation and current status| customer
~~~

## Export for the report

Open this file in GitHub, VS Code with a Mermaid preview extension, or the
Mermaid Live Editor. Export each diagram as SVG or PNG, then place it below the
matching heading in the Lab Evaluation I report.

## End-Semester Design Diagrams

The UCS503 end-semester template requires at least two significant examples of
class, sequence, collaboration, and state-chart diagrams, plus component and
deployment diagrams. The following diagrams fulfil those requirements.

### 3.1 Class Diagram 1 — Paint Catalog and Inventory

~~~mermaid
classDiagram
    class Product {
        +id: int
        +name: string
        +category: string
        +finish: string
        +price_per_litre: float
    }
    class Shade {
        +id: int
        +shade_code: string
        +shade_name: string
        +hex_color: string
        +shade_family: string
    }
    class SKU {
        +id: int
        +sku_code: string
        +size: string
        +mrp: float
    }
    class Warehouse {
        +id: int
        +name: string
        +city: string
        +capacity: int
    }
    class InventoryLevel {
        +id: int
        +current_stock: int
        +days_of_cover: float
        +min_threshold: int
    }
    class InventoryTransfer {
        +id: int
        +quantity: int
        +status: string
        +is_ai_suggested: boolean
    }

    Product "1" --> "*" Shade : offers
    Shade "1" --> "*" SKU : packaged as
    Warehouse "1" --> "*" InventoryLevel : stores
    SKU "1" --> "*" InventoryLevel : tracked by
    SKU "1" --> "*" InventoryTransfer : transferred
    Warehouse "1" --> "*" InventoryTransfer : source or destination
~~~

### 3.1 Class Diagram 2 — Users, Dealers, and Customer Orders

~~~mermaid
classDiagram
    class User {
        +id: int
        +email: string
        +phone: string
        +role: string
        +status: string
    }
    class Dealer {
        +id: int
        +name: string
        +code: string
        +city: string
        +tier: string
    }
    class CustomerOrderRequest {
        +id: int
        +customer_name: string
        +customer_phone: string
        +size_preference: string
        +quantity: int
        +delivery_address: string
        +status: string
    }
    class DealerOrder {
        +id: int
        +quantity: int
        +status: string
        +is_ai_suggested: boolean
    }
    class Shade {
        +id: int
        +shade_name: string
        +shade_code: string
    }

    User "1" --> "0..1" Dealer : represents when dealer
    User "1" --> "*" CustomerOrderRequest : places
    Dealer "1" --> "*" CustomerOrderRequest : fulfils
    Dealer "1" --> "*" DealerOrder : creates
    Shade "1" --> "*" CustomerOrderRequest : requested shade
~~~

### 3.2 Sequence Diagram 1 — Customer Order Request

~~~mermaid
sequenceDiagram
    actor Customer
    participant UI as Customer Portal
    participant API as Customer API
    participant DB as Database
    participant Dealer as Dealer Portal

    Customer->>UI: Select shade, size and quantity
    UI->>API: Request nearby availability
    API->>DB: Read dealer warehouse inventory
    DB-->>API: Stock levels and dealers
    API-->>UI: Orderable dealer list
    Customer->>UI: Submit delivery details
    UI->>API: Create customer order request
    API->>DB: Validate shade and dealer
    API->>DB: Save request with requested status
    API-->>UI: Request confirmation
    Dealer->>API: View assigned customer leads
    API->>DB: Retrieve dealer requests
    DB-->>API: Assigned requests
    API-->>Dealer: Lead list
~~~

### 3.2 Sequence Diagram 2 — AI Transfer Recommendation

~~~mermaid
sequenceDiagram
    actor Admin
    participant UI as Admin Portal
    participant API as Inventory API
    participant DB as Database
    participant Engine as Recommendation Engine

    Admin->>UI: Open inventory and transfer dashboard
    UI->>API: Request warehouse health data
    API->>DB: Read inventory, SKU and warehouse records
    DB-->>API: Stock and days-of-cover data
    API->>Engine: Analyse stock imbalance
    Engine-->>API: Suggested source, destination and quantity
    API-->>UI: Transfer recommendations and alerts
    Admin->>UI: Approve transfer
    UI->>API: Confirm transfer action
    API->>DB: Create transfer and update stock levels
    API-->>UI: Updated transfer status
~~~

### 3.3 Collaboration Diagram 1 — Customer Order Collaboration

~~~mermaid
flowchart LR
    customer[1 Customer]
    portal[2 Customer Portal]
    customerApi[3 Customer API]
    inventory[4 Inventory Service]
    database[5 Database]
    dealer[6 Dealer Portal]

    customer -->|1. select shade| portal
    portal -->|2. availability query| customerApi
    customerApi -->|3. stock lookup| inventory
    inventory -->|4. read inventory| database
    database -->|5. stock result| inventory
    inventory -->|6. eligible dealers| customerApi
    customerApi -->|7. orderable dealers| portal
    customer -->|8. submit request| portal
    portal -->|9. create request| customerApi
    customerApi -->|10. save request| database
    dealer -->|11. retrieve assigned lead| customerApi
    customerApi -->|12. lead details| dealer
~~~

### 3.3 Collaboration Diagram 2 — Forecast and Smart-Order Collaboration

~~~mermaid
flowchart LR
    dealer[1 Dealer]
    dealerUi[2 Dealer Portal]
    dealerApi[3 Dealer API]
    forecast[4 Forecast Service]
    inventory[5 Inventory Service]
    database[6 Database]

    dealer -->|1. open smart orders| dealerUi
    dealerUi -->|2. request recommendations| dealerApi
    dealerApi -->|3. demand forecast query| forecast
    forecast -->|4. sales history and model data| database
    database -->|5. historical demand| forecast
    dealerApi -->|6. inventory health query| inventory
    inventory -->|7. stock and cover query| database
    database -->|8. inventory levels| inventory
    forecast -->|9. demand signal| dealerApi
    inventory -->|10. reorder risk| dealerApi
    dealerApi -->|11. smart order list| dealerUi
    dealerUi -->|12. review recommendations| dealer
~~~

### 3.4 State Chart Diagram 1 — Customer Order Request

~~~mermaid
stateDiagram-v2
    [*] --> Requested
    Requested --> Contacted : Dealer contacts customer
    Requested --> Cancelled : Customer or dealer cancels
    Contacted --> Fulfilled : Order delivered or collected
    Contacted --> Cancelled : Order cannot be fulfilled
    Fulfilled --> [*]
    Cancelled --> [*]
~~~

### 3.4 State Chart Diagram 2 — Inventory Transfer

~~~mermaid
stateDiagram-v2
    [*] --> Suggested
    Suggested --> Approved : Admin approves
    Suggested --> Rejected : Admin rejects
    Approved --> InTransit : Dispatch confirmed
    InTransit --> Completed : Destination receives stock
    Approved --> Cancelled : Transfer cancelled
    Rejected --> [*]
    Completed --> [*]
    Cancelled --> [*]
~~~

### 4.1 Component Diagram

~~~mermaid
flowchart TB
    subgraph Frontend["React Frontend"]
        customerUi[Customer Portal]
        dealerUi[Dealer Portal]
        adminUi[Admin Portal]
        apiClient[Axios API Client]
    end

    subgraph Backend["FastAPI Backend"]
        auth[Authentication Component]
        customerApi[Customer Router]
        dealerApi[Dealer Router]
        adminApi[Admin Router]
        forecastApi[Forecast Router]
        copilotApi[Copilot Router]
        inventoryService[Inventory Service]
        forecastService[Forecast Service]
        recommendationService[Dealer and Transfer Services]
    end

    database[(SQLite Database)]
    prophet[Prophet Forecast Models]
    gemini[Google Gemini API]

    customerUi --> apiClient
    dealerUi --> apiClient
    adminUi --> apiClient
    apiClient --> auth
    apiClient --> customerApi
    apiClient --> dealerApi
    apiClient --> adminApi
    apiClient --> forecastApi
    apiClient --> copilotApi

    customerApi --> inventoryService
    dealerApi --> recommendationService
    adminApi --> inventoryService
    forecastApi --> forecastService
    copilotApi --> inventoryService
    copilotApi --> gemini
    inventoryService --> database
    recommendationService --> database
    forecastService --> database
    forecastService --> prophet
~~~

### 4.2 Deployment Diagram

~~~mermaid
flowchart TB
    browser[User Browser]
    frontend[Frontend Host - React and Vite Build]
    backend[Application Host - FastAPI and Uvicorn]
    database[(SQLite Data Store)]
    modelStore[(Prophet Model Files)]
    gemini[Google Gemini API]

    browser -->|HTTPS| frontend
    frontend -->|REST API requests| backend
    backend -->|read and write| database
    backend -->|load trained models| modelStore
    backend -->|optional AI request| gemini
~~~
