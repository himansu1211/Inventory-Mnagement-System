# Enterprise Smart-IMS (Inventory Management System)

A professional full-stack Inventory Management System built with React (Tailwind CSS), Python Flask, and SQLite.

## Features

### Backend (Flask + SQLite)
- ✅ Automatic database initialization
- ✅ Database transactions for atomic operations
- ✅ RESTful API endpoints
- ✅ PDF report generation using ReportLab
- ✅ Dashboard statistics aggregation
- ✅ Comprehensive error handling

### Frontend (React)
- ✅ Modern sidebar-based layout
- ✅ Dashboard with stat cards and sales trend chart
- ✅ Inventory table with live search and filtering
- ✅ Stock status badges (In Stock, Low Stock, Out of Stock)
- ✅ Record Sale modal with validation
- ✅ Restock modal
- ✅ Toast notifications
- ✅ Fully responsive design
- ✅ Loading states

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

**No database server needed!** SQLite is built into Python.

## Quick Start

### 1. Backend Setup

```bash
# Navigate to backend folder
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run the Flask server (database will be created automatically)
python app.py
```

The backend will:
- ✅ Create `inventory.db` automatically if it doesn't exist
- ✅ Create all tables and indexes
- ✅ Insert sample categories
- ✅ Start on `http://localhost:5000`

### 2. Seed the Database (Optional)

To populate with 50 products and 7 days of sales data:

```bash
# In the backend folder
python seed_sqlite.py
```

This will create:
- 8 categories
- 50 products
- 7 days of sales data
- Stock log entries

### 3. Frontend Setup

```bash
# Navigate to frontend folder
cd frontend

# Install Node.js dependencies
npm install

# Start the React development server
npm start
```

The frontend will run on `http://localhost:3000`

## Project Structure

```
Enterprise Smart-IMS/
├── backend/
│   ├── app.py              # Flask backend with SQLite
│   ├── inventory.db        # SQLite database (auto-generated)
│   ├── seed_sqlite.py      # Database seeding script
│   └── requirements.txt    # Python dependencies
├── frontend/               # React App
│   ├── src/
│   │   ├── App.js
│   │   ├── index.js
│   │   └── components/
│   ├── public/
│   ├── package.json
│   └── ...
└── README.md
```

## API Endpoints

### Dashboard
- `GET /api/dashboard-stats` - Get dashboard statistics and sales trend

### Products
- `GET /api/products` - Get all products (supports `?search=query` and `?low_stock_only=true`)
- `GET /api/products/<id>` - Get a single product
- `POST /api/products` - Create a new product
- `PUT /api/products/<id>` - Update an existing product

### Sales
- `POST /api/add-sale` - Record a sale (with transaction)
- `GET /api/sales` - Get all sales

### Stock Management
- `POST /api/restock` - Restock a product

### Reports
- `GET /api/export-pdf` - Generate and download PDF inventory report

### Categories
- `GET /api/categories` - Get all categories

### Health Check
- `GET /api/health` - Check API and database status

## Key Features Explained

### Automatic Database Initialization
The `init_db()` function in `app.py` automatically:
- Creates `inventory.db` if it doesn't exist
- Creates all tables (categories, products, sales, stock_logs)
- Creates indexes for performance
- Inserts sample categories

### Database Transactions
The `/api/add-sale` endpoint uses SQLite transactions to ensure:
- Stock is deducted atomically
- Sale is recorded
- Stock log is created
- All operations succeed or fail together

### PDF Export
The `/api/export-pdf` endpoint generates a professional PDF report with:
- All products listed in a table
- Color-coded status indicators
- Formatted pricing and stock levels

## Running the Application

### Terminal 1 - Backend:
```bash
cd backend
python app.py
```

### Terminal 2 - Frontend:
```bash
cd frontend
npm start
```

Then open `http://localhost:3000` in your browser.

## Database File Location

The SQLite database file (`inventory.db`) is created in the `backend/` folder. You can:
- ✅ View it with any SQLite browser (DB Browser for SQLite, etc.)
- ✅ Backup by copying the file
- ✅ Delete it to reset the database (it will be recreated on next run)

## Troubleshooting

### Backend won't start
- Make sure you're in the `backend/` folder
- Check Python version: `python --version` (should be 3.8+)
- Install dependencies: `pip install -r requirements.txt`

### Frontend won't start
- Make sure you're in the `frontend/` folder
- Install dependencies: `npm install`
- Check Node.js version: `node --version` (should be 16+)

### Database errors
- Delete `backend/inventory.db` and restart the backend (it will recreate)
- Make sure no other process is using the database file

### CORS Errors
- Ensure Flask-CORS is installed: `pip install flask-cors`
- Verify backend is running on port 5000
- Check browser console for specific errors

## Technologies Used

- **Frontend**: React 18, Tailwind CSS, Recharts, Lucide React, Axios
- **Backend**: Flask, Flask-CORS, SQLite3 (built-in), ReportLab
- **Database**: SQLite 3

## Advantages of SQLite Over MySQL

1. **Zero Configuration**: No server setup, no passwords
2. **Portable**: Single file database - easy to backup and move
3. **Fast**: Perfect for single-user or small team applications
4. **No Dependencies**: SQLite is built into Python
5. **Development Friendly**: Great for prototyping and testing

## License

This project is for educational and commercial use.

---

**Enjoy your simplified Inventory Management System!** 