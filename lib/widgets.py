"""
Módulo de Widgets Personalizados (Componentes Reutilizables de GUI)

Este archivo contiene clases que extienden la funcionalidad base de Tkinter
para crear componentes de interfaz gráfica (widgets) a medida. El objetivo
principal es encapsular funcionalidades complejas y repetitivas de la GUI
en clases autocontenidas y reutilizables.

Esto sigue el principio de "No te repitas" (Don't Repeat Yourself - DRY)
y ayuda a que el código del módulo principal de la GUI (`gui.py`) sea
mucho más limpio, legible y fácil de mantener, ya que puede instanciar
estos widgets complejos con una sola línea de código.

Widgets definidos:
- Tooltip: Una clase que añade mensajes emergentes (tooltips) a cualquier widget.
- CollapsibleFrame: Un widget de tipo "acordeón" que puede mostrar y ocultar
  su contenido, ideal para organizar la información verticalmente.
"""

# Se importa la librería `tkinter` completa como 'tk' para los componentes base.
import tkinter as tk

# Se importa el submódulo `ttk` que contiene los widgets temáticos y de
# apariencia más moderna.
from tkinter import ttk


# --- Clase Auxiliar para Crear Tooltips ---
class Tooltip:
    """
    Crea un mensaje emergente (tooltip) para un widget de Tkinter.

    Esta clase no es un widget en sí misma, sino una clase "ayudante" que se
    asocia a un widget existente. Se encarga de escuchar los eventos del ratón
    (cuando entra y sale del área del widget) para mostrar y ocultar una pequeña
    ventana con texto informativo.
    """

    def __init__(self, widget, text):
        """
        Inicializa el tooltip y lo asocia a un widget.

        Args:
            widget (tk.Widget): El widget al cual se le añadirá el tooltip.
            text (str): El texto que se mostrará en el mensaje emergente.
        """
        # Guarda una referencia al widget "padre" y al texto.
        self.widget = widget
        self.text = text
        self.tooltip_window = None  # Inicialmente, no hay ninguna ventana de tooltip.

        # --- Manejo de Eventos ---
        # `bind` asocia un evento a una función (callback).
        # Cuando el cursor del ratón entra en el área del widget, se llama a `show_tooltip`.
        self.widget.bind("<Enter>", self.show_tooltip)
        # Cuando el cursor del ratón sale del área del widget, se llama a `hide_tooltip`.
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        """

        Crea y muestra la ventana del tooltip cerca del cursor del ratón.
        Esta función es el "callback" que se ejecuta con el evento <Enter>.

        Args:
            event: El objeto de evento de Tkinter (no se usa directamente,
                   pero es requerido por la firma de la función `bind`).
        """
        # Pide al widget las coordenadas de su "caja" (bounding box).
        x, y, _, _ = self.widget.bbox("insert")
        # Convierte las coordenadas locales del widget a coordenadas globales de la pantalla.
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        # Crea una nueva ventana de nivel superior (`Toplevel`), que es una
        # ventana independiente sin los controles estándar (minimizar, cerrar, etc.).
        self.tooltip_window = tk.Toplevel(self.widget)
        # `wm_overrideredirect(True)` elimina los bordes y la barra de título de la ventana.
        self.tooltip_window.wm_overrideredirect(True)
        # Posiciona la ventana en las coordenadas calculadas.
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # Crea una etiqueta (Label) dentro de la ventana del tooltip para mostrar el texto.
        label = tk.Label(self.tooltip_window, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self, event):
        """
        Destruye la ventana del tooltip.
        Esta función es el "callback" que se ejecuta con el evento <Leave>.
        """
        # Si la ventana del tooltip existe, destrúyela.
        if self.tooltip_window:
            self.tooltip_window.destroy()
        # Restablece la variable a None para indicar que ya no hay un tooltip visible.
        self.tooltip_window = None


# --- Widget Personalizado: Frame Colapsable (Acordeón) ---
class CollapsibleFrame(ttk.Frame):
    """
    Un widget que consiste en un Frame de `ttk` que puede ser expandido o
    colapsado por el usuario haciendo clic en un botón en su cabecera.

    Hereda de `ttk.Frame`, por lo que se puede usar como cualquier otro frame
    para contener otros widgets. La diferencia es que encapsula la lógica
    para mostrar u ocultar su contenido.
    """

    def __init__(self, parent, text="", expanded=True):
        """
        Inicializa el Frame colapsable.

        Args:
            parent (tk.Widget): El widget maestro que contendrá este frame.
            text (str): El texto del título que aparecerá en la cabecera.
            expanded (bool): El estado inicial del widget (expandido o colapsado).
        """
        # Llama al constructor de la clase padre (ttk.Frame).
        super().__init__(parent)

        # Guarda las propiedades iniciales.
        self.text = text
        self._expanded = expanded  # Se usa '_' para indicar que es una variable "privada".

        # --- Construcción de la Cabecera ---
        # La cabecera es un frame interno que contiene el botón de despliegue y el título.
        self.header_frame = ttk.Frame(self)
        self.header_frame.pack(fill="x", expand=True, pady=(0, 2))

        # El botón de despliegue (toggle) muestra una flecha que cambia de dirección.
        # Su `command` está asociado al método `toggle` de esta misma clase.
        self.toggle_button = ttk.Button(self.header_frame, text="▼" if expanded else "▶",
                                        width=3, command=self.toggle)
        self.toggle_button.pack(side="left")

        # La etiqueta que muestra el título del frame.
        ttk.Label(self.header_frame, text=self.text, font=("Arial", 10, "bold")).pack(side="left", padx=5)

        # --- Construcción del Contenedor ---
        # Este es el frame que se mostrará u ocultará.
        # Otros widgets (botones, etiquetas, etc.) se deben añadir a ESTE `container`,
        # no directamente al `CollapsibleFrame`.
        self.container = ttk.Frame(self, style='Content.TFrame', padding=10)

        # Si el estado inicial es expandido, se muestra el contenedor.
        if self._expanded:
            self.container.pack(fill="x", expand=True, padx=5, pady=(0, 5))

    def toggle(self):
        """
        Cambia el estado del frame entre expandido y colapsado.
        Este método es llamado por el `toggle_button`.
        """
        # Si el frame está actualmente expandido, lo colapsamos.
        if self._expanded:
            # `pack_forget()` oculta el widget sin destruirlo, manteniendo su
            # estado y contenido para cuando se vuelva a mostrar.
            self.container.pack_forget()
            # Cambia el texto del botón para indicar la acción de expandir.
            self.toggle_button.configure(text="▶")
        # Si el frame está actualmente colapsado, lo expandimos.
        else:
            # `pack()` vuelve a mostrar el widget en la ventana.
            self.container.pack(fill="x", expand=True, padx=5, pady=(0, 5))
            # Cambia el texto del botón para indicar la acción de colapsar.
            self.toggle_button.configure(text="▼")

        # Invierte el valor booleano del estado.
        self._expanded = not self._expanded