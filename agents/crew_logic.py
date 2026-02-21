"""
Lógica de agentes CrewAI para VendoVe.
- Asistente Virtual (chat): solo agente de ventas.
- Reportes/analytics: se generan de forma automática en app.py, no desde el chat.
"""
from crewai import Agent, Task, Crew, Process
from tools.sales_tools import ConsultarCatalogoTool, RegistrarVentaTool
from tools.analytics_tools import AnalyticsTool

# Herramientas
tool_catalogo = ConsultarCatalogoTool()
tool_venta = RegistrarVentaTool()
tool_analytics = AnalyticsTool()

# Agente de ventas: solo este atiende el chat (Asistente Virtual)
agente_ventas = Agent(
    role='Vendedor VendoVe',
    goal='Ayudar a los clientes, consultar el catálogo y cerrar ventas.',
    backstory='Asesor senior de VendoVe. Eres amable y eficiente. Si un cliente pregunta qué productos hay, usas el catálogo.',
    tools=[tool_catalogo, tool_venta],
    verbose=True,
    allow_delegation=False
)


def ejecutar_crew(mensaje_usuario):
    """
    Ejecuta solo el agente de ventas para el chat.
    La respuesta que ve el usuario es siempre la del vendedor (no la del analista).
    Los reportes se generan de forma automática en la pestaña Analytics.
    """
    tarea_venta = Task(
        description=(
            f"Procesa la solicitud del usuario: '{mensaje_usuario}'. "
            "Si el usuario pregunta por productos, consulta el catálogo. "
            "Si el usuario quiere comprar, usa el ID del producto para registrar la venta. "
            "Responde de forma amable y clara. No generes reportes ni gráficas; eso se hace en otro panel."
        ),
        expected_output="Una respuesta amable y clara para el cliente con los resultados de la operación.",
        agent=agente_ventas
    )

    crew = Crew(
        agents=[agente_ventas],
        tasks=[tarea_venta],
        process=Process.sequential,
    )

    resultado = crew.kickoff()
    # Con un solo agente, raw es la respuesta del vendedor
    return resultado.raw if hasattr(resultado, 'raw') and resultado.raw else str(resultado)


def generar_reportes_automatico():
    """
    Genera Excel y gráfica de ventas sin usar el chat.
    Se llama al cargar la app y/o periódicamente desde la pestaña Analytics.
    """
    return tool_analytics._run("")