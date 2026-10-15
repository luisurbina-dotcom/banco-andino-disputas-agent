from rich.console import Console

from agent.garantias import Evento
from chat import vista
from chat.indicadores import desde_eventos


def _consola():
    return Console(record=True, width=120, color_system=None)


def test_bienvenida_menciona_datos_ficticios_y_salida():
    consola = _consola()
    vista.bienvenida(consola)
    texto = consola.export_text()
    assert "ficticios" in texto and "/salir" in texto


def test_cliente_y_agente_se_diferencian():
    consola = _consola()
    vista.mensaje_cliente(consola, "No reconozco un cobro")
    vista.respuesta_agente(consola, "Revisemos tu caso")
    texto = consola.export_text()
    assert "Cliente" in texto and "No reconozco un cobro" in texto
    assert "Agente Banco Andino" in texto and "Revisemos tu caso" in texto


def test_indicadores_principales_y_secundarios_se_muestran():
    consola = _consola()
    eventos = [
        Evento("verificar_identidad", {}, "ok", {"verificado": True, "nombre": "Ana"}),
        Evento("bloquear_tarjeta", {}, "ok", {"ultimos4": "4821"}),
        Evento("iniciar_disputa", {}, "negado", "Regla 2: supera $500.000"),
    ]
    vista.indicadores(consola, desde_eventos(eventos))
    texto = consola.export_text()
    assert "Identidad verificada" in texto
    assert "TARJETA BLOQUEADA" in texto and "•••• 4821" in texto
    assert "NEGADO" in texto and "Regla 2" in texto


def test_sin_indicadores_no_imprime_nada():
    consola = _consola()
    vista.indicadores(consola, [])
    assert consola.export_text().strip() == ""


def test_resumen_lista_las_acciones():
    consola = _consola()
    vista.resumen(consola, {"DISPUTA ABIERTA": 1, "NEGADO": 2})
    texto = consola.export_text()
    assert "DISPUTA ABIERTA" in texto and "2" in texto


def test_resumen_vacio():
    consola = _consola()
    vista.resumen(consola, {})
    assert "Sin acciones" in consola.export_text()
