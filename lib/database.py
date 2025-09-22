"""
Módulo de Base de Datos (Capa de Persistencia)

Este archivo centraliza toda la interacción con la base de datos SQLite3.
Actúa como una capa de abstracción, de modo que el resto de la aplicación
(GUI, lógica) no necesita conocer el lenguaje SQL ni los detalles de cómo
se almacenan los datos. Simplemente llaman a los métodos de esta clase.

Responsabilidades principales:
- Establecer y cerrar la conexión con el archivo de la base de datos.
- Definir y crear el esquema de la base de datos (tablas y columnas).
- Proveer métodos para las operaciones CRUD (Crear, Leer, Actualizar, Borrar)
  sobre equipos, partidos y configuraciones.
- Contener la lógica compleja de consulta, como el cálculo de la tabla de posiciones.
"""

# Se importa 'sqlite3' para la interacción con la base de datos.
import sqlite3

# Se importa 'random' para la generación de colores hexadecimales únicos.
import random

# Se importa 'atexit' para registrar una función que se ejecutará automáticamente
# cuando el programa esté a punto de finalizar. Se usa para garantizar que la
# conexión a la base de datos siempre se cierre correctamente.
import atexit

# Se importa el logger para registrar eventos importantes de la base de datos.
from .logger import logger

# Constante que define el nombre del archivo de la base de datos.
# Centralizarlo aquí facilita cambiarlo si fuera necesario.
DB_NAME = "torneo.sqlite3"


# --- Clase Principal de la Base de Datos ---
class Database:
    """
    Gestiona la conexión y todas las operaciones con la base de datos del torneo.
    Esta clase sigue el patrón Singleton (a través de la instancia única 'db'
    creada al final del archivo), asegurando que toda la aplicación comparta
    la misma conexión a la base de datos.
    """

    def __init__(self, db_name=DB_NAME):
        """
        Constructor de la clase. Establece la conexión con la base de datos.

        Al instanciar esta clase, se conecta al archivo SQLite especificado
        (creándolo si no existe), obtiene un 'cursor' para ejecutar comandos,
        y llama al método que asegura que las tablas necesarias existan.
        También registra el método de cierre para que se ejecute al salir.

        Args:
            db_name (str): El nombre del archivo de la base de datos.
                           Permite especificar un nombre diferente para los tests
                           (ej: ':memory:' para una base de datos en RAM).
        """
        try:
            # Establece la conexión con el archivo de la base de datos.
            self.conn = sqlite3.connect(db_name)
            # Crea un objeto cursor, que es el que ejecuta las sentencias SQL.
            self.cursor = self.conn.cursor()
            # Llama al método para crear las tablas si no existen.
            self.crear_tablas()

            # Registra 'cerrar_conexion' para que se llame automáticamente al
            # finalizar el programa, evitando conexiones abiertas.
            atexit.register(self.cerrar_conexion)
            logger.info("Conexión a la base de datos establecida.")
        except Exception as e:
            # Si ocurre cualquier error durante la conexión, se registra como
            # crítico y se relanza la excepción para detener el programa.
            logger.critical(f"No se pudo conectar a la base de datos: {e}")
            raise e

    def cerrar_conexion(self):
        """
        Cierra la conexión activa con la base de datos.
        Es importante cerrar la conexión para liberar recursos y asegurar que
        todos los cambios se guarden correctamente en el archivo.
        """
        # Se comprueba si el objeto de conexión existe antes de intentar cerrarlo.
        if self.conn:
            self.conn.close()
            logger.info("Conexión a la base de datos cerrada.")

    def crear_tablas(self):
        """
        Define y ejecuta las sentencias SQL para crear el esquema de la base de datos.
        Utiliza "CREATE TABLE IF NOT EXISTS" para que solo se ejecute la primera
        vez o si el archivo de la base de datos es eliminado.
        """
        # --- Tabla de Equipos ---
        # Almacena la información de cada equipo participante.
        # - id: Clave primaria autoincremental, única para cada equipo.
        # - nombre: Nombre del equipo, debe ser único (UNIQUE).
        # - zona: Grupo al que pertenece el equipo (ej: "A").
        # - color_hex: Un color hexadecimal único para la UI.
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            zona TEXT NOT NULL,
            color_hex TEXT NOT NULL UNIQUE
        )
        """)

        # --- Tabla de Partidos ---
        # Almacena cada partido jugado en el torneo.
        # - fase: Etapa del torneo (ej: "Grupo", "Octavos").
        # - equipo_local/visitante_id: Claves foráneas que referencian el 'id' de la tabla 'equipos'.
        # - ganador_id: También referencia el 'id' de la tabla 'equipos'. Es NULL en caso de empate.
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS partidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fase TEXT NOT NULL,
            equipo_local_id INTEGER,
            equipo_visitante_id INTEGER,
            goles_local INTEGER,
            goles_visitante INTEGER,
            ganador_id INTEGER,
            FOREIGN KEY (equipo_local_id) REFERENCES equipos (id),
            FOREIGN KEY (equipo_visitante_id) REFERENCES equipos (id),
            FOREIGN KEY (ganador_id) REFERENCES equipos (id)
        )
        """)

        # --- Tabla de Configuración ---
        # Almacena pares de llave-valor para guardar el estado del torneo.
        # - llave: El nombre de la configuración (ej: 'equipos_bloqueados').
        # - valor: El valor de esa configuración.
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS config (
            llave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        )""")

        # Confirma y guarda todos los cambios realizados en esta transacción.
        self.conn.commit()
        logger.debug("Estructura de la base de datos verificada/creada.")

    def borrar_todos_los_datos(self):
        """
        Elimina todos los registros de todas las tablas. Es una operación
        destructiva utilizada para reiniciar el torneo por completo.
        """
        logger.warning("Iniciando borrado total de la base de datos...")
        # Se usan sentencias DELETE sin WHERE para borrar todo el contenido.
        self.cursor.execute("DELETE FROM partidos")
        self.cursor.execute("DELETE FROM equipos")
        self.cursor.execute("DELETE FROM config")
        self.conn.commit()
        logger.info("Todos los datos han sido eliminados de la base de datos.")

    def obtener_config(self, llave, valor_por_defecto=None):
        """
        Obtiene un valor de la tabla de configuración.

        Args:
            llave (str): La configuración a buscar.
            valor_por_defecto: El valor a devolver si la llave no se encuentra.

        Returns:
            str or None: El valor encontrado o el valor por defecto.
        """
        self.cursor.execute("SELECT valor FROM config WHERE llave = ?", (llave,))
        resultado = self.cursor.fetchone()
        # El operador ternario devuelve el primer elemento de la tupla si
        # `resultado` no es None, de lo contrario devuelve `valor_por_defecto`.
        return resultado[0] if resultado else valor_por_defecto

    def establecer_config(self, llave, valor):
        """
        Guarda o actualiza un valor en la tabla de configuración.
        Utiliza "INSERT OR REPLACE" que inserta una nueva fila si la llave
        no existe, o reemplaza la fila existente si ya existe.

        Args:
            llave (str): La configuración a establecer.
            valor (any): El valor a guardar (se convierte a string).
        """
        self.cursor.execute("INSERT OR REPLACE INTO config (llave, valor) VALUES (?, ?)", (llave, str(valor)))
        self.conn.commit()
        logger.info(f"Configuración actualizada: '{llave}' = '{valor}'")

    # --- Métodos de conveniencia para configuraciones comunes ---
    def fase_grupos_bloqueada(self):
        """Comprueba si la fase de grupos está bloqueada, devolviendo True o False."""
        return self.obtener_config('fase_grupos_bloqueada') == '1'

    def equipos_bloqueados(self):
        """Comprueba si la gestión de equipos está bloqueada, devolviendo True o False."""
        return self.obtener_config('equipos_bloqueados') == '1'

    def desbloquear_equipos(self):
        """Elimina la bandera de bloqueo de equipos para permitir su edición."""
        self.cursor.execute("DELETE FROM config WHERE llave = 'equipos_bloqueados'")
        self.conn.commit()
        logger.warning("El bloqueo de la lista de equipos ha sido removido.")

    def desbloquear_fase_grupos(self):
        """Elimina la bandera de bloqueo de la fase de grupos."""
        self.cursor.execute("DELETE FROM config WHERE llave = 'fase_grupos_bloqueada'")
        self.conn.commit()
        logger.warning("El bloqueo de la fase de grupos ha sido removido.")

    def _generar_color_unico(self):
        """
        Genera un color hexadecimal aleatorio y verifica que no esté ya en uso.
        El prefijo '_' indica que es un método "privado", pensado para ser
        usado solo por otros métodos dentro de esta misma clase.
        """
        while True:
            # Genera un color aleatorio en formato #RRGGBB.
            color = f"#{random.randint(0, 0xFFFFFF):06x}"
            # Consulta la base de datos para ver si este color ya existe.
            self.cursor.execute("SELECT id FROM equipos WHERE color_hex = ?", (color,))
            # Si `fetchone()` devuelve None, significa que el color no se encontró y es único.
            if self.cursor.fetchone() is None:
                return color

    def agregar_equipo(self, nombre, zona):
        """
        Inserta un nuevo equipo en la base de datos con un color único.
        Maneja posibles errores de integridad (nombres duplicados).

        Returns:
            bool: True si el equipo se agregó con éxito, False en caso contrario.
        """
        try:
            # Primero, obtiene un color que no esté repetido.
            color = self._generar_color_unico()
            # Ejecuta la inserción.
            self.cursor.execute("INSERT INTO equipos (nombre, zona, color_hex) VALUES (?, ?, ?)", (nombre, zona, color))
            self.conn.commit()
            logger.info(f"Equipo '{nombre}' agregado a Zona '{zona}' con color {color}.")
            return True
        except sqlite3.IntegrityError:
            # Este bloque se ejecuta si la inserción viola una restricción
            # UNIQUE (en este caso, el nombre del equipo).
            logger.error(f"Error al agregar: El equipo '{nombre}' ya existe.")
            return False

    def obtener_equipos(self):
        """Obtiene una lista de todos los equipos, ordenados por zona y nombre."""
        self.cursor.execute("SELECT id, nombre, zona, color_hex FROM equipos ORDER BY zona, nombre")
        return self.cursor.fetchall()

    def eliminar_equipo(self, equipo_id):
        """Elimina un equipo de la base de datos usando su ID."""
        self.cursor.execute("DELETE FROM equipos WHERE id = ?", (equipo_id,))
        self.conn.commit()
        logger.info(f"Equipo con ID '{equipo_id}' eliminado.")

    def actualizar_equipo(self, equipo_id, nuevo_nombre, nueva_zona):
        """
        Actualiza el nombre y la zona de un equipo existente.
        Maneja errores si el nuevo nombre ya está en uso.

        Returns:
            bool: True si la actualización fue exitosa, False si no.
        """
        try:
            self.cursor.execute("UPDATE equipos SET nombre = ?, zona = ? WHERE id = ?", (nuevo_nombre, nueva_zona, equipo_id))
            self.conn.commit()
            logger.info(f"Equipo con ID '{equipo_id}' actualizado a: Nombre='{nuevo_nombre}', Zona='{nueva_zona}'.")
            return True
        except sqlite3.IntegrityError:
            logger.error(f"Error al actualizar: El nombre '{nuevo_nombre}' ya está en uso.")
            return False

    def registrar_partido(self, fase, equipo_local_id, equipo_visitante_id, goles_local, goles_visitante):
        """
        Guarda el resultado de un partido en la base de datos.
        Calcula automáticamente el ID del ganador basado en los goles.
        """
        ganador_id = None  # Por defecto, es un empate.
        if goles_local > goles_visitante:
            ganador_id = equipo_local_id
        elif goles_visitante > goles_local:
            ganador_id = equipo_visitante_id

        self.cursor.execute("""
        INSERT INTO partidos (fase, equipo_local_id, equipo_visitante_id, goles_local, goles_visitante, ganador_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (fase, equipo_local_id, equipo_visitante_id, goles_local, goles_visitante, ganador_id))
        self.conn.commit()
        logger.info(f"Partido de '{fase}' registrado: ID_Local={equipo_local_id} vs ID_Visitante={equipo_visitante_id} ({goles_local}-{goles_visitante}).")

    def obtener_partido_por_equipos(self, fase, local_id, visitante_id):
        """
        Busca un partido específico entre dos equipos en una fase determinada.
        Útil para saber si un partido ya ha sido jugado.
        """
        # La cláusula WHERE comprueba ambas combinaciones de localía.
        self.cursor.execute("""
            SELECT id, goles_local, goles_visitante FROM partidos
            WHERE fase = ? AND ((equipo_local_id = ? AND equipo_visitante_id = ?) OR (equipo_local_id = ? AND equipo_visitante_id = ?))
        """, (fase, local_id, visitante_id, visitante_id, local_id))
        return self.cursor.fetchone()

    def actualizar_partido(self, partido_id, goles_local, goles_visitante, ganador_id):
        """Actualiza el resultado de un partido que ya existe en la base de datos."""
        self.cursor.execute("""
            UPDATE partidos SET goles_local = ?, goles_visitante = ?, ganador_id = ?
            WHERE id = ?
        """, (goles_local, goles_visitante, ganador_id, partido_id))
        self.conn.commit()
        logger.info(f"Resultado del partido ID '{partido_id}' actualizado a {goles_local}-{goles_visitante}.")

    def obtener_partidos_fase(self, fase):
        """
        Obtiene una lista de todos los partidos jugados en una fase específica,
        incluyendo los nombres de los equipos en lugar de solo sus IDs.
        """
        # Se utilizan JOINs para cruzar la tabla de partidos con la de equipos
        # (dos veces, una para el local y otra para el visitante).
        self.cursor.execute("""
        SELECT p.id, el.nombre, ev.nombre, p.goles_local, p.goles_visitante
        FROM partidos p
        JOIN equipos el ON p.equipo_local_id = el.id
        JOIN equipos ev ON p.equipo_visitante_id = ev.id
        WHERE p.fase = ?
        """, (fase,))
        return self.cursor.fetchall()

    def reiniciar_fase_grupos(self):
        """Borra únicamente los partidos pertenecientes a la fase de grupos."""
        self.cursor.execute("DELETE FROM partidos WHERE fase = 'Grupo'")
        self.conn.commit()
        logger.warning("Resultados de la fase de grupos han sido reiniciados.")

    def reiniciar_fases_eliminatorias(self):
        """Borra únicamente los partidos que NO pertenecen a la fase de grupos."""
        # Esta consulta elimina todos los registros de la tabla 'partidos'
        # cuya fase sea diferente a 'Grupo', reseteando así Octavos, Cuartos, etc.
        self.cursor.execute("DELETE FROM partidos WHERE fase != 'Grupo'")
        self.conn.commit()
        logger.warning("Resultados de las fases eliminatorias han sido reiniciados.")

    def calcular_tabla_posiciones(self, zona):
        """
        Calcula y devuelve la tabla de posiciones completa para una zona.
        Este es el método más complejo, ya que realiza múltiples consultas a la
        base de datos para agregar los datos de cada equipo.

        Args:
            zona (str): La zona para la cual se calculará la tabla.

        Returns:
            list: Una lista de diccionarios, donde cada diccionario representa
                  una fila de la tabla de posiciones para un equipo.
        """
        # 1. Obtener todos los equipos de la zona.
        self.cursor.execute("SELECT id, nombre FROM equipos WHERE zona = ?", (zona,))
        equipos = self.cursor.fetchall()
        tabla = []

        # 2. Iterar sobre cada equipo para calcular sus estadísticas.
        for equipo_id, nombre_equipo in equipos:
            # Partidos Jugados (PJ)
            self.cursor.execute("SELECT COUNT(*) FROM partidos WHERE (equipo_local_id = ? OR equipo_visitante_id = ?) AND fase = 'Grupo'", (equipo_id, equipo_id))
            pj = self.cursor.fetchone()[0]
            # Partidos Ganados (PG)
            self.cursor.execute("SELECT COUNT(*) FROM partidos WHERE ganador_id = ? AND fase = 'Grupo'", (equipo_id,))
            pg = self.cursor.fetchone()[0]
            # Partidos Empatados (PE)
            self.cursor.execute("SELECT COUNT(*) FROM partidos WHERE (equipo_local_id = ? OR equipo_visitante_id = ?) AND goles_local = goles_visitante AND fase = 'Grupo'", (equipo_id, equipo_id))
            pe = self.cursor.fetchone()[0]
            # Partidos Perdidos (PP) se calcula a partir de los otros valores.
            pp = pj - pg - pe
            # Goles a Favor (GF)
            self.cursor.execute("SELECT SUM(goles_local) FROM partidos WHERE equipo_local_id = ? AND fase = 'Grupo'", (equipo_id,))
            gf_local = self.cursor.fetchone()[0] or 0 # 'or 0' para manejar casos de SUM sobre 0 filas (que devuelve None)
            self.cursor.execute("SELECT SUM(goles_visitante) FROM partidos WHERE equipo_visitante_id = ? AND fase = 'Grupo'", (equipo_id,))
            gf_visitante = self.cursor.fetchone()[0] or 0
            gf = gf_local + gf_visitante
            # Goles en Contra (GC)
            self.cursor.execute("SELECT SUM(goles_visitante) FROM partidos WHERE equipo_local_id = ? AND fase = 'Grupo'", (equipo_id,))
            gc_local = self.cursor.fetchone()[0] or 0
            self.cursor.execute("SELECT SUM(goles_local) FROM partidos WHERE equipo_visitante_id = ? AND fase = 'Grupo'", (equipo_id,))
            gc_visitante = self.cursor.fetchone()[0] or 0
            gc = gc_local + gc_visitante
            # Diferencia de Goles (DG)
            dg = gf - gc
            # Puntos (3 por victoria, 1 por empate)
            puntos = (pg * 3) + pe

            # 3. Construir un diccionario con todas las estadísticas del equipo.
            tabla.append({
                "nombre": nombre_equipo, "pj": pj, "pg": pg, "pe": pe, "pp": pp,
                "gf": gf, "gc": gc, "dg": dg, "puntos": puntos
            })

        # 4. Ordenar la tabla según los criterios de desempate.
        #    Se ordena primero por Puntos, luego por Diferencia de Goles, y finalmente
        #    por Goles a Favor. `reverse=True` para que sea de mayor a menor.
        tabla.sort(key=lambda x: (x['puntos'], x['dg'], x['gf']), reverse=True)
        return tabla

# --- Instancia Única (Singleton) ---
# Se crea una única instancia de la clase Database cuando este módulo es importado.
# El resto de la aplicación (gui.py, logic.py) importará esta variable 'db'
# para asegurarse de que todos los componentes compartan la misma conexión.
db = Database()