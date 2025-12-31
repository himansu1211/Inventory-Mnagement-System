"""
Quick test script to verify the server setup
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    print("Testing imports...")
    from app import app, init_db, get_db_connection
    print("✅ All imports successful")
    
    print("\nTesting database initialization...")
    init_db()
    print("✅ Database initialized")
    
    print("\nTesting database connection...")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()[0]
    print(f"✅ Database connected - Found {product_count} products")
    conn.close()
    
    print("\n✅ All tests passed! Server is ready to run.")
    print("\nTo start the server, run: python app.py")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

