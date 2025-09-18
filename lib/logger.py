"""
Módulo de Configuración de Logging

Este archivo se encarga de una única tarea: configurar y proporcionar una
instancia centralizada del sistema de registro (logger) para toda la aplicación.
El uso de un logger es una práctica recomendada sobre el uso de `print()`
para la depuración, ya que permite:

- Asignar niveles de severidad a los mensajes (DEBUG, INFO, WARNING, ERROR).
- Formatear la salida de manera consistente.
- Activar o desactivar fácilmente toda la salida de depuración desde un
  único punto (el archivo de configuración).

La librería `colorlog` se utiliza para mejorar la legibilidad de los logs en
la terminal, asignando colores a cada nivel de severidad.
"""

# Se importa el módulo `logging` estándar de Python.
import logging

# Se importa `colorlog`, una librería externa que extiende `logging` para
# añadir color a la salida de la consola.
import colorlog

# Se importa el módulo de configuración para poder leer si el logging
# debe estar activado o no.
from . import config


def configurar_logger():
    """
    Crea, configura y devuelve un objeto logger para la aplicación.

    Esta función es el núcleo de la configuración. Comprueba el valor de
    `LOGGING_ACTIVADO` en el archivo `config.py`.
    - Si es `True`, configura un logger que imprime mensajes coloridos en la
      consola para todos los niveles a partir de DEBUG.
    - Si es `False`, configura un logger "silencioso" que no realiza ninguna
      acción, evitando así cualquier salida en la consola en un entorno de
      producción.

    Returns:
        logging.Logger: La instancia del logger configurada.
    """
    # Obtiene (o crea si no existe) un logger con el nombre "torneo_app".
    # Usar un nombre específico permite que toda la app comparta el mismo logger.
    log = logging.getLogger("torneo_app")

    # Condición principal: solo se configura el handler si el logging está
    # activado Y si el logger no tiene ya handlers configurados (esto evita
    # añadir handlers duplicados si la función se llamara varias veces).
    if config.LOGGING_ACTIVADO and not log.handlers:
        # Establece el nivel mínimo de severidad que el logger procesará.
        # `logging.DEBUG` es el nivel más bajo, por lo que capturará todo.
        log.setLevel(logging.DEBUG)

        # Crea un 'handler', que es el responsable de enviar los registros
        # a un destino. `StreamHandler` lo envía a la consola (terminal).
        handler = colorlog.StreamHandler()

        # Define el formato de cada línea de log.
        # - `%(log_color)s`: Inyecta el código de color para el nivel del mensaje.
        # - `%(levelname)-8s`: El nombre del nivel (ej: "INFO"), alineado a 8 caracteres.
        # - `%(reset)s`: Restablece el color.
        # - `%(blue)s%(message)s`: El mensaje del log en color azul.
        formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s',
            # Mapea cada nivel de log a un color específico.
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red,bg_white',
            }
        )

        # Asocia el formateador al handler.
        handler.setFormatter(formatter)
        # Asocia el handler al logger.
        log.addHandler(handler)

    # Si el logging está explícitamente desactivado en el archivo de configuración.
    elif not config.LOGGING_ACTIVADO:
        # Se añade un `NullHandler`, que es un "agujero negro" para los logs.
        # Recibe los mensajes de log pero no hace nada con ellos. Esto es más
        # eficiente que llenar el código de `if config.LOGGING_ACTIVADO:`
        # antes de cada llamada al logger.
        log.addHandler(logging.NullHandler())

    # Devuelve la instancia del logger, ya sea configurada o silenciosa.
    return log

# --- Instancia Única (Singleton) ---
# Se llama a la función de configuración UNA SOLA VEZ, cuando este módulo es
# importado por primera vez.
# La instancia resultante se guarda en la variable 'logger'.
# Otros módulos (gui.py, database.py, etc.) importarán esta variable
# para usar el mismo logger configurado en toda la aplicación.
logger = configurar_logger()