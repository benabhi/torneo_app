"""
Suite de Tests para el Módulo de Base de Datos (`database.py`)

Este archivo contiene los tests unitarios y de integración para la clase `Database`.
El objetivo es verificar que todas las operaciones de la base de datos (crear,
leer, actualizar, borrar y calcular) funcionen de manera correcta y aislada.

Cada test se centra en una funcionalidad específica y se ejecuta contra una
base de datos temporal en memoria, asegurando que los tests no interfieran
entre sí y no modifiquen la base de datos real de la aplicación.
"""

# Se importa `pytest` para poder usar sus funcionalidades, como los fixtures.
import pytest

# Se importa el módulo de configuración para poder parchearlo con `monkeypatch`.
import lib.config


# --- Fixture de Preparación del Entorno de Test ---
@pytest.fixture
def db_test(monkeypatch):
    """
    Crea y configura un entorno de base de datos limpio para cada test.

    Esta función es un "fixture" de pytest. Se ejecuta automáticamente antes de
    cada función de test que la reciba como argumento. Su propósito es:
    1. Desactivar el logging para mantener la salida de los tests limpia.
    2. Importar la clase `Database` DESPUÉS de desactivar el logging.
    3. Crear una instancia de `Database` conectada a una base de datos en
       memoria (`:memory:`), que es temporal y se borra al final del test.
    4. Entregar (`yield`) esta instancia al test.
    5. Cerrar la conexión a la base de datos una vez que el test ha finalizado.

    Args:
        monkeypatch: Un fixture de pytest que permite modificar variables,
                     métodos o clases de forma segura durante un test.

    Yields:
        Database: Una instancia limpia de la clase Database para que el test la utilice.
    """
    # 1. Modifica la configuración para desactivar los logs durante el test.
    monkeypatch.setattr(lib.config, 'LOGGING_ACTIVADO', False)

    # 2. Importa la clase `Database` aquí. Esto es crucial para que se importe
    #    con la configuración ya modificada.
    from lib.database import Database

    # 3. Crea la instancia de la base de datos. `:memory:` es una directiva especial
    #    de SQLite que crea la base de datos en la RAM, haciéndola muy rápida y efímera.
    database_instance = Database(db_name=':memory:')

    # 4. `yield` pausa la ejecución del fixture y entrega el control (y la
    #    instancia de la base de datos) al test.
    yield database_instance

    # 5. Después de que el test termina, la ejecución del fixture se reanuda aquí
    #    para realizar la limpieza.
    database_instance.cerrar_conexion()


# --- Suite de Tests para Funcionalidades de la Base de Datos ---

def test_agregar_y_obtener_equipo(db_test):
    """
    Verifica la funcionalidad más básica: agregar un equipo y luego recuperarlo.
    Este test sigue el patrón estándar "Arrange-Act-Assert" (AAA).
    """
    # 1. Arrange (Preparar): Define los datos de entrada para el test.
    nombre_equipo = "Equipo de Prueba"
    zona_equipo = "A"

    # 2. Act (Actuar): Ejecuta el método que se quiere probar.
    resultado_agregado = db_test.agregar_equipo(nombre_equipo, zona_equipo)
    # Ejecuta un segundo método para obtener el resultado de la acción.
    equipos = db_test.obtener_equipos()

    # 3. Assert (Verificar): Comprueba que los resultados son los esperados.
    # El método debe devolver True indicando que la operación fue exitosa.
    assert resultado_agregado is True
    # La lista de equipos ahora debe contener exactamente un elemento.
    assert len(equipos) == 1

    # Desempaqueta el primer (y único) equipo para verificar sus datos.
    equipo_guardado = equipos[0] # Formato: (id, nombre, zona, color_hex)
    assert equipo_guardado[1] == nombre_equipo
    assert equipo_guardado[2] == zona_equipo
    # Verifica que se asignó un color hexadecimal (debe empezar con '#').
    assert equipo_guardado[3].startswith("#")

def test_no_permite_equipos_duplicados(db_test):
    """
    Verifica la restricción UNIQUE de la base de datos.
    Asegura que no se puedan agregar dos equipos con el mismo nombre.
    """
    # Arrange: Agrega un equipo inicial.
    nombre_equipo = "Equipo Duplicado"
    db_test.agregar_equipo(nombre_equipo, "A")

    # Act: Intenta agregar un segundo equipo con el mismo nombre.
    resultado_segundo_agregado = db_test.agregar_equipo(nombre_equipo, "B")
    # Obtiene la lista de equipos para ver el estado final.
    equipos = db_test.obtener_equipos()

    # Assert:
    # El método `agregar_equipo` debe devolver False para indicar el fallo.
    assert resultado_segundo_agregado is False
    # La base de datos debe seguir conteniendo solo el primer equipo.
    assert len(equipos) == 1

def test_calcular_tabla_posiciones_simple(db_test):
    """
    Verifica que el cálculo de la tabla de posiciones funciona para un escenario simple.
    Se crea un único partido y se comprueban los puntos del ganador y el perdedor.
    """
    # Arrange: Crea dos equipos y registra un partido entre ellos.
    db_test.agregar_equipo("Equipo Ganador", "A")
    db_test.agregar_equipo("Equipo Perdedor", "A")

    # Obtiene los IDs autogenerados de los equipos para poder registrar el partido.
    equipos_map = {e[1]: e[0] for e in db_test.obtener_equipos()}
    id_ganador = equipos_map["Equipo Ganador"]
    id_perdedor = equipos_map["Equipo Perdedor"]

    # Registra un partido donde "Equipo Ganador" gana 2-1.
    db_test.registrar_partido("Grupo", id_ganador, id_perdedor, 2, 1)

    # Act: Llama al método para calcular la tabla de la zona "A".
    tabla = db_test.calcular_tabla_posiciones("A")

    # Assert:
    # La tabla debe contener dos filas (una por cada equipo).
    assert len(tabla) == 2

    # La tabla está ordenada por puntos, así que el primer elemento debe ser el ganador.
    tabla_ganador = tabla[0]
    assert tabla_ganador["nombre"] == "Equipo Ganador"
    assert tabla_ganador["puntos"] == 3 # 3 puntos por una victoria.

    # El segundo elemento debe ser el perdedor.
    tabla_perdedor = tabla[1]
    assert tabla_perdedor["nombre"] == "Equipo Perdedor"
    assert tabla_perdedor["puntos"] == 0 # 0 puntos por una derrota.

def test_reiniciar_fases_eliminatorias_mantiene_grupos(db_test):
    """
    Verifica que el reinicio de las eliminatorias borra solo los partidos
    de fases como 'Octavos' o 'Final', pero deja intactos los de 'Grupo'.
    """
    # 1. Arrange (Preparar):
    # Se crean 4 equipos para simular las fases.
    db_test.agregar_equipo("Equipo A", "A")
    db_test.agregar_equipo("Equipo B", "A")
    db_test.agregar_equipo("Equipo C", "B")
    db_test.agregar_equipo("Equipo D", "B")
    equipos = db_test.obtener_equipos()
    id_a, id_b, id_c, id_d = equipos[0][0], equipos[1][0], equipos[2][0], equipos[3][0]

    # Se registra un partido de fase de grupos.
    db_test.registrar_partido("Grupo", id_a, id_b, 1, 0)
    # Se registran dos partidos de eliminatorias.
    db_test.registrar_partido("Octavos", id_a, id_c, 2, 1)
    db_test.registrar_partido("Final", id_b, id_d, 0, 3)

    # Verificación inicial: deben existir 3 partidos en total.
    assert len(db_test.cursor.execute("SELECT * FROM partidos").fetchall()) == 3

    # 2. Act (Actuar):
    # Se ejecuta el método que se quiere probar.
    db_test.reiniciar_fases_eliminatorias()

    # 3. Assert (Verificar):
    # Se obtienen todos los partidos restantes en la base de datos.
    partidos_restantes = db_test.cursor.execute("SELECT * FROM partidos").fetchall()

    # Debe quedar exactamente 1 partido.
    assert len(partidos_restantes) == 1
    # Y ese partido debe ser el de la fase de "Grupo".
    assert partidos_restantes[0][1] == "Grupo"

def test_eliminar_todos_los_equipos_mantiene_config(db_test):
    """
    Verifica que `eliminar_todos_los_equipos` borra equipos y partidos
    pero deja intacta la tabla de configuración.
    """
    # Arrange: Añade equipos, un partido y una clave de configuración.
    db_test.agregar_equipo("Equipo A", "A")
    db_test.agregar_equipo("Equipo B", "B")
    equipos = db_test.obtener_equipos()
    db_test.registrar_partido("Grupo", equipos[0][0], equipos[1][0], 1, 1)
    db_test.establecer_config("test_key", "test_value")

    # Act: Llama al método de eliminación.
    db_test.eliminar_todos_los_equipos()

    # Assert: Verifica que los equipos y partidos se han ido, pero la config permanece.
    assert len(db_test.obtener_equipos()) == 0
    assert len(db_test.cursor.execute("SELECT * FROM partidos").fetchall()) == 0
    assert db_test.obtener_config("test_key") == "test_value"

def test_desbloquear_equipos_elimina_config(db_test):
    """
    Verifica que los métodos `desbloquear_*` eliminan la clave correspondiente
    de la tabla de configuración.
    """
    # Arrange: Establece las claves de bloqueo.
    db_test.establecer_config('equipos_bloqueados', '1')
    db_test.establecer_config('fase_grupos_bloqueada', '1')
    assert db_test.equipos_bloqueados() is True
    assert db_test.fase_grupos_bloqueada() is True

    # Act: Llama a los métodos de desbloqueo.
    db_test.desbloquear_equipos()
    db_test.desbloquear_fase_grupos()

    # Assert: Verifica que las claves ya no existen.
    assert db_test.equipos_bloqueados() is False
    assert db_test.fase_grupos_bloqueada() is False

def test_on_delete_cascade_funciona(db_test):
    """
    Verifica que al eliminar un equipo, sus partidos asociados se eliminan
    automáticamente gracias a la restricción `ON DELETE CASCADE`.
    """
    # Arrange: Crea dos equipos y un partido entre ellos.
    db_test.agregar_equipo("Equipo A", "A")
    db_test.agregar_equipo("Equipo B", "A")
    equipos = db_test.obtener_equipos()
    id_a, id_b = equipos[0][0], equipos[1][0]
    db_test.registrar_partido("Grupo", id_a, id_b, 1, 0)
    assert len(db_test.obtener_partidos_fase("Grupo")) == 1

    # Act: Elimina uno de los equipos.
    db_test.eliminar_equipo(id_a)

    # Assert: Verifica que el partido también ha sido eliminado.
    assert len(db_test.obtener_partidos_fase("Grupo")) == 0