import sqlite3
import os
import json

# Obtiene la ruta de la carpeta actual ('database/') y sube un nivel a la raíz ('vendove-ai-bot/')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

DB_PATH = os.path.join(ROOT_DIR, "data", "vendove_store.db")
JSON_PATH = os.path.join(ROOT_DIR, "data", "productos.json")

def inicializar_db_vendove():
    # Asegurar que la carpeta data exista
    os.makedirs(os.path.join(ROOT_DIR, "data"), exist_ok=True)

    # Leer el archivo JSON, cargamos los datos de prueba para BD
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    conn = sqlite3.connect(DB_PATH)
    # IMPORTANTE: En SQLite las foreign keys deben habilitarse por conexión
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # --- RESETEAR TABLAS PARA DESARROLLO ---
    # Esto borra las tablas viejas para aplicar la nueva estructura limpia
    cursor.execute("DROP TABLE IF EXISTS products;")
    cursor.execute("DROP TABLE IF EXISTS categories;")
    
    # 1. Tabla de Categorías
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id_category INTEGER PRIMARY KEY AUTOINCREMENT,
            name_category TEXT NOT NULL UNIQUE,
            description_category TEXT
        )
    ''')

    # 2. Tabla de Productos con relación a la categoría
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id_product INTEGER PRIMARY KEY AUTOINCREMENT,
            state_product TEXT DEFAULT 'show',
            name_product TEXT NOT NULL,
            image_product TEXT,
            price_product REAL DEFAULT 0,
            stock_product INTEGER DEFAULT 0,
            sales_product INTEGER DEFAULT 0,
            description_product TEXT,
            summary_product TEXT,
            category_id INTEGER,
            CONSTRAINT fk_products_categories 
                FOREIGN KEY (category_id) 
                REFERENCES categories(id_category) 
                ON DELETE SET NULL
        )
    ''')
    
  # 3. Cargar Categorías desde el JSON si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        print("Insertando categorías desde el JSON...")
        categorias_tuplas = [
            (cat['name_category'], cat['description_category']) 
            for cat in data.get('categories', [])
        ]
        cursor.executemany("""
            INSERT INTO categories (name_category, description_category) 
            VALUES (?, ?)
        """, categorias_tuplas)
        conn.commit()

  # 4. Cargar Productos desde el JSON si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        print("Insertando productos desde el JSON...")
        productos_tuplas = [
            (
                p['state_product'], 
                p['name_product'], 
                p['image_product'], 
                p['price_product'], 
                p['stock_product'], 
                p['sales_product'], 
                p['description_product'], 
                p['summary_product'], 
                p['category_id']
            ) 
            for p in data.get('products', [])
        ]
        cursor.executemany("""
            INSERT INTO products (
                state_product, name_product, image_product, price_product, 
                stock_product, sales_product, description_product, summary_product, category_id
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, productos_tuplas)
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

def probar_conexion_y_consultas():
    """Función para consultar la base de datos y verificar que funciona."""
    print("--- EJECUTANDO PRUEBA DE CONSULTA EN LA BD ---")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Consulta uniendo productos con sus categorías usando JOIN
    query = """
        SELECT 
            p.id_product, 
            p.name_product, 
            p.price_product, 
            p.stock_product, 
            c.name_category 
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id_category
    """
    
    cursor.execute(query)
    resultados = cursor.fetchall()
    
    print(f"Se encontraron {len(resultados)} productos en la base de datos:\n")
    print(f"{'ID':<4} | {'PRODUCTO':<30} | {'PRECIO':<8} | {'STOCK':<6} | {'CATEGORÍA'}")
    print("-" * 65)
    
    for row in resultados:
        id_p, nombre, precio, stock, categoria = row
        print(f"{id_p:<4} | {nombre:<30} | ${precio:<7.2f} | {stock:<6} | {categoria}")
        
    conn.close()
    print("\n¡Prueba completada con éxito!")

if __name__ == "__main__":
    # 1. Inicializa y puebla la BD
    inicializar_db_vendove()
    
    # 2. Ejecuta la prueba de lectura inmediatamente después
    probar_conexion_y_consultas()