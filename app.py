import gradio as gr
import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from database.db_manager import inicializar_db_vendove
from agents.crew_logic import ejecutar_crew

# 1. Configuración de inicio
load_dotenv()
inicializar_db_vendove()
os.environ["CREWAI_TELEMETRY_OPTOUT"] = "true"

# --- LÓGICA DE DATOS ---

def responder(mensaje, historial):
    """
    Formato exigido por el error: 
    [{'role': 'user', 'content': '...'}, {'role': 'assistant', 'content': '...'}]
    """
    if historial is None:
        historial = []
        
    # Llamamos a CrewAI
    respuesta_ia = ejecutar_crew(mensaje)
    
    # AGREGAMOS COMO DICCIONARIOS (Lo que el error pidió)
    historial.append({"role": "user", "content": mensaje})
    historial.append({"role": "assistant", "content": respuesta_ia})
    
    return "", historial

def actualizar_panel():
    try:
        conn = sqlite3.connect("data/vendove_store.db")
        df = pd.read_sql_query("SELECT name_product, price_product, sales_product, stock_product FROM products", conn)
        conn.close()
        df['Alerta'] = df['stock_product'].apply(lambda x: "⚠️ BAJO" if x < 10 else "✅ OK")
        return df, "data/reporte_gerencial_vendove.xlsx"
    except Exception as e:
        return None, None

# --- INTERFAZ ---

with gr.Blocks(title="VendoVe ERP") as demo:
    gr.Markdown("# 🏢 VendoVe ERP - Panel de Control")
    
    with gr.Tabs():
        with gr.TabItem("💬 Asistente Virtual"):
            # Sin 'type' para evitar el TypeError del inicio
            chatbot = gr.Chatbot(label="Asistente de Ventas", height=500)
            with gr.Row():
                txt_input = gr.Textbox(placeholder="Pregunta algo...", show_label=False, scale=4)
                btn_enviar = gr.Button("Enviar 🚀", variant="primary", scale=1)

        with gr.TabItem("📊 Analytics"):
            with gr.Row():
                with gr.Column():
                    tabla_datos = gr.Dataframe(interactive=False)
                    btn_refrescar = gr.Button("🔄 Refrescar Datos")
                with gr.Column():
                    gr.File(label="Excel", value="data/reporte_gerencial_vendove.xlsx")

    # Eventos
    txt_input.submit(responder, [txt_input, chatbot], [txt_input, chatbot])
    btn_enviar.click(responder, [txt_input, chatbot], [txt_input, chatbot])
    btn_refrescar.click(actualizar_panel, None, [tabla_datos, gr.File()])

if __name__ == "__main__":
    # El theme se define aquí para cumplir con Gradio 6
    demo.launch(theme=gr.themes.Soft())