import sqlite3
import os
from crewai.tools import BaseTool
from pydantic import Field

DB_PATH = os.path.join("data", "vendove_store.db")

class ConsultarCatalogoTool(BaseTool):
    name: str = "consultar_catalogo"
    description: str = "Consulta los productos disponibles en el catálogo de VendoVe. Muestra ID, nombre, precio y stock."

    def _run(self, query: str = "") -> str:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        sql = "SELECT id_product, name_product, price_product, stock_product FROM products WHERE state_product != 'hide' AND stock_product > 0"
        cursor.execute(sql)
        items = cursor.fetchall()
        conn.close()
        
        if not items: return "No hay productos disponibles."
        res = "Catálogo VendoVe:\n"
        for item in items:
            res += f"- [ID: {item[0]}] {item[1]} | ${item[2]} | Stock: {item[3]}\n"
        return res

class RegistrarVentaTool(BaseTool):
    name: str = "registrar_venta_producto"
    description: str = "Registra la venta de un producto usando su ID numérico. Resta stock y aumenta ventas."

    def _run(self, id_product: str) -> str:
        try:
            # Forzamos la conversión a entero ya que la IA a veces manda strings
            id_int = int(''.join(filter(str.isdigit, str(id_product))))
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("UPDATE products SET stock_product = stock_product - 1, sales_product = IFNULL(sales_product, 0) + 1 WHERE id_product = ?", (id_int,))
            conn.commit()
            conn.close()
            return f"✅ Venta del producto ID {id_int} procesada correctamente."
        except Exception as e:
            return f"Error al registrar venta: {str(e)}"