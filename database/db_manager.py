import sqlite3
import os

DB_PATH = os.path.join("data", "vendove_store.db")

def inicializar_db_vendove():
    # Asegurar que la carpeta data exista
    os.makedirs("data", exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabla EXACTA según tu definición (simplificada para SQLite)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id_product INTEGER PRIMARY KEY AUTOINCREMENT,
            state_product TEXT DEFAULT 'show',
            name_product TEXT,
            image_product TEXT,
            price_product REAL DEFAULT 0,
            stock_product INTEGER DEFAULT 0,
            sales_product INTEGER DEFAULT 0,
            description_product TEXT,
            summary_product TEXT
        )
    ''')
    
    # Datos semilla de prueba
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        print("Insertando datos de prueba...")
        productos_fake = [
            ('show', 'Camiseta VendoVe Oficial', 'tshirt.jpg', 25.00, 50, 120, 'Algodón 100%'),
            ('show', 'Zapatillas Running Pro', 'shoes.jpg', 89.99, 10, 5, 'Para correr'),
            ('show', 'Gorra Urbana', 'cap.jpg', 15.50, 0, 45, 'Estilo urbano'),
            ('hide', 'Producto Oculto Test', '', 10.00, 100, 0, 'No debe verse')
        ]
        cursor.executemany("""
            INSERT INTO products (state_product, name_product, image_product, price_product, stock_product, sales_product, summary_product) 
            VALUES (?,?,?,?,?,?,?)
        """, productos_fake)
        conn.commit()
    
    conn.close()
    print(f"Base de datos inicializada en: {DB_PATH}")


    # --- MODO PRODUCCIÓN (MySQL Real) ---
# Para usar tu BD real, instalarías: pip install mysql-connector-python
# Y usarías esta función en lugar de la anterior:
"""
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="vendove"
    )
"""