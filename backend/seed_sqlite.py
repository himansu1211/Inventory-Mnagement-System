"""
Database seeding script for Enterprise Smart-IMS (SQLite)
Populates the database with sample data for testing and development
"""

import sqlite3
import random
import os
from datetime import datetime, timedelta

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'inventory.db')


def seed():
    """Seed the database with sample data"""
    conn = None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print("🔄 Starting database seeding...")

        # 1. Clear existing data (Careful! This resets the DB)
        print("  Clearing existing data...")
        cursor.execute("DELETE FROM sales")
        cursor.execute("DELETE FROM stock_logs")
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM categories")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('categories', 'products', 'sales', 'stock_logs')")
        conn.commit()

        # 2. Add Categories
        print("  Adding categories...")
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
        cursor.executemany("INSERT INTO categories (name) VALUES (?)", categories)
        conn.commit()
        print(f"  ✅ Added {len(categories)} categories")

        # 3. Add 50 Products with realistic names
        print("  Adding products...")
        product_names = [
            # Electronics
            'Laptop Pro 15', 'Wireless Mouse', 'USB-C Cable', 'Bluetooth Headphones', 
            'Smart Watch', 'Tablet 10"', 'Keyboard Mechanical', 'Webcam HD',
            'External SSD 1TB', 'Power Bank 20000mAh',
            # Clothing
            'Cotton T-Shirt', 'Denim Jeans', 'Hoodie', 'Running Shoes',
            'Winter Jacket', 'Baseball Cap', 'Socks Pack', 'Belt Leather',
            'Dress Shirt', 'Sneakers',
            # Food & Beverages
            'Coffee Beans 1kg', 'Green Tea 100g', 'Chocolate Bar', 'Energy Drink',
            'Protein Powder', 'Olive Oil 500ml', 'Honey 250g', 'Granola Bars',
            'Instant Noodles', 'Cereal Box',
            # Books
            'Python Programming', 'React Guide', 'JavaScript Mastery', 'Database Design',
            'Web Development', 'Data Structures', 'Algorithms', 'System Design',
            'Machine Learning', 'Cloud Computing',
            # Home & Garden
            'Garden Tools Set', 'Plant Pot Ceramic', 'Watering Can', 'Garden Hose',
            'Lawn Mower', 'Pruning Shears', 'Garden Gloves', 'Fertilizer 5kg',
            'Seeds Pack', 'Garden Bench',
            # Sports & Outdoors
            'Yoga Mat', 'Dumbbells 10kg', 'Basketball', 'Tennis Racket',
            'Camping Tent', 'Sleeping Bag', 'Backpack 30L', 'Hiking Boots',
            'Bicycle Helmet', 'Water Bottle'
        ]
        
        products = []
        category_ids = list(range(1, 9))  # 8 categories
        
        for i, name in enumerate(product_names[:50], 1):
            cat_id = random.choice(category_ids)
            sku = f"SKU-{random.randint(1000, 9999)}-{i:03d}"
            price = round(random.uniform(10.0, 500.0), 2)
            stock = random.randint(0, 100)
            min_stock = random.randint(5, 20)
            products.append((name, sku, cat_id, price, stock, min_stock))

        cursor.executemany(
            "INSERT INTO products (name, sku, category_id, price, stock_quantity, min_stock_level) VALUES (?, ?, ?, ?, ?, ?)",
            products
        )
        conn.commit()
        print(f"  ✅ Added {len(products)} products")

        # 4. Add Sales for the last 7 days (for the Chart)
        print("  Adding sales data...")
        sales = []
        product_ids = list(range(1, 51))  # 50 products
        
        for day_offset in range(7):
            date = datetime.now() - timedelta(days=day_offset)
            # Create 5-15 sales per day
            num_sales = random.randint(5, 15)
            
            for _ in range(num_sales):
                p_id = random.choice(product_ids)
                qty = random.randint(1, 5)
                # Get product price for realistic total
                cursor.execute("SELECT price FROM products WHERE id = ?", (p_id,))
                price_result = cursor.fetchone()
                if price_result:
                    unit_price = float(price_result[0])
                    total_price = round(unit_price * qty, 2)
                    # Set specific time for the sale
                    sale_datetime = date.replace(
                        hour=random.randint(9, 18),
                        minute=random.randint(0, 59),
                        second=random.randint(0, 59)
                    )
                    sales.append((p_id, qty, total_price, sale_datetime.isoformat()))

        cursor.executemany(
            "INSERT INTO sales (product_id, quantity, total_price, sale_date) VALUES (?, ?, ?, ?)",
            sales
        )
        conn.commit()
        print(f"  ✅ Added {len(sales)} sales records")

        # 5. Add some stock logs for history
        print("  Adding stock logs...")
        stock_logs = []
        for product_id in random.sample(product_ids, 20):  # Random 20 products
            change_amount = random.randint(10, 50)
            reasons = [
                'Initial stock',
                'Restock from supplier',
                'Returned items',
                'Inventory adjustment',
                'Bulk purchase'
            ]
            reason = random.choice(reasons)
            timestamp = (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            stock_logs.append((product_id, change_amount, reason, timestamp))

        cursor.executemany(
            "INSERT INTO stock_logs (product_id, change_amount, reason, timestamp) VALUES (?, ?, ?, ?)",
            stock_logs
        )
        conn.commit()
        print(f"  ✅ Added {len(stock_logs)} stock log entries")

        print("\n✅ Database seeded successfully!")
        print(f"   - {len(categories)} categories")
        print(f"   - {len(products)} products")
        print(f"   - {len(sales)} sales records")
        print(f"   - {len(stock_logs)} stock log entries")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("  Database connection closed")


if __name__ == "__main__":
    seed()

