"""
Flask backend for Enterprise Smart-IMS using SQLite
Handles all API routes with proper error handling and database transactions
"""

import sqlite3
import os
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'inventory.db')


# ==================== DATABASE INITIALIZATION ====================

def init_db():
    """Initialize the database and create tables if they don't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                sku TEXT NOT NULL UNIQUE,
                category_id INTEGER NOT NULL,
                price REAL NOT NULL,
                purchasing_price REAL NOT NULL DEFAULT 0,
                stock_quantity INTEGER NOT NULL DEFAULT 0,
                min_stock_level INTEGER NOT NULL DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')
        
        # Add purchasing_price column if it doesn't exist (migration)
        try:
            cursor.execute('ALTER TABLE products ADD COLUMN purchasing_price REAL NOT NULL DEFAULT 0')
            conn.commit()
        except sqlite3.OperationalError:
            # Column already exists, ignore
            pass
        
        # Sales table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                total_price REAL NOT NULL,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')
        
        # Stock logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                change_amount INTEGER NOT NULL,
                reason TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_logs_timestamp ON stock_logs(timestamp)')
        
        conn.commit()
        print("✅ Database initialized successfully")
        
        # Insert sample categories if they don't exist
        categories = [
            ('Electronics',),
            ('Clothing',),
            ('Food & Beverages',),
            ('Books',),
            ('Home & Garden',),
            ('Sports & Outdoors',),
            ('Toys & Games',),
            ('Health & Beauty',)
        ]
        cursor.executemany('INSERT OR IGNORE INTO categories (name) VALUES (?)', categories)
        conn.commit()
        
    except sqlite3.Error as e:
        print(f"❌ Database initialization error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


# ==================== DATABASE HELPER FUNCTIONS ====================

def get_db_connection():
    """Get a database connection with row factory for dict-like access"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This allows dict-like access to rows
    return conn


# ==================== UTILITY FUNCTIONS ====================

def format_error(message, status_code=400):
    """Format error response"""
    return jsonify({'error': message}), status_code


# ==================== DASHBOARD STATS ====================

@app.route('/api/dashboard-stats', methods=['GET'])
def dashboard_stats():
    """Get dashboard statistics including total value, low stock count, total orders, and 7-day sales trend"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total inventory value (at selling price)
        cursor.execute('''
            SELECT COALESCE(SUM(price * stock_quantity), 0) as total_value
            FROM products
        ''')
        total_value = cursor.fetchone()['total_value'] or 0.0
        
        # Total profit (selling price - purchasing price) * stock quantity
        cursor.execute('''
            SELECT COALESCE(SUM((price - COALESCE(purchasing_price, 0)) * stock_quantity), 0) as total_profit
            FROM products
        ''')
        total_profit = cursor.fetchone()['total_profit'] or 0.0
        
        # Low stock count (stock_quantity <= min_stock_level)
        cursor.execute('''
            SELECT COUNT(*) as low_stock_count
            FROM products
            WHERE stock_quantity <= min_stock_level
        ''')
        low_stock_count = cursor.fetchone()['low_stock_count']
        
        # Total orders (sales count)
        cursor.execute('SELECT COUNT(*) as total_orders FROM sales')
        total_orders = cursor.fetchone()['total_orders']
        
        # 7-day sales trend
        seven_days_ago = datetime.now() - timedelta(days=7)
        cursor.execute('''
            SELECT 
                DATE(sale_date) as sale_date,
                COALESCE(SUM(total_price), 0) as daily_total
            FROM sales
            WHERE sale_date >= ?
            GROUP BY DATE(sale_date)
            ORDER BY sale_date ASC
        ''', (seven_days_ago.isoformat(),))
        
        sales_data = {row['sale_date']: row['daily_total'] for row in cursor.fetchall()}
        
        # Create a complete 7-day array (fill missing days with 0)
        sales_trend = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=6-i)).date()
            date_str = date.isoformat()
            daily_sale = sales_data.get(date_str, 0.0)
            sales_trend.append({
                'date': date_str,
                'value': float(daily_sale)
            })
        
        conn.close()
        
        return jsonify({
            'total_value': round(total_value, 2),
            'total_profit': round(total_profit, 2),
            'low_stock_count': low_stock_count,
            'total_orders': total_orders,
            'sales_trend': sales_trend
        })
        
    except Exception as e:
        print(f"Error fetching dashboard stats: {e}")
        return format_error(f"Failed to fetch dashboard stats: {str(e)}", 500)


# ==================== PRODUCTS ====================

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products with optional search and low stock filter"""
    try:
        search = request.args.get('search', '').strip()
        low_stock_only = request.args.get('low_stock_only', 'false').lower() == 'true'
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                p.id,
                p.name,
                p.sku,
                p.category_id,
                c.name as category_name,
                p.price,
                p.purchasing_price,
                p.stock_quantity,
                p.min_stock_level,
                p.created_at,
                p.updated_at
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE 1=1
        '''
        params = []
        
        if search:
            query += " AND (p.name LIKE ? OR p.sku LIKE ?)"
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern])
        
        if low_stock_only:
            query += " AND p.stock_quantity <= p.min_stock_level"
        
        query += " ORDER BY p.name ASC"
        
        cursor.execute(query, params)
        products = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify(products)
        
    except Exception as e:
        print(f"Error fetching products: {e}")
        return format_error(f"Failed to fetch products: {str(e)}", 500)


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a single product by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                p.id,
                p.name,
                p.sku,
                p.category_id,
                c.name as category_name,
                p.price,
                p.purchasing_price,
                p.stock_quantity,
                p.min_stock_level
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.id = ?
        ''', (product_id,))
        
        product = cursor.fetchone()
        conn.close()
        
        if not product:
            return format_error("Product not found", 404)
        
        return jsonify(dict(product))
        
    except Exception as e:
        print(f"Error fetching product: {e}")
        return format_error(f"Failed to fetch product: {str(e)}", 500)


@app.route('/api/products', methods=['POST'])
def create_product():
    """Create a new product"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'sku', 'category_id', 'price', 'purchasing_price']
        for field in required_fields:
            if field not in data:
                return format_error(f"{field} is required", 400)
        
        name = data.get('name').strip()
        sku = data.get('sku').strip()
        category_id = data.get('category_id')
        price = float(data.get('price'))
        purchasing_price = float(data.get('purchasing_price', 0))
        stock_quantity = int(data.get('stock_quantity', 0))
        min_stock_level = int(data.get('min_stock_level', 5))
        
        if not name or not sku:
            return format_error("Name and SKU are required", 400)
        
        if price <= 0:
            return format_error("Price must be greater than 0", 400)
        
        if purchasing_price < 0:
            return format_error("Purchasing price cannot be negative", 400)
        
        if stock_quantity < 0:
            return format_error("Stock quantity cannot be negative", 400)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Check if SKU already exists
            cursor.execute('SELECT id FROM products WHERE sku = ?', (sku,))
            if cursor.fetchone():
                conn.close()
                return format_error("SKU already exists", 400)
            
            # Check if category exists
            cursor.execute('SELECT id FROM categories WHERE id = ?', (category_id,))
            if not cursor.fetchone():
                conn.close()
                return format_error("Category not found", 404)
            
            # Insert product
            cursor.execute('''
                INSERT INTO products (name, sku, category_id, price, purchasing_price, stock_quantity, min_stock_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, sku, category_id, price, purchasing_price, stock_quantity, min_stock_level))
            
            product_id = cursor.lastrowid
            
            # Log stock change if initial stock > 0
            if stock_quantity > 0:
                cursor.execute('''
                    INSERT INTO stock_logs (product_id, change_amount, reason, timestamp)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (product_id, stock_quantity, 'Initial stock'))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': f'Product "{name}" created successfully',
                'product_id': product_id
            }), 201
            
        except sqlite3.IntegrityError as e:
            conn.rollback()
            conn.close()
            return format_error("SKU already exists", 400)
            
    except ValueError as e:
        return format_error(f"Invalid value: {str(e)}", 400)
    except Exception as e:
        print(f"Error creating product: {e}")
        return format_error(f"Failed to create product: {str(e)}", 500)


@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update an existing product"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if product exists
        cursor.execute('SELECT id FROM products WHERE id = ?', (product_id,))
        if not cursor.fetchone():
            conn.close()
            return format_error("Product not found", 404)
        
        # Build update query dynamically based on provided fields
        updates = []
        params = []
        
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                conn.close()
                return format_error("Name cannot be empty", 400)
            updates.append('name = ?')
            params.append(name)
        
        if 'sku' in data:
            sku = data['sku'].strip()
            if not sku:
                conn.close()
                return format_error("SKU cannot be empty", 400)
            # Check if SKU is already used by another product
            cursor.execute('SELECT id FROM products WHERE sku = ? AND id != ?', (sku, product_id))
            if cursor.fetchone():
                conn.close()
                return format_error("SKU already exists", 400)
            updates.append('sku = ?')
            params.append(sku)
        
        if 'category_id' in data:
            category_id = data['category_id']
            # Check if category exists
            cursor.execute('SELECT id FROM categories WHERE id = ?', (category_id,))
            if not cursor.fetchone():
                conn.close()
                return format_error("Category not found", 404)
            updates.append('category_id = ?')
            params.append(category_id)
        
        if 'price' in data:
            price = float(data['price'])
            if price <= 0:
                conn.close()
                return format_error("Price must be greater than 0", 400)
            updates.append('price = ?')
            params.append(price)
        
        if 'purchasing_price' in data:
            purchasing_price = float(data['purchasing_price'])
            if purchasing_price < 0:
                conn.close()
                return format_error("Purchasing price cannot be negative", 400)
            updates.append('purchasing_price = ?')
            params.append(purchasing_price)
        
        if 'stock_quantity' in data:
            stock_quantity = int(data['stock_quantity'])
            if stock_quantity < 0:
                conn.close()
                return format_error("Stock quantity cannot be negative", 400)
            # Get current stock to calculate change
            cursor.execute('SELECT stock_quantity FROM products WHERE id = ?', (product_id,))
            current_stock = cursor.fetchone()['stock_quantity']
            stock_change = stock_quantity - current_stock
            updates.append('stock_quantity = ?')
            params.append(stock_quantity)
        
        if 'min_stock_level' in data:
            min_stock_level = int(data['min_stock_level'])
            if min_stock_level < 0:
                conn.close()
                return format_error("Min stock level cannot be negative", 400)
            updates.append('min_stock_level = ?')
            params.append(min_stock_level)
        
        if not updates:
            conn.close()
            return format_error("No fields to update", 400)
        
        # Add updated_at timestamp
        updates.append('updated_at = CURRENT_TIMESTAMP')
        
        # Add product_id to params
        params.append(product_id)
        
        # Execute update
        query = f'UPDATE products SET {", ".join(updates)} WHERE id = ?'
        cursor.execute(query, params)
        
        # Log stock change if stock_quantity was updated
        if 'stock_quantity' in data and stock_change != 0:
            reason = 'Stock adjustment' if stock_change > 0 else 'Stock reduction'
            cursor.execute('''
                INSERT INTO stock_logs (product_id, change_amount, reason, timestamp)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (product_id, stock_change, reason))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Product updated successfully'
        }), 200
        
    except ValueError as e:
        return format_error(f"Invalid value: {str(e)}", 400)
    except Exception as e:
        print(f"Error updating product: {e}")
        return format_error(f"Failed to update product: {str(e)}", 500)


# ==================== SALES ====================

@app.route('/api/add-sale', methods=['POST'])
def add_sale():
    """
    Record a sale with atomic transaction.
    Deducts stock and logs the sale in a single transaction.
    """
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        
        if not product_id or not quantity:
            return format_error("product_id and quantity are required", 400)
        
        if quantity <= 0:
            return format_error("Quantity must be greater than 0", 400)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Start transaction (SQLite uses implicit transactions)
        try:
            # Get current product stock (with lock)
            cursor.execute('''
                SELECT stock_quantity, price, name
                FROM products
                WHERE id = ?
            ''', (product_id,))
            
            product = cursor.fetchone()
            if not product:
                conn.rollback()
                conn.close()
                return format_error("Product not found", 404)
            
            current_stock = product['stock_quantity']
            price = product['price']
            product_name = product['name']
            
            # Check if sufficient stock
            if current_stock < quantity:
                conn.rollback()
                conn.close()
                return format_error(
                    f"Insufficient stock. Available: {current_stock}, Requested: {quantity}",
                    400
                )
            
            # Calculate total price
            total_price = price * quantity
            
            # Deduct stock
            new_stock = current_stock - quantity
            cursor.execute('''
                UPDATE products
                SET stock_quantity = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_stock, product_id))
            
            # Record sale
            cursor.execute('''
                INSERT INTO sales (product_id, quantity, total_price, sale_date)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (product_id, quantity, total_price))
            
            sale_id = cursor.lastrowid
            
            # Log stock change
            cursor.execute('''
                INSERT INTO stock_logs (product_id, change_amount, reason, timestamp)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (product_id, -quantity, f"Sale #{sale_id}"))
            
            # Commit transaction
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'sale_id': sale_id,
                'message': f"Sale recorded: {quantity} x {product_name}",
                'total_price': round(total_price, 2),
                'remaining_stock': new_stock
            }), 201
            
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
                
    except Exception as e:
        print(f"Error recording sale: {e}")
        return format_error(f"Failed to record sale: {str(e)}", 500)


@app.route('/api/sales', methods=['GET'])
def get_sales():
    """Get all sales with optional date range"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                s.id,
                s.product_id,
                p.name as product_name,
                p.sku,
                s.quantity,
                s.total_price,
                s.sale_date
            FROM sales s
            JOIN products p ON s.product_id = p.id
            ORDER BY s.sale_date DESC
            LIMIT 100
        ''')
        
        sales = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify(sales)
        
    except Exception as e:
        print(f"Error fetching sales: {e}")
        return format_error(f"Failed to fetch sales: {str(e)}", 500)


# ==================== STOCK MANAGEMENT ====================

@app.route('/api/restock', methods=['POST'])
def restock():
    """Increase stock levels for a product"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        reason = data.get('reason', 'Manual restock')
        
        if not product_id or not quantity:
            return format_error("product_id and quantity are required", 400)
        
        if quantity <= 0:
            return format_error("Quantity must be greater than 0", 400)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Start transaction
        try:
            # Get current product
            cursor.execute('''
                SELECT stock_quantity, name
                FROM products
                WHERE id = ?
            ''', (product_id,))
            
            product = cursor.fetchone()
            if not product:
                conn.rollback()
                conn.close()
                return format_error("Product not found", 404)
            
            current_stock = product['stock_quantity']
            product_name = product['name']
            
            # Update stock
            new_stock = current_stock + quantity
            cursor.execute('''
                UPDATE products
                SET stock_quantity = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_stock, product_id))
            
            # Log stock change
            cursor.execute('''
                INSERT INTO stock_logs (product_id, change_amount, reason, timestamp)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (product_id, quantity, reason))
            
            # Commit transaction
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': f"Restocked {quantity} units of {product_name}",
                'new_stock': new_stock
            }), 200
            
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
                
    except Exception as e:
        print(f"Error restocking: {e}")
        return format_error(f"Failed to restock: {str(e)}", 500)


# ==================== CATEGORIES ====================

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM categories ORDER BY name ASC')
        categories = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(categories)
        
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return format_error(f"Failed to fetch categories: {str(e)}", 500)


# ==================== PDF EXPORT ====================

@app.route('/api/export-pdf', methods=['GET'])
def export_pdf():
    """Generate a professional PDF inventory report"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Fetch all products with categories
        cursor.execute('''
            SELECT 
                p.sku,
                p.name,
                c.name as category_name,
                p.price,
                p.stock_quantity,
                p.min_stock_level,
                CASE 
                    WHEN p.stock_quantity = 0 THEN 'Out of Stock'
                    WHEN p.stock_quantity <= p.min_stock_level THEN 'Low Stock'
                    ELSE 'In Stock'
                END as status
            FROM products p
            JOIN categories c ON p.category_id = c.id
            ORDER BY p.name ASC
        ''')
        
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        # Title
        title = Paragraph("Enterprise Smart-IMS Inventory Report", title_style)
        elements.append(title)
        
        # Report date
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#64748b'),
            alignment=1
        )
        date_text = Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", date_style)
        elements.append(date_text)
        elements.append(Spacer(1, 0.3*inch))
        
        # Prepare table data
        table_data = [['SKU', 'Product Name', 'Category', 'Price', 'Stock', 'Min Level', 'Status']]
        
        for product in products:
            status = product['status']
            row = [
                product['sku'],
                product['name'],
                product['category_name'],
                f"${float(product['price']):.2f}",
                str(product['stock_quantity']),
                str(product['min_stock_level']),
                status
            ]
            table_data.append(row)
        
        # Create table
        table = Table(table_data, colWidths=[1*inch, 2*inch, 1.2*inch, 0.8*inch, 0.7*inch, 0.8*inch, 1*inch])
        
        # Style the table
        table_style = TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
        ])
        
        # Color code status column
        for i, product in enumerate(products, start=1):
            status = product['status']
            if status == 'Out of Stock':
                table_style.add('TEXTCOLOR', (6, i), (6, i), colors.HexColor('#dc2626'))
            elif status == 'Low Stock':
                table_style.add('TEXTCOLOR', (6, i), (6, i), colors.HexColor('#ca8a04'))
            else:
                table_style.add('TEXTCOLOR', (6, i), (6, i), colors.HexColor('#16a34a'))
        
        table.setStyle(table_style)
        elements.append(table)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        # Return PDF
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'inventory_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return format_error(f"Failed to generate PDF: {str(e)}", 500)


# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        if os.path.exists(DB_PATH):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            cursor.fetchone()
            conn.close()
            return jsonify({'status': 'healthy', 'database': 'connected'})
        else:
            return jsonify({'status': 'unhealthy', 'database': 'not_found'}), 503
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ==================== INITIALIZE DATABASE ON STARTUP ====================

if __name__ == '__main__':
    print("🚀 Starting Enterprise Smart-IMS Backend...")
    print("📦 Initializing database...")
    init_db()
    print("✅ Database ready!")
    print("🌐 API available at http://localhost:5000")
    app.run(debug=True, port=5000)

