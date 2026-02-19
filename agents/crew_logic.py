from crewai import Agent, Task, Crew, Process
from tools.sales_tools import ConsultarCatalogoTool, RegistrarVentaTool
# Importamos solo la herramienta robusta que creamos
from tools.analytics_tools import AnalyticsTool

# 1. Instanciamos las herramientas
tool_catalogo = ConsultarCatalogoTool()
tool_venta = RegistrarVentaTool()
tool_analytics = AnalyticsTool()  # Esta herramienta ya hace gráficas y Excel

# 2. Definir Agentes
agente_ventas = Agent(
    role='Vendedor VendoVe',
    goal='Ayudar a los clientes, consultar el catálogo y cerrar ventas.',
    backstory='Asesor senior de VendoVe. Eres amable y eficiente. Si un cliente pregunta qué productos hay, usas el catálogo.',
    tools=[tool_catalogo, tool_venta],
    verbose=True,
    allow_delegation=False
)

agente_analista = Agent(
    role='Analista de Datos y Negocios',
    goal='Generar reportes visuales y archivos Excel de las ventas realizadas.',
    backstory='Experto en Business Intelligence. Te encargas de transformar datos brutos en informes ejecutivos profesionales.',
    tools=[tool_analytics], # Ahora usa la herramienta robusta
    verbose=True,
    allow_delegation=False
)

def ejecutar_crew(mensaje_usuario):
    # Tarea para el vendedor
    tarea_venta = Task(
        description=(
            f"Procesa la solicitud del usuario: '{mensaje_usuario}'. "
            "Si el usuario pregunta por productos, consulta el catálogo. "
            "Si el usuario quiere comprar, usa el ID del producto para registrar la venta. "
            "Si el usuario pide un informe, reporte o gráfica, delega la interpretación al Analista."
        ),
        expected_output="Una respuesta amable y clara para el cliente con los resultados de la operación.",
        agent=agente_ventas
    )

    # Tarea para el analista (se activa si se pide un reporte)
    tarea_analisis = Task(
        description=(
            "Si la solicitud del usuario requiere un informe, gráfica o análisis, "
            "utiliza la herramienta de analítica para generar el PNG y el Excel."
        ),
        expected_output="Confirmación de que los reportes gráficos y Excel han sido generados exitosamente.",
        agent=agente_analista,
        context=[tarea_venta] # El analista sabe qué pasó en la venta
    )
    
    # Configuramos el Crew
    crew = Crew(
        agents=[agente_ventas, agente_analista],
        tasks=[tarea_venta, tarea_analisis],
        process=Process.sequential # Se ejecutan en orden
    )
    
    # kickoff devuelve un objeto CrewOutput, lo convertimos a string
    resultado = crew.kickoff()
    return str(resultado)