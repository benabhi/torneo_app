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
- ActionButtonBar: Un contenedor estandarizado para las barras de botones inferiores.
- MatchRowWidget: Un widget que representa visualmente una fila de partido,
  ya sea jugado o por jugar.
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

# --- Widget Personalizado: Barra de Botones de Acción ---
class ActionButtonBar(ttk.Frame):
    """
    Un contenedor estandarizado para las barras de botones inferiores de cada etapa.
    Se encarga de crear la estructura de centrado y proporciona un método
    sencillo para añadir botones.
    """
    def __init__(self, parent, height=50, **kwargs):
        """
        Inicializa la barra de botones.
        """
        super().__init__(parent, height=height, **kwargs)
        self.pack(side="bottom", fill="x", padx=10)
        self.pack_propagate(False)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0) # Columna central para el frame de botones
        self.columnconfigure(2, weight=1)

        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=0, column=1)

    def add_button(self, **button_options):
        """
        Crea y añade un nuevo botón a la barra.

        Args:
            **button_options: Opciones para el constructor de ttk.Button (text, image, command, etc.).

        Returns:
            ttk.Button: La instancia del botón creado.
        """
        button = ttk.Button(self.button_frame, **button_options)
        button.pack(side="left", padx=5)
        return button

# --- Widget Personalizado: Fila de Partido ---
class MatchRowWidget(ttk.Frame):
    """
    Representa una fila completa para un partido de eliminatorias.
    Puede ser 'editable' (con campos de entrada) o 'jugado' (mostrando resultados).
    """
    def __init__(self, parent, local_data, visitante_data, vcmd=None, editable=False, resultado=None, **kwargs):
        super().__init__(parent, style='Content.TFrame', **kwargs)

        self.local_data = local_data
        self.visitante_data = visitante_data
        self.editable = editable
        self.vcmd = vcmd

        self._configure_grid()

        if editable:
            self._create_editable_row()
        else:
            self._create_played_row(resultado)

    def _configure_grid(self):
        """Configura las columnas para alinear los componentes."""
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=0)
        self.columnconfigure(4, weight=1)

    def _create_team_label(self, parent, team_data, compound_side):
        """Crea la etiqueta de un equipo, con o sin escudo."""
        text = f" {team_data['nombre']} "
        if team_data.get('escudo'):
            return ttk.Label(parent, text=text, image=team_data['escudo'], compound=compound_side, style='Content.TLabel')
        else:
            return ttk.Label(parent, text=text, style='Content.TLabel')

    def _create_editable_row(self):
        """Construye la fila para un partido pendiente."""
        local_label = self._create_team_label(self, self.local_data, "right")
        local_label.grid(row=0, column=0, sticky="e", padx=5)

        self.goles_local = ttk.Entry(self, width=4, justify="center", validate='key', validatecommand=self.vcmd)
        self.goles_local.grid(row=0, column=1, padx=2)

        ttk.Label(self, text="vs", style='Content.TLabel').grid(row=0, column=2)

        self.goles_visitante = ttk.Entry(self, width=4, justify="center", validate='key', validatecommand=self.vcmd)
        self.goles_visitante.grid(row=0, column=3, padx=2)

        visitante_label = self._create_team_label(self, self.visitante_data, "left")
        visitante_label.grid(row=0, column=4, sticky="w", padx=5)

    def _create_played_row(self, resultado):
        """Construye la fila para un partido ya jugado."""
        goles_l, goles_v = resultado
        font_normal = ("Arial", 10); font_bold = ("Arial", 10, "bold")

        style_local, font_local = 'Normal.TLabel', font_normal
        style_visitante, font_visitante = 'Normal.TLabel', font_normal

        if goles_l > goles_v:
            style_local, font_local = 'Winner.TLabel', font_bold
            style_visitante, font_visitante = 'Loser.TLabel', font_normal
        elif goles_v > goles_l:
            style_local, font_local = 'Loser.TLabel', font_normal
            style_visitante, font_visitante = 'Winner.TLabel', font_bold

        local_label = self._create_team_label(self, self.local_data, "right")
        local_label.grid(row=0, column=0, sticky="e", padx=5)

        ttk.Label(self, text=str(goles_l), anchor="center", style=style_local, font=font_local, width=4).grid(row=0, column=1, padx=2)
        ttk.Label(self, text="-", anchor="center", style='Normal.TLabel', font=font_normal).grid(row=0, column=2)
        ttk.Label(self, text=str(goles_v), anchor="center", style=style_visitante, font=font_visitante, width=4).grid(row=0, column=3, padx=2)

        visitante_label = self._create_team_label(self, self.visitante_data, "left")
        visitante_label.grid(row=0, column=4, sticky="w", padx=5)

    def get_result_entries(self):
        """Devuelve los widgets de entrada de goles si la fila es editable."""
        if self.editable:
            return (self.goles_local, self.goles_visitante)
        return None