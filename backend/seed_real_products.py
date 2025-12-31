"""
Seed script to populate inventory.db with 121 real-life products
"""

import sqlite3
import random
import os

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'inventory.db')


def init_db_if_needed():
    """Initialize the database and create tables if they don't exist"""
    print("  Initializing database...")
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
                stock_quantity INTEGER NOT NULL DEFAULT 0,
                min_stock_level INTEGER NOT NULL DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')
        
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
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_logs_timestamp ON stock_logs(timestamp)')
        
        conn.commit()
        print("  ✅ Database initialized")
    except Exception as e:
        print(f"  ⚠️  Error initializing: {e}")
    finally:
        conn.close()


def seed_real_products():
    """Seed the database with 121 real-life products"""
    # Initialize database if needed
    init_db_if_needed()
    
    conn = None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print("🔄 Starting database seeding with 121 real products...")

        # 1. Clear existing products and sales (keep categories)
        print("  Clearing existing products and sales...")
        try:
            cursor.execute("DELETE FROM sales")
            cursor.execute("DELETE FROM stock_logs")
            cursor.execute("DELETE FROM products")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('products', 'sales', 'stock_logs')")
            conn.commit()
        except sqlite3.OperationalError:
            # Tables don't exist yet, that's okay
            pass

        # 2. Get or create categories
        categories_map = {}
        category_list = [
            ('Home & Kitchen',),
            ('Electronics',),
            ('Fitness & Outdoors',),
            ('Health & Personal Care',),
            ('Office & Hobby',),
            ('Apparel & Lifestyle',),
        ]
        
        # Insert categories if they don't exist
        for cat_name in category_list:
            cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", cat_name)
            cursor.execute("SELECT id FROM categories WHERE name = ?", (cat_name[0],))
            categories_map[cat_name[0]] = cursor.fetchone()[0]
        
        conn.commit()
        print(f"  ✅ Categories ready")

        # 3. Define all 121 products with categories
        products_data = [
            # 🏠 Home & Kitchen (20)
            ("Air Fryer 5.5L", "HOME", categories_map['Home & Kitchen'], 89.99),
            ("Non-Stick Cookware Set (12-Piece)", "HOME", categories_map['Home & Kitchen'], 149.99),
            ("Electric Kettle (1.7L)", "HOME", categories_map['Home & Kitchen'], 34.99),
            ("Memory Foam Pillow", "HOME", categories_map['Home & Kitchen'], 29.99),
            ("Blackout Curtains (Set of 2)", "HOME", categories_map['Home & Kitchen'], 45.99),
            ("Digital Food Scale", "HOME", categories_map['Home & Kitchen'], 19.99),
            ("French Press Coffee Maker", "HOME", categories_map['Home & Kitchen'], 24.99),
            ("Bamboo Cutting Board", "HOME", categories_map['Home & Kitchen'], 18.99),
            ("Microfiber Cleaning Cloths (10-Pack)", "HOME", categories_map['Home & Kitchen'], 12.99),
            ("Magnetic Knife Strip", "HOME", categories_map['Home & Kitchen'], 22.99),
            ("Spice Rack Organizer", "HOME", categories_map['Home & Kitchen'], 16.99),
            ("Silicone Baking Mats", "HOME", categories_map['Home & Kitchen'], 14.99),
            ("Food Storage Containers (Glass)", "HOME", categories_map['Home & Kitchen'], 39.99),
            ("Handheld Milk Frother", "HOME", categories_map['Home & Kitchen'], 15.99),
            ("Dish Drying Rack", "HOME", categories_map['Home & Kitchen'], 27.99),
            ("Automatic Soap Dispenser", "HOME", categories_map['Home & Kitchen'], 32.99),
            ("Cast Iron Skillet (12-inch)", "HOME", categories_map['Home & Kitchen'], 49.99),
            ("Toaster Oven", "HOME", categories_map['Home & Kitchen'], 79.99),
            ("Electric Salt and Pepper Grinder", "HOME", categories_map['Home & Kitchen'], 44.99),
            ("Vegetable Spiralizer", "HOME", categories_map['Home & Kitchen'], 19.99),
            
            # 💻 Electronics & Tech (25)
            ("Mechanical Keyboard (RGB)", "ELEC", categories_map['Electronics'], 129.99),
            ("Wireless Ergonomic Mouse", "ELEC", categories_map['Electronics'], 59.99),
            ("4K Ultra HD Monitor (27-inch)", "ELEC", categories_map['Electronics'], 299.99),
            ("USB-C Docking Station", "ELEC", categories_map['Electronics'], 89.99),
            ("Noise Cancelling Headphones", "ELEC", categories_map['Electronics'], 199.99),
            ("Portable SSD (1TB)", "ELEC", categories_map['Electronics'], 89.99),
            ("Smart Wi-Fi Plug", "ELEC", categories_map['Electronics'], 24.99),
            ("Ring Light with Tripod", "ELEC", categories_map['Electronics'], 49.99),
            ("Webcam (1080p)", "ELEC", categories_map['Electronics'], 69.99),
            ("Bluetooth Speaker (Waterproof)", "ELEC", categories_map['Electronics'], 79.99),
            ("Laptop Stand (Aluminum)", "ELEC", categories_map['Electronics'], 39.99),
            ("Tablet Stylus Pen", "ELEC", categories_map['Electronics'], 29.99),
            ("Wireless Charging Pad", "ELEC", categories_map['Electronics'], 19.99),
            ("Smart Home Camera", "ELEC", categories_map['Electronics'], 89.99),
            ("Gaming Headset", "ELEC", categories_map['Electronics'], 79.99),
            ("Graphic Drawing Tablet", "ELEC", categories_map['Electronics'], 149.99),
            ("Power Bank (20,000 mAh)", "ELEC", categories_map['Electronics'], 34.99),
            ("HDMI 2.1 Cable (6ft)", "ELEC", categories_map['Electronics'], 14.99),
            ("Universal Travel Adapter", "ELEC", categories_map['Electronics'], 19.99),
            ("Smart LED Strip Lights", "ELEC", categories_map['Electronics'], 24.99),
            ("Tile Bluetooth Tracker", "ELEC", categories_map['Electronics'], 29.99),
            ("Lap Desk with Cushion", "ELEC", categories_map['Electronics'], 34.99),
            ("Desktop Cable Organizer", "ELEC", categories_map['Electronics'], 12.99),
            ("VR Headset (Standalone)", "ELEC", categories_map['Electronics'], 399.99),
            ("E-Reader (6-inch Display)", "ELEC", categories_map['Electronics'], 119.99),
            
            # 🏃 Fitness & Outdoors (20)
            ("Yoga Mat (Eco-Friendly)", "FIT", categories_map['Fitness & Outdoors'], 24.99),
            ("Adjustable Dumbbell Set", "FIT", categories_map['Fitness & Outdoors'], 199.99),
            ("Resistance Bands (5-Pack)", "FIT", categories_map['Fitness & Outdoors'], 19.99),
            ("Foam Roller (High Density)", "FIT", categories_map['Fitness & Outdoors'], 22.99),
            ("Hydro Flask Water Bottle (32oz)", "FIT", categories_map['Fitness & Outdoors'], 34.99),
            ("Microfiber Travel Towel", "FIT", categories_map['Fitness & Outdoors'], 16.99),
            ("Camping Hammock", "FIT", categories_map['Fitness & Outdoors'], 39.99),
            ("Headlamp Flashlight", "FIT", categories_map['Fitness & Outdoors'], 24.99),
            ("Running Waist Pack", "FIT", categories_map['Fitness & Outdoors'], 19.99),
            ("Jump Rope (Speed)", "FIT", categories_map['Fitness & Outdoors'], 14.99),
            ("Pull-Up Bar (Doorway)", "FIT", categories_map['Fitness & Outdoors'], 29.99),
            ("Inflatable Kayak", "FIT", categories_map['Fitness & Outdoors'], 149.99),
            ("Picnic Blanket (Waterproof)", "FIT", categories_map['Fitness & Outdoors'], 34.99),
            ("Binoculars (10x42)", "FIT", categories_map['Fitness & Outdoors'], 89.99),
            ("Hydration Bladder (2L)", "FIT", categories_map['Fitness & Outdoors'], 24.99),
            ("Dry Bag (10L)", "FIT", categories_map['Fitness & Outdoors'], 19.99),
            ("Folding Camping Chair", "FIT", categories_map['Fitness & Outdoors'], 44.99),
            ("Portable Gas Stove", "FIT", categories_map['Fitness & Outdoors'], 39.99),
            ("Trekking Poles (Carbon Fiber)", "FIT", categories_map['Fitness & Outdoors'], 79.99),
            ("Fitness Tracker Watch", "FIT", categories_map['Fitness & Outdoors'], 149.99),
            
            # 💄 Health & Personal Care (20)
            ("Electric Toothbrush", "HEALTH", categories_map['Health & Personal Care'], 49.99),
            ("Essential Oil Diffuser", "HEALTH", categories_map['Health & Personal Care'], 29.99),
            ("Jade Roller & Gua Sha Set", "HEALTH", categories_map['Health & Personal Care'], 19.99),
            ("Rechargeable Beard Trimmer", "HEALTH", categories_map['Health & Personal Care'], 39.99),
            ("Silk Eye Mask", "HEALTH", categories_map['Health & Personal Care'], 14.99),
            ("Deep Tissue Massage Gun", "HEALTH", categories_map['Health & Personal Care'], 99.99),
            ("Foot Spa Massager", "HEALTH", categories_map['Health & Personal Care'], 44.99),
            ("UV Nail Lamp", "HEALTH", categories_map['Health & Personal Care'], 24.99),
            ("Hair Straightener (Ceramic)", "HEALTH", categories_map['Health & Personal Care'], 34.99),
            ("Digital Thermometer", "HEALTH", categories_map['Health & Personal Care'], 12.99),
            ("Hand Sanitizer (Pack of 5)", "HEALTH", categories_map['Health & Personal Care'], 9.99),
            ("Makeup Mirror (Lighted)", "HEALTH", categories_map['Health & Personal Care'], 29.99),
            ("First Aid Kit (100-Piece)", "HEALTH", categories_map['Health & Personal Care'], 24.99),
            ("Pulse Oximeter", "HEALTH", categories_map['Health & Personal Care'], 19.99),
            ("Electric Heating Pad", "HEALTH", categories_map['Health & Personal Care'], 34.99),
            ("Sonic Facial Cleansing Brush", "HEALTH", categories_map['Health & Personal Care'], 39.99),
            ("Wet/Dry Electric Shaver", "HEALTH", categories_map['Health & Personal Care'], 59.99),
            ("Water Flosser", "HEALTH", categories_map['Health & Personal Care'], 49.99),
            ("Sleep Sound Machine (White Noise)", "HEALTH", categories_map['Health & Personal Care'], 39.99),
            ("Humidifier (Cool Mist)", "HEALTH", categories_map['Health & Personal Care'], 44.99),
            
            # 📚 Office & Hobby (20)
            ("Fountain Pen (Fine Nib)", "OFFICE", categories_map['Office & Hobby'], 24.99),
            ("Bullet Journal (Dotted)", "OFFICE", categories_map['Office & Hobby'], 16.99),
            ("Dual Brush Marker Pens (12-Color)", "OFFICE", categories_map['Office & Hobby'], 19.99),
            ("Desktop Paper Shredder", "OFFICE", categories_map['Office & Hobby'], 79.99),
            ("Standing Desk Converter", "OFFICE", categories_map['Office & Hobby'], 199.99),
            ("Acrylic Paint Set (24-Color)", "OFFICE", categories_map['Office & Hobby'], 29.99),
            ("Watercolor Paper Pad", "OFFICE", categories_map['Office & Hobby'], 14.99),
            ("Stapleless Stapler", "OFFICE", categories_map['Office & Hobby'], 12.99),
            ("Mesh Ergonomic Office Chair", "OFFICE", categories_map['Office & Hobby'], 149.99),
            ("Under-Desk Footrest", "OFFICE", categories_map['Office & Hobby'], 24.99),
            ("Drawing Pencil Set (H-B)", "OFFICE", categories_map['Office & Hobby'], 12.99),
            ("Blue Light Blocking Glasses", "OFFICE", categories_map['Office & Hobby'], 19.99),
            ("Magnetic Whiteboard", "OFFICE", categories_map['Office & Hobby'], 34.99),
            ("Weekly Planner Pad", "OFFICE", categories_map['Office & Hobby'], 9.99),
            ("Sticky Note Dispenser", "OFFICE", categories_map['Office & Hobby'], 14.99),
            ("Laminator Machine", "OFFICE", categories_map['Office & Hobby'], 39.99),
            ("3D Printing Filament (PLA)", "OFFICE", categories_map['Office & Hobby'], 24.99),
            ("Calligraphy Starter Kit", "OFFICE", categories_map['Office & Hobby'], 29.99),
            ("Photo Studio Box (Portable)", "OFFICE", categories_map['Office & Hobby'], 49.99),
            ("Cork Bulletin Board", "OFFICE", categories_map['Office & Hobby'], 34.99),
            
            # 🚗 Apparel & Lifestyle (16)
            ("Minimalist Slim Wallet (RFID)", "APP", categories_map['Apparel & Lifestyle'], 24.99),
            ("Canvas Backpack (Anti-theft)", "APP", categories_map['Apparel & Lifestyle'], 49.99),
            ("Aviator Sunglasses", "APP", categories_map['Apparel & Lifestyle'], 34.99),
            ("Leather Belt (Reversible)", "APP", categories_map['Apparel & Lifestyle'], 29.99),
            ("No-Show Socks (6-Pack)", "APP", categories_map['Apparel & Lifestyle'], 12.99),
            ("Compression Packing Cubes", "APP", categories_map['Apparel & Lifestyle'], 34.99),
            ("Gym Duffel Bag", "APP", categories_map['Apparel & Lifestyle'], 39.99),
            ("Laptop Sleeve (Padded)", "APP", categories_map['Apparel & Lifestyle'], 19.99),
            ("Wool Scarf", "APP", categories_map['Apparel & Lifestyle'], 24.99),
            ("Baseball Cap (Cotton)", "APP", categories_map['Apparel & Lifestyle'], 16.99),
            ("Rain Poncho (Reusable)", "APP", categories_map['Apparel & Lifestyle'], 14.99),
            ("Watch Box Organizer", "APP", categories_map['Apparel & Lifestyle'], 29.99),
            ("Shoe Tree (Cedar)", "APP", categories_map['Apparel & Lifestyle'], 19.99),
            ("Umbrella (Windproof)", "APP", categories_map['Apparel & Lifestyle'], 24.99),
            ("Knit Beanie", "APP", categories_map['Apparel & Lifestyle'], 14.99),
            ("Tote Bag (Heavy Duty)", "APP", categories_map['Apparel & Lifestyle'], 19.99),
        ]

        # 4. Insert products with unique SKUs
        print("  Adding 121 products...")
        inserted_products = []
        
        for idx, (name, prefix, category_id, base_price) in enumerate(products_data, 1):
            # Generate unique SKU: PREFIX-XXXX-YYY
            sku = f"{prefix}-{random.randint(1000, 9999)}-{idx:03d}"
            
            # Add some price variation (±10%)
            price_variation = random.uniform(0.9, 1.1)
            price = round(base_price * price_variation, 2)
            
            # Ensure price is between $10 and $500
            price = max(10.0, min(500.0, price))
            
            # Calculate purchasing price (60-80% of selling price for realistic profit)
            purchasing_price = round(price * random.uniform(0.6, 0.8), 2)
            
            # Random stock quantity between 0 and 100
            stock_quantity = random.randint(0, 100)
            
            # Min stock level (10-20% of a typical stock level)
            min_stock_level = random.randint(5, 20)
            
            inserted_products.append((name, sku, category_id, price, purchasing_price, stock_quantity, min_stock_level))

        cursor.executemany(
            "INSERT INTO products (name, sku, category_id, price, purchasing_price, stock_quantity, min_stock_level) VALUES (?, ?, ?, ?, ?, ?, ?)",
            inserted_products
        )
        conn.commit()
        print(f"  ✅ Added {len(inserted_products)} products")

        # 5. Add some sales for the last 7 days
        print("  Adding sales data...")
        sales = []
        product_ids = list(range(1, len(inserted_products) + 1))
        
        from datetime import datetime, timedelta
        for day_offset in range(7):
            date = datetime.now() - timedelta(days=day_offset)
            # Create 5-15 sales per day
            num_sales = random.randint(5, 15)
            
            for _ in range(num_sales):
                p_id = random.choice(product_ids)
                qty = random.randint(1, 5)
                # Get product price
                cursor.execute("SELECT price FROM products WHERE id = ?", (p_id,))
                price_result = cursor.fetchone()
                if price_result:
                    unit_price = float(price_result[0])
                    total_price = round(unit_price * qty, 2)
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

        print("\n✅ Database seeded successfully!")
        print(f"   - {len(category_list)} categories")
        print(f"   - {len(inserted_products)} products")
        print(f"   - {len(sales)} sales records")
        
        # Show summary by category
        print("\n📊 Products by category:")
        for cat_name, cat_id in categories_map.items():
            cursor.execute("SELECT COUNT(*) FROM products WHERE category_id = ?", (cat_id,))
            count = cursor.fetchone()[0]
            print(f"   - {cat_name}: {count} products")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("\n  Database connection closed")


if __name__ == "__main__":
    seed_real_products()

