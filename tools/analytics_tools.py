import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import os
from crewai.tools import BaseTool
from pydantic import Field

# Configuración de rutas
DB_PATH = os.path.join("data", "vendove_store.db")
CHART_PATH = os.path.join("data", "chart_sales.png")
EXCEL_PATH = os.path.join("data", "reporte_gerencial_vendove.xlsx")

class AnalyticsTool(BaseTool):
    name: str = "analizar_y_exportar_ventas"
    description: str = (
        "Consulta la base de datos, genera una gráfica de barras en PNG y "
        "un reporte ejecutivo en Excel con KPIs y alertas de stock."
    )

    def _run(self, query: str = "") -> str:
        try:
            # 1. Conexión y carga de datos
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query("SELECT * FROM products", conn)
            conn.close()

            if df.empty:
                return "Error: La base de datos está vacía. No se puede generar el informe."

            # 2. Cálculos de Negocio (KPIs)
            # Ingreso bruto por producto
            df['Ingresos_Brutos'] = df['price_product'] * df['sales_product']
            
            # Estado de Stock: Alerta si hay menos de 10 unidades
            df['Estado_Stock'] = df['stock_product'].apply(
                lambda x: '⚠️ REABASTECER' if x < 10 else '✅ OK'
            )

            # Ratio de Ventas (Qué tanto del inventario se ha movido)
            df['Desplazamiento_%'] = (
                (df['sales_product'] / (df['stock_product'] + df['sales_product'])) * 100
            ).round(2)

            # 3. Generar Gráfica Profesional
            plt.figure(figsize=(12, 6))
            colors = ['#2c3e50' if x >= 10 else '#e74c3c' for x in df['stock_product']]
            plt.bar(df['name_product'], df['sales_product'], color=colors)
            
            total_ingresos = df['Ingresos_Brutos'].sum()
            plt.title(f'Rendimiento de Ventas VendoVe\n(Ingresos Totales: ${total_ingresos:,.2f})', fontsize=14)
            plt.xlabel('Productos', fontsize=12)
            plt.ylabel('Unidades Vendidas', fontsize=12)
            plt.xticks(rotation=30, ha='right')
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            plt.tight_layout()
            plt.savefig(CHART_PATH)
            plt.close()

            # 4. Exportar a Excel con dos pestañas (Reporte Robusto)
            with pd.ExcelWriter(EXCEL_PATH, engine='openpyxl') as writer:
                # Hoja 1: Detalle Completo
                df.to_excel(writer, sheet_name='Detalle_Inventario', index=False)
                
                # Hoja 2: Resumen Ejecutivo
                resumen_data = {
                    'Indicador': ['Ingresos Totales', 'Unidades Totales Vendidas', 'Productos en Alerta'],
                    'Valor': [
                        f"${total_ingresos:,.2f}", 
                        df['sales_product'].sum(),
                        len(df[df['stock_product'] < 10])
                    ]
                }
                pd.DataFrame(resumen_data).to_excel(writer, sheet_name='Resumen_Ejecutivo', index=False)

            return (f"✅ Análisis completado con éxito.\n"
                    f"- Gráfica guardada en: {CHART_PATH}\n"
                    f"- Excel generado en: {EXCEL_PATH}\n"
                    f"- KPI: Ingresos totales de ${total_ingresos:,.2f}")

        except Exception as e:
            return f"Error crítico al generar analytics: {str(e)}"