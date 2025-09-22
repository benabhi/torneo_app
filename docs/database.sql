-- Tabla para almacenar la información de cada equipo participante.
-- - 'nombre' y 'color_hex' deben ser únicos para evitar duplicados.
CREATE TABLE IF NOT EXISTS equipos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    zona TEXT NOT NULL,
    color_hex TEXT NOT NULL UNIQUE
);

-- Tabla para almacenar cada partido jugado en el torneo.
-- - Utiliza claves foráneas (FOREIGN KEY) para relacionar los IDs
--   con la tabla 'equipos', asegurando la integridad de los datos.
-- - 'ganador_id' es NULL en caso de empate.
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
);

-- Tabla de tipo llave-valor para guardar el estado del torneo.
-- - Se usa para almacenar 'flags' como si la lista de equipos o la
--   fase de grupos ya han sido bloqueadas.
CREATE TABLE IF NOT EXISTS config (
    llave TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);