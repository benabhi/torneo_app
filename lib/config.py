"""
Módulo de Configuración

Este archivo centraliza las constantes y parámetros de configuración de la
aplicación. Permite modificar el comportamiento del programa fácilmente sin
tener que cambiar la lógica principal.
"""

# --- CONFIGURACIÓN DE BOTONES DE PRUEBA ---
# Establecer en True para mostrar los botones de "Autogenerar".
# Establecer en False para ocultarlos en una versión "de producción".
BOTONES_PRUEBA_VISIBLES = True

# --- CONFIGURACIÓN DE LA ESTRUCTURA DEL TORNEO ---
# Define los nombres de las zonas/grupos. Puedes tener 2, 4, 8...
# Ejemplo para 4 zonas: ZONAS_DEL_TORNEO = ["A", "B", "C", "D"]
ZONAS_DEL_TORNEO = ["A", "B"]

# Define cuántos equipos por zona clasifican a la fase eliminatoria.
# El total de clasificados debe ser una potencia de 2 (4, 8, 16, 32...).
# Total = len(ZONAS_DEL_TORNEO) * EQUIPOS_CLASIFICAN_POR_ZONA
EQUIPOS_CLASIFICAN_POR_ZONA = 8

# --- INICIO DE LA MODIFICACIÓN ---
# Define el número máximo de equipos permitidos por zona.
# Esto previene que se agreguen equipos de más en la fase de gestión.
# Un valor común es el doble de los que clasifican.
MAX_EQUIPOS_POR_ZONA = EQUIPOS_CLASIFICAN_POR_ZONA * 2
# --- FIN DE LA MODIFICACIÓN ---

# --- CONFIGURACIÓN DE LOGGING ---
# Establecer en True para mostrar logs detallados en la terminal.
# Establecer en False para una operación más silenciosa.
LOGGING_ACTIVADO = True

# --- CONFIGURACIÓN VISUAL ---
# Establecer en True para que los escudos de los equipos en las fases
# eliminatorias se muestren con el color único de cada equipo.
# Si es False, los escudos no se mostraran
ESCUDOS_VISIBLES = True