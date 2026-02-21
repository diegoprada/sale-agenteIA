import gradio as gr
import os
import sqlite3
import pandas as pd
import threading
import time
from dotenv import load_dotenv
from database.db_manager import inicializar_db_vendove
from agents.crew_logic import ejecutar_crew, generar_reportes_automatico

# Configuración de inicio
load_dotenv()
inicializar_db_vendove()
os.environ["CREWAI_TELEMETRY_OPTOUT"] = "true"

CHART_PATH = "data/chart_sales.png"
EXCEL_PATH = "data/reporte_gerencial_vendove.xlsx"
DB_PATH = "data/vendove_store.db"

# --- LÓGICA DE DATOS ---

def responder(mensaje, historial):
    """Responde en el chat solo con el agente de ventas (Asistente Virtual)."""
    if historial is None:
        historial = []

    respuesta_ia = ejecutar_crew(mensaje)

    historial.append({"role": "user", "content": mensaje})
    historial.append({"role": "assistant", "content": respuesta_ia})

    return "", historial


def actualizar_panel():
    """
    Regenera reportes (Excel + gráfica) y devuelve datos para la pestaña Analytics.
    Se usa al cargar la app y al pulsar Refrescar.
    """
    try:
        generar_reportes_automatico()
        if not os.path.exists(DB_PATH):
            return None, None, None
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            "SELECT name_product, price_product, sales_product, stock_product FROM products",
            conn,
        )
        conn.close()
        df["Alerta"] = df["stock_product"].apply(
            lambda x: "⚠️ BAJO" if x < 10 else "✅ OK"
        )
        excel_path = EXCEL_PATH if os.path.exists(EXCEL_PATH) else None
        chart_path = CHART_PATH if os.path.exists(CHART_PATH) else None
        return df, excel_path, chart_path
    except Exception as e:
        return None, None, None


def _generar_reportes_en_segundo_plano(intervalo_minutos=5):
    """Hilo en segundo plano: regenera reportes cada N minutos sin tocar el chat."""
    while True:
        time.sleep(intervalo_minutos * 60)
        try:
            generar_reportes_automatico()
        except Exception:
            pass


# --- INTERFAZ ---

with gr.Blocks(title="VendoVe ERP") as demo:
    gr.Markdown("# 🏢 VendoVe ERP - Panel de Control")

    with gr.Tabs():
        with gr.TabItem("💬 Asistente Virtual"):
            chatbot = gr.Chatbot(label="Asistente de Ventas", height=500)
            with gr.Row():
                txt_input = gr.Textbox(
                    placeholder="Pregunta por productos o realiza una venta...",
                    show_label=False,
                    scale=4,
                )
                btn_enviar = gr.Button("Enviar 🚀", variant="primary", scale=1)

        with gr.TabItem("📊 Analytics"):
            gr.Markdown("Análisis de ventas (reportes generados automáticamente)")
            with gr.Row():
                with gr.Column():
                    tabla_datos = gr.Dataframe(interactive=False, label="Datos de productos")
                    imagen_grafica = gr.Image(
                        value=CHART_PATH if os.path.exists(CHART_PATH) else None,
                        label="Gráfica de ventas",
                        type="filepath",
                    )
                with gr.Column():
                    archivo_excel = gr.File(label="Reporte Excel", value=EXCEL_PATH if os.path.exists(EXCEL_PATH) else None)
                    btn_refrescar = gr.Button("🔄 Refrescar análisis")

    # Al cargar la app: generar reportes y rellenar Analytics
    def al_cargar():
        return actualizar_panel()

    demo.load(al_cargar, None, [tabla_datos, archivo_excel, imagen_grafica])

    # Eventos
    txt_input.submit(responder, [txt_input, chatbot], [txt_input, chatbot])
    btn_enviar.click(responder, [txt_input, chatbot], [txt_input, chatbot])
    btn_refrescar.click(
        actualizar_panel,
        None,
        [tabla_datos, archivo_excel, imagen_grafica],
    )

if __name__ == "__main__":
    # Reportes automáticos en segundo plano cada 5 minutos
    hilo_reportes = threading.Thread(
        target=_generar_reportes_en_segundo_plano,
        kwargs={"intervalo_minutos": 5},
        daemon=True,
    )
    hilo_reportes.start()

    demo.launch(theme=gr.themes.Soft())