"""
Suite de Tests para el Módulo de Lógica del Torneo (`logic.py`)

Este archivo contiene los tests unitarios para las funciones que definen las
reglas y el flujo del torneo. El objetivo es asegurar que la lógica de negocio
(generación de partidos, cruces, etc.) sea correcta, independientemente de la
interfaz gráfica o la implementación de la base de datos.

Los tests utilizan un `fixture` que proporciona una base de datos de prueba
y se asegura de que el módulo `logic` la utilice, garantizando un total
aislamiento.
"""

# Se importa `pytest` para poder usar sus funcionalidades, como los fixtures.
import pytest
# Se importa el módulo de configuración para poder parchearlo.
import lib.config
# Se importa el módulo `logic` que contiene las funciones a probar.
from lib import logic


@pytest.fixture
def db_test(monkeypatch):
    """
    Crea y configura un entorno de base de datos limpio para los tests de lógica.

    Este fixture es fundamental para los tests de lógica porque el módulo `logic`
    depende de la instancia `db` del módulo `database`. El fixture hace lo siguiente:
    1. Desactiva el logging.
    2. Crea una base de datos de prueba en memoria.
    3. **Parchea la variable `db` en `lib.database`**, reemplazándola por la
       instancia de prueba. Esto es crucial para que las funciones de `logic`
       operen sobre los datos de prueba y no sobre la base de datos real.
    4. Entrega la instancia de la base de datos de prueba al test, para que
       pueda llenarla con los datos necesarios (Arrange).
    """
    monkeypatch.setattr(lib.config, 'LOGGING_ACTIVADO', False)

    from lib.database import Database

    # Se crea la instancia de la base de datos de prueba.
    db_instance = Database(db_name=':memory:')

    # --- Paso Clave para los Tests de Lógica ---
    # `monkeypatch.setattr` modifica un atributo en tiempo de ejecución.
    # Aquí, le decimos que vaya al módulo `lib.database` y reemplace la
    # variable global `db` con nuestra `db_instance` de prueba.
    monkeypatch.setattr('lib.database.db', db_instance)

    # Se entrega la instancia al test para que pueda prepararla.
    yield db_instance

    # Se cierra la conexión al finalizar el test.
    db_instance.cerrar_conexion()


# --- Tests para las Funciones de Lógica del Torneo ---

def test_generar_fixture_zona_completo(db_test):
    """
    Verifica que `generar_fixture_zona` crea el número correcto de partidos
    para un escenario "todos contra todos". Para 4 equipos, deben ser 6 partidos.
    """
    # 1. Arrange (Preparar): Se añaden 4 equipos a la base de datos de prueba.
    db_test.agregar_equipo("Equipo A", "A")
    db_test.agregar_equipo("Equipo B", "A")
    db_test.agregar_equipo("Equipo C", "A")
    db_test.agregar_equipo("Equipo D", "A")

    # 2. Act (Actuar): Se llama a la función de lógica que se quiere probar.
    partidos_pendientes = logic.generar_fixture_zona("A")

    # 3. Assert (Verificar): Se comprueban los resultados.
    # La fórmula para combinaciones de N elementos tomados de 2 en 2 es N*(N-1)/2.
    # Para 4 equipos: 4*3/2 = 6 partidos.
    assert len(partidos_pendientes) == 6

    # Para verificar el contenido sin depender del orden, se usan `sets`.
    # Un `set` no tiene orden, por lo que `set_a == set_b` es verdadero
    # aunque los elementos estén en diferente orden en las listas originales.
    partidos_esperados = {
        ("Equipo A", "Equipo B"), ("Equipo A", "Equipo C"), ("Equipo A", "Equipo D"),
        ("Equipo B", "Equipo C"), ("Equipo B", "Equipo D"), ("Equipo C", "Equipo D")
    }
    # Se "normalizan" los resultados ordenando cada tupla para que ('A', 'B')
    # sea igual a ('B', 'A'), y luego se convierten a un set.
    partidos_resultado_set = {tuple(sorted(p)) for p in partidos_pendientes}
    partidos_esperados_set = {tuple(sorted(p)) for p in partidos_esperados}

    assert partidos_resultado_set == partidos_esperados_set

def test_generar_fixture_con_partidos_ya_jugados(db_test):
    """
    Verifica que `generar_fixture_zona` excluye correctamente los partidos
    que ya han sido registrados en la base de datos.
    """
    # 1. Arrange: Se añaden 3 equipos y se registra un partido entre dos de ellos.
    db_test.agregar_equipo("Equipo A", "A")
    db_test.agregar_equipo("Equipo B", "A")
    db_test.agregar_equipo("Equipo C", "A")

    equipos_map = {e[1]: e[0] for e in db_test.obtener_equipos()}
    id_a = equipos_map["Equipo A"]
    id_c = equipos_map["Equipo C"]
    db_test.registrar_partido("Grupo", id_a, id_c, 1, 0) # A gana a C

    # 2. Act: Se genera el fixture.
    partidos_pendientes = logic.generar_fixture_zona("A")

    # 3. Assert:
    # Con 3 equipos, el total de partidos es 3. Si uno ya se jugó, deben quedar 2.
    assert len(partidos_pendientes) == 2

    # Se verifica explícitamente que el partido jugado (A vs C) NO está en
    # la lista de partidos pendientes devuelta por la función.
    partido_jugado = tuple(sorted(("Equipo A", "Equipo C")))
    partidos_resultado_set = {tuple(sorted(p)) for p in partidos_pendientes}
    assert partido_jugado not in partidos_resultado_set

def test_generar_enfrentamientos_siguientes(db_test):
    """
    Verifica que `generar_enfrentamientos` crea correctamente los partidos
    para una fase eliminatoria a partir de los ganadores de la fase anterior.
    """
    # 1. Arrange: Se crean 8 equipos y se simulan 4 partidos de "Octavos",
    # registrando a los equipos con índice par (0, 2, 4, 6) como ganadores.
    equipos_ids = []
    for i in range(8):
        db_test.agregar_equipo(f"Equipo-{i}", "A")
        equipos_ids.append(i + 1)

    db_test.registrar_partido("Octavos", equipos_ids[0], equipos_ids[1], 1, 0) # Gana Eq-0
    db_test.registrar_partido("Octavos", equipos_ids[2], equipos_ids[3], 1, 0) # Gana Eq-2
    db_test.registrar_partido("Octavos", equipos_ids[4], equipos_ids[5], 1, 0) # Gana Eq-4
    db_test.registrar_partido("Octavos", equipos_ids[6], equipos_ids[7], 1, 0) # Gana Eq-6

    # 2. Act: Se generan los enfrentamientos para la siguiente fase ("Cuartos").
    enfrentamientos_cuartos = logic.generar_enfrentamientos("Octavos")

    # 3. Assert:
    # De 4 ganadores deben salir 2 partidos de cuartos de final.
    assert len(enfrentamientos_cuartos) == 2

    # La función `obtener_ganadores` baraja (`shuffle`) la lista, por lo que
    # no podemos predecir los cruces exactos. Sin embargo, podemos verificar
    # que los 4 equipos que participan en los nuevos enfrentamientos son,
    # en efecto, los 4 que ganaron en la fase anterior.
    ganadores_esperados = {"Equipo-0", "Equipo-2", "Equipo-4", "Equipo-6"}
    participantes_reales = set()
    for local, visitante in enfrentamientos_cuartos:
        participantes_reales.add(local)
        participantes_reales.add(visitante)

    assert participantes_reales == ganadores_esperados