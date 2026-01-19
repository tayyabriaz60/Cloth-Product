# Clothing Billing System - Complete Inventory & Sales Management

A comprehensive billing and inventory management system for a 2-piece clothing system (Kameez & Shalwar) with FastAPI backend and HTML frontend. Includes stock management, sales tracking, and profit/loss reporting.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Frontend**: HTML5, Tailwind CSS (CDN), Vanilla JavaScript

## Database Setup

1. Make sure PostgreSQL is installed and running
2. Create a database named `billu`:
   ```sql
   CREATE DATABASE billu;
   ```
3. The application will automatically create the `inventory` and `sales_records` tables on first run

## Installation & Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Update database credentials in `main.py` if needed:
   - Host: localhost
   - User: postgres
   - Password: tayyab
   - Database: billu

3. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

4. Open `index.html` for Sales Page or `admin.html` for Admin Dashboard

## Features

### Sales Page (`index.html`)
- ✅ Real-time calculation of totals as you type
- ✅ Standard size button to auto-fill 2.5 meters for both pieces
- ✅ Inventory selection dropdown with available stock display
- ✅ Automatic stock deduction when sales are made
- ✅ Stock validation to prevent overselling

### Admin Dashboard (`admin.html`)
- ✅ Stock Entry Form: Add new inventory with company name, design code, thans, meters per than, and cost price
- ✅ Stock Status Table: View current stock, sold meters, and remaining meters
- ✅ Profit/Loss Tracking: Calculate and display profit per design based on selling price vs cost price
- ✅ Low stock indicators (highlighted when remaining < 10m)

### Backend Features
- ✅ Automatic inventory stock deduction on sales
- ✅ Stock availability validation before processing sales
- ✅ Profit/loss calculations per design
- ✅ Automatic total meters and stock value calculations

## API Endpoints

- `GET /` - Health check endpoint
- `POST /add-stock` - Add new inventory stock
- `GET /get-inventory` - Get complete inventory status (sold/remaining)
- `GET /get-inventory-simple` - Get simplified inventory list for dropdowns
- `GET /get-profit-loss` - Get profit/loss report per design
- `POST /create-bill` - Create a new bill record (with inventory tracking)

### POST /add-stock Request Body

```json
{
  "company_name": "Gul Ahmed",
  "design_code": "Design-101",
  "total_thans": 5,
  "meters_per_than": 20,
  "cost_price_per_meter": 150.00
}
```

### POST /create-bill Request Body

```json
{
  "inventory_id": 1,
  "company_name": "Gul Ahmed",
  "design_code": "Design-101",
  "kameez_meters": 2.5,
  "kameez_rate": 200.00,
  "shalwar_meters": 2.5,
  "shalwar_rate": 180.00
}
```

Note: `inventory_id`, `company_name`, and `design_code` are optional. If `inventory_id` is provided, stock will be automatically deducted.

## Database Schema

### `inventory` Table
- `id` (Primary Key)
- `company_name`
- `design_code`
- `total_thans`
- `meters_per_than`
- `total_meters` (Calculated: thans × meters_per_than)
- `cost_price_per_meter`
- `total_stock_value` (Calculated: total_meters × cost_price_per_meter)
- `created_at`

### `sales_records` Table
- `id` (Primary Key)
- `inventory_id` (Foreign Key to inventory)
- `company_name`
- `design_code`
- `kameez_meters`, `kameez_rate`, `kameez_total`
- `shalwar_meters`, `shalwar_rate`, `shalwar_total`
- `grand_total`
- `created_at`

## Workflow Example

1. **Admin Entry**: Add stock via Admin Dashboard
   - Company: Gul Ahmed
   - Design Code: Design-101
   - Thans: 5
   - Meters per Than: 20
   - **Result**: System calculates 100 meters total stock

2. **Customer Sale**: Process sale via Sales Page
   - Select Design-101 from dropdown
   - Customer buys 5 meters (2.5m Kameez + 2.5m Shalwar)
   - **Result**: Stock automatically updated to 95 meters

3. **Profit Report**: View in Admin Dashboard
   - Shows profit per design based on (Selling Price - Cost Price)
   - Displays total revenue, cost, and profit percentage

## Project Structure

```
Clothes/
├── main.py              # FastAPI backend with all endpoints
├── index.html           # Sales page (customer flow)
├── admin.html           # Admin dashboard (inventory management)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```
