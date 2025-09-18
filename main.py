"""
Punto de Entrada Principal de la Aplicación

Este es el script que se debe ejecutar para iniciar el gestor de torneos.
Su responsabilidad es mínima pero fundamental:
1. Importar la clase principal de la interfaz gráfica (`App` desde `gui.py`).
2. Intentar cargar un ícono para la ventana.
3. Crear una instancia de la clase `App`.
4. Iniciar el bucle de eventos principal de Tkinter (`mainloop`), que pone
   en marcha la aplicación y la mantiene en ejecución.
"""

# Se importa el módulo `os` para interactuar con el sistema operativo,
# específicamente para construir rutas de archivos de manera robusta.
import os

# Se importa `PhotoImage` de Tkinter como una forma básica de cargar imágenes.
# Funciona bien con formatos como .png y .gif, pero no con .ico.
from tkinter import PhotoImage

# Se importa el módulo `gui` que contiene la clase principal `App`.
from lib import gui


# --- Manejo de Dependencia Opcional (Pillow) ---
# Se intenta importar las librerías `Image` y `ImageTk` de Pillow (PIL).
# Pillow es más potente que PhotoImage y soporta más formatos, incluyendo .ico
# en Windows, y permite un mejor manejo de transparencias.
try:
    from PIL import Image, ImageTk
    # Si la importación tiene éxito, se establece una bandera para usar Pillow.
    PIL_SUPPORT = True
except ImportError:
    # Si Pillow no está instalado, la importación falla y se establece una
    # bandera para usar la solución de respaldo (PhotoImage de Tkinter).
    PIL_SUPPORT = False


def main():
    """
    Función principal que crea y lanza la aplicación.
    """

    # 1. Crear una instancia de la aplicación.
    #    Esto ejecuta el método `__init__` de la clase `App`, que construye
    #    toda la interfaz gráfica en memoria.
    app = gui.App()

    # 2. Intentar establecer el ícono de la ventana.
    #    Este bloque está envuelto en un `try...except` para que, si falla
    #    la carga del ícono, la aplicación pueda continuar ejecutándose
    #    sin él en lugar de cerrarse con un error.
    try:
        # `os.path.abspath(__file__)` obtiene la ruta absoluta de este script.
        # `os.path.dirname(...)` obtiene el directorio que contiene el script.
        # Esto asegura que la ruta base sea correcta sin importar desde dónde
        # se ejecute el programa.
        base_path = os.path.dirname(os.path.abspath(__file__))

        # Se construye una ruta tentativa para el ícono.
        icon_path = os.path.join(base_path, 'lib', 'assets', 'icon.png')

        # Si el ícono no se encuentra en la primera ruta, se intenta buscar
        # directamente en la carpeta raíz del proyecto.
        if not os.path.exists(icon_path):
            icon_path = os.path.join(base_path, 'icon.png')

        # Si se encuentra un archivo de ícono en alguna de las rutas.
        if os.path.exists(icon_path):
            # Si se dispone de soporte de Pillow (la mejor opción).
            if PIL_SUPPORT:
                image = Image.open(icon_path)
                photo = ImageTk.PhotoImage(image)
                # `wm_iconphoto` con `True` permite usar objetos de PhotoImage complejos.
                app.wm_iconphoto(True, photo)
            # Si no, se usa la opción básica de Tkinter.
            else:
                photo = PhotoImage(file=icon_path)
                # `iconphoto` con `False` es la forma estándar de Tkinter.
                app.iconphoto(False, photo)
        # Si el archivo del ícono no se encuentra en ninguna de las rutas esperadas.
        else:
             print(f"Advertencia: No se pudo encontrar el icono de la aplicación en '{icon_path}'.")

    # Si ocurre cualquier otro error durante la carga del ícono (ej: archivo corrupto).
    except Exception as e:
        print(f"Advertencia: No se pudo cargar el icono de la aplicación.")
        print(f"Error: {e}")

    # 3. Iniciar el bucle de eventos principal de la aplicación.
    #    Esta línea es crucial. `mainloop()` pone a Tkinter en un bucle infinito
    #    donde escucha eventos (clics del ratón, pulsaciones de teclas, etc.)
    #    y actualiza la GUI en consecuencia. El programa permanecerá en esta
    #    línea hasta que el usuario cierre la ventana.
    app.mainloop()

# --- Punto de Entrada del Script ---
# Esta es una construcción estándar en Python.
# El bloque de código dentro de este `if` solo se ejecutará cuando este archivo
# (`main.py`) sea ejecutado directamente por el intérprete de Python.
# Si otro archivo importara `main.py` (ej: `import main`), este bloque
# NO se ejecutaría. Esto lo convierte en el punto de partida ideal para la aplicación.
if __name__ == "__main__":
    main()