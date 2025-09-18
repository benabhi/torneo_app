"""
Módulo de Lógica del Torneo (Motor de Reglas)

Este archivo representa el "cerebro" del torneo. Contiene toda la lógica de
negocio y las reglas específicas para determinar el flujo de los partidos.
Es deliberadamente independiente de la interfaz gráfica y de los detalles
internos de la base de datos. Su única responsabilidad es procesar datos
y devolver resultados basados en las reglas del torneo.

Funciones clave:
- generar_fixture_zona: Crea los enfrentamientos para la fase de grupos.
- generar_enfrentamientos_iniciales: Genera los cruces de la primera fase eliminatoria.
- obtener_ganadores: Determina los equipos que avanzan de una fase eliminatoria.
- generar_enfrentamientos: Crea los partidos para las siguientes fases eliminatorias.
"""

# Se importa 'random' para poder barajar (shuffle) a los ganadores de una fase,
# asegurando que los siguientes enfrentamientos sean aleatorios.
import random

# Se importa 'itertools' específicamente por su función 'combinations', que es
# extremadamente eficiente para generar todos los pares únicos de un grupo
# (perfecto para un fixture de "todos contra todos").
import itertools

# Se importa el módulo 'database' completo para poder acceder a su instancia
# compartida 'db'. Esto es crucial para que los tests puedan reemplazarla.
from . import database

# Se importa el módulo de configuración para acceder a las reglas del torneo,
# como la lista de zonas y cuántos equipos clasifican.
from . import config

# Se importa el logger para registrar información sobre el progreso de la lógica.
from .logger import logger


def generar_fixture_zona(zona):
    """
    Genera la lista de partidos pendientes para una zona específica en la fase de grupos.

    Esta función implementa la lógica de "todos contra todos". Primero, calcula
    todos los enfrentamientos posibles entre los equipos de la zona. Luego, consulta
    la base de datos para ver qué partidos ya se han jugado y los excluye,
    devolviendo únicamente los que quedan por disputar.

    Args:
        zona (str): El nombre de la zona para la cual generar el fixture (ej: "A").

    Returns:
        list: Una lista de tuplas, donde cada tupla representa un partido
              pendiente con los nombres de los dos equipos.
    """
    # 1. Obtener todos los equipos que pertenecen a la zona especificada.
    database.db.cursor.execute("SELECT nombre FROM equipos WHERE zona = ?", (zona,))
    equipos_db = database.db.cursor.fetchall()
    # Extraer solo los nombres de los equipos de los resultados de la consulta.
    equipos_nombres = [equipo[0] for equipo in equipos_db]

    # 2. Obtener todos los partidos de fase de grupos que ya han sido registrados
    #    para esta zona. Es una consulta más compleja que une las tablas 'partidos'
    #    y 'equipos' para obtener los nombres de los participantes.
    database.db.cursor.execute("""
        SELECT el.nombre, ev.nombre
        FROM partidos p
        JOIN equipos el ON p.equipo_local_id = el.id
        JOIN equipos ev ON p.equipo_visitante_id = ev.id
        WHERE p.fase = 'Grupo' AND el.zona = ?
    """, (zona,))
    partidos_jugados_db = database.db.cursor.fetchall()

    # 3. Procesar los partidos jugados para una búsqueda eficiente.
    #    Se convierte la lista a un 'set' porque la comprobación de pertenencia
    #    (ej: `if x in my_set`) es mucho más rápida (O(1)) que en una lista (O(n)).
    #    Además, se "normaliza" cada partido ordenando los nombres de los equipos.
    #    Esto asegura que ('Equipo A', 'Equipo B') y ('Equipo B', 'Equipo A') se
    #    traten como el mismo partido, independientemente de la localía.
    partidos_jugados_set = {tuple(sorted(partido)) for partido in partidos_jugados_db}

    # 4. Generar todos los enfrentamientos posibles ("todos contra todos").
    #    `itertools.combinations` crea pares únicos de todos los equipos.
    #    Por ejemplo, para [A, B, C], genera (A, B), (A, C), (B, C).
    fixture_completo = list(itertools.combinations(equipos_nombres, 2))

    # 5. Filtrar el fixture para obtener solo los partidos pendientes.
    partidos_pendientes = []
    for partido in fixture_completo:
        # Para cada posible partido, se normaliza (ordena) y se comprueba si
        # ya está en el set de partidos jugados.
        if tuple(sorted(partido)) not in partidos_jugados_set:
            # Si no se ha jugado, se añade a la lista de pendientes.
            partidos_pendientes.append(partido)

    return partidos_pendientes

def generar_enfrentamientos_iniciales():
    """
    Genera los enfrentamientos para la primera fase eliminatoria (ej: Octavos de Final).

    Esta función sigue la regla de negocio específica de un cruce entre zonas.
    Primero, obtiene la tabla de posiciones final de cada zona. Luego, empareja
    a los equipos según un esquema cruzado (ej: 1° de Zona A vs. último clasificado
    de Zona B, 2° de Zona A vs. penúltimo de Zona B, y así sucesivamente).

    Returns:
        list or None: Una lista de tuplas con los enfrentamientos, o None si no
                      hay suficientes equipos clasificados para generar los cruces.
    """
    logger.info("Generando enfrentamientos iniciales (Octavos de Final)...")
    clasificados_por_zona = {}

    # Itera sobre cada zona definida en el archivo de configuración.
    for zona in config.ZONAS_DEL_TORNEO:
        # Llama al método de la base de datos para obtener la tabla de posiciones
        # ya calculada y ordenada para la zona actual.
        tabla = database.db.calcular_tabla_posiciones(zona)

        # Medida de seguridad: si no hay suficientes equipos en la tabla para
        # cumplir con el número de clasificados, la lógica no puede continuar.
        if len(tabla) < config.EQUIPOS_CLASIFICAN_POR_ZONA:
            logger.error(f"No hay suficientes equipos en la Zona {zona} para clasificar.")
            return None

        # Extrae los nombres de los equipos que clasificaron.
        # Se usa slicing `[:NUMERO]` para tomar solo los N primeros de la tabla.
        clasificados_por_zona[zona] = [equipo['nombre'] for equipo in tabla[:config.EQUIPOS_CLASIFICAN_POR_ZONA]]
        logger.debug(f"Clasificados de Zona {zona}: {clasificados_por_zona[zona]}")

    # --- LÓGICA DE EMPAREJAMIENTO CRUZADO ---
    # Esta es una regla de negocio específica para un torneo de 2 zonas.
    # Si el torneo se expandiera a 4 zonas, esta sección necesitaría ser modificada.
    if len(config.ZONAS_DEL_TORNEO) != 2:
        logger.error("La lógica de emparejamiento actual solo soporta 2 zonas.")
        return []

    # Se extraen los nombres de las zonas y las listas de equipos para mayor claridad.
    zona_a = config.ZONAS_DEL_TORNEO[0]
    zona_b = config.ZONAS_DEL_TORNEO[1]
    equipos_a = clasificados_por_zona[zona_a]
    equipos_b = clasificados_por_zona[zona_b]

    enfrentamientos = []
    num_clasificados = config.EQUIPOS_CLASIFICAN_POR_ZONA

    # Itera N veces, donde N es el número de equipos que clasifican por zona.
    for i in range(num_clasificados):
        # El equipo de la Zona A se toma en orden ascendente de clasificación.
        # Para i=0, es el 1er clasificado (equipos_a[0]).
        equipo_a = equipos_a[i]

        # El equipo de la Zona B se toma en orden descendente de clasificación.
        # La fórmula `(num_clasificados - 1) - i` logra el cruce:
        # - Cuando i=0 (1° de A), se enfrenta a equipos_b[N-1] (el último clasificado de B).
        # - Cuando i=1 (2° de A), se enfrenta a equipos_b[N-2] (el penúltimo de B).
        equipo_b = equipos_b[(num_clasificados - 1) - i]

        # Se crea la tupla del enfrentamiento y se añade a la lista.
        enfrentamiento = (equipo_a, equipo_b)
        enfrentamientos.append(enfrentamiento)
        logger.debug(f"Enfrentamiento generado: {equipo_a} (Pos {i+1}{zona_a}) vs {equipo_b} (Pos {num_clasificados-i}{zona_b})")

    return enfrentamientos

def obtener_ganadores(fase_anterior):
    """
    Consulta la base de datos para obtener la lista de equipos ganadores de una fase.

    Después de obtener la lista, la baraja aleatoriamente (`shuffle`) para que el
    sorteo de la siguiente ronda sea imparcial y no dependa del orden en que
    se jugaron o guardaron los partidos.

    Args:
        fase_anterior (str): El nombre de la fase de la cual obtener los ganadores
                             (ej: "Octavos").

    Returns:
        list: Una lista con los nombres de los equipos ganadores, en orden aleatorio.
    """
    # Pide al módulo de base de datos todos los partidos de la fase especificada.
    partidos = database.db.obtener_partidos_fase(fase_anterior)
    ganadores = []

    # Itera sobre cada partido recuperado.
    for partido in partidos:
        # Para cada partido, realiza una consulta para encontrar el nombre del equipo
        # cuyo ID coincide con el 'ganador_id' del partido.
        database.db.cursor.execute("SELECT e.nombre FROM partidos p JOIN equipos e ON p.ganador_id = e.id WHERE p.id = ?", (partido[0],))
        ganador = database.db.cursor.fetchone()
        if ganador:
            ganadores.append(ganador[0])

    # ¡Paso crucial! Se baraja la lista de ganadores. Esto asegura que los
    # emparejamientos en la siguiente ronda (Cuartos, Semis) sean aleatorios.
    random.shuffle(ganadores)
    return ganadores

def generar_enfrentamientos(fase_anterior):
    """
    Genera los enfrentamientos para las fases eliminatorias subsecuentes
    (Cuartos, Semifinal, Final).

    Esta función es más simple que la inicial. Llama a `obtener_ganadores` para
    obtener una lista ya barajada de los equipos que avanzaron y simplemente
    los empareja en el orden en que están en esa lista.

    Args:
        fase_anterior (str): El nombre de la fase de la cual provienen los
                             ganadores (ej: "Octavos").

    Returns:
        list: Una lista de tuplas con los nuevos enfrentamientos.
    """
    # El primer paso es determinar quiénes avanzaron de la ronda anterior.
    ganadores = obtener_ganadores(fase_anterior)

    # Si hay menos de dos ganadores, no se pueden formar partidos.
    if len(ganadores) < 2:
        return []

    enfrentamientos = []
    # Se utiliza un bucle `range` con un paso de 2 para tomar a los ganadores
    # de dos en dos (índices 0 y 1, luego 2 y 3, etc.).
    for i in range(0, len(ganadores), 2):
        # Se asegura de que haya un oponente para el equipo actual.
        if i + 1 < len(ganadores):
            # Se crea el par y se añade a la lista de enfrentamientos.
            enfrentamientos.append((ganadores[i], ganadores[i+1]))

    return enfrentamientos