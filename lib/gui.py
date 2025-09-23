"""
Módulo de Interfaz Gráfica (GUI) - El Corazón Visual de la Aplicación

Este archivo define la clase principal `App`, que orquesta toda la interfaz
gráfica del usuario. Hereda de `tkinter.Tk` para convertirse en la ventana
principal de la aplicación.

Su rol es actuar como el "Controlador" en un patrón similar a MVC (Modelo-Vista-Controlador):
- **Vista:** Construye y organiza todos los widgets visibles (botones, tablas, etc.).
- **Controlador:** Captura las interacciones del usuario (clics, selecciones) y
  llama a los módulos de lógica (`logic.py`) o de datos (`database.py`) para
  procesar las solicitudes. Luego, actualiza la Vista con los nuevos datos.

La estructura está dividida en tres pestañas principales, cada una manejando
una etapa del torneo, lo que guía al usuario a través de un flujo de trabajo lógico.
"""

# Se importa la librería `tkinter` completa como 'tk' para los componentes base.
import tkinter as tk
# Se importan los submódulos `ttk` (widgets modernos) y `messagebox` (ventanas emergentes).
from tkinter import ttk, messagebox
# Se importa 'random' para la funcionalidad de autogeneración de resultados.
import random

# --- Importaciones de Módulos Propios ---
# Se importan los otros componentes de la aplicación.
from . import database          # Capa de acceso a datos.
from . import logic             # Capa de reglas de negocio del torneo.
from . import widgets           # Componentes de GUI personalizados.
from . import config            # Archivo de configuración central.
from .logger import logger      # Sistema de registro de eventos.
import tkfontawesome as fa      # Librería para usar iconos en la GUI.


# --- CLASE PRINCIPAL DE LA APLICACIÓN ---
class App(tk.Tk):
    """
    La clase principal que representa la ventana de la aplicación.
    Hereda de tk.Tk y encapsula todos los widgets, la lógica de eventos
    y los métodos para actualizar la interfaz.
    """

    def __init__(self):
        """
        Constructor de la aplicación. Se ejecuta una sola vez al iniciar.
        Es responsable de configurar la ventana, inicializar variables de estado,
        cargar recursos y construir toda la jerarquía de widgets.
        """
        # Llama al constructor de la clase padre (tk.Tk) para inicializar la ventana.
        super().__init__()

        # Se registra una función de validación con Tkinter. `self.register`
        # devuelve un "wrapper" que puede ser llamado desde el intérprete Tcl interno
        # de Tkinter. Esto es necesario para que los widgets `Entry` puedan usar
        # una función de Python para su validación.
        # '%P' es un código de sustitución que le dice a Tkinter que pase el
        # valor que TENDRÁ el Entry si la edición es permitida.
        self.vcmd = (self.register(self._validar_solo_numeros), '%P')

        # --- 1. Configuración de la Ventana Principal ---
        self.title("Gestor de Torneo de Fútbol")

        # Define las dimensiones de la ventana.
        window_width = 960
        window_height = 600
        # Obtiene las dimensiones de la pantalla del usuario.
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        # Calcula las coordenadas X e Y para centrar la ventana en la pantalla.
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2) - 30 # Un pequeño ajuste vertical.
        # Establece la geometría y posición de la ventana.
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        # Impide que el usuario pueda cambiar el tamaño de la ventana.
        self.resizable(False, False)

        # --- 2. Configuración de Estilos Gráficos (ttk.Style) ---
        # Se crea un objeto Style para personalizar la apariencia de los widgets ttk.
        style = ttk.Style(self)
        # Posiciona las pestañas del Notebook en la parte superior.
        style.configure('TNotebook', tabposition='n')
        # Define el padding y la fuente para las etiquetas de las pestañas.
        style.configure('TNotebook.Tab', padding=(30, 8), font=('Arial', 10, 'bold'))
        # Crea estilos personalizados que se usarán en widgets específicos.
        style.configure('Champion.TFrame', background='#f0f0f0', relief='solid', borderwidth=1)
        style.configure('Danger.TButton', foreground='black', background='#ffcdd2', font=('Arial', 9, 'bold'), borderwidth=1, relief='raised')
        style.map('Danger.TButton', background=[('active', '#ef9a9a')]) # Color cuando el botón está activo/presionado.
        style.configure('Test.TButton', foreground='black', background='#fff9c4', font=('Arial', 9), borderwidth=1, relief='raised')
        style.map('Test.TButton', background=[('active', '#fff59d')])
        style.configure('Content.TFrame', background='#fafafa', relief='solid', borderwidth=1)
        style.configure('Content.TLabel', background='#fafafa')
        style.configure('Winner.TLabel', foreground='green', background='#fafafa')
        style.configure('Loser.TLabel', foreground='red', background='#fafafa')
        style.configure('Normal.TLabel', background='#fafafa')

        # --- 3. Carga de Recursos (Iconos) ---
        # Se cargan todos los iconos una sola vez al inicio para optimizar el rendimiento.
        # `tkfontawesome.icon_to_image` convierte un icono de FontAwesome en un objeto de imagen de Tkinter.
        self.icon_add = fa.icon_to_image("plus-circle", fill="green", scale_to_height=16)
        self.icon_edit = fa.icon_to_image("pencil-alt", fill="#3366cc", scale_to_height=16)
        self.icon_delete = fa.icon_to_image("trash-alt", fill="#c00", scale_to_height=16)
        self.icon_delete_all = fa.icon_to_image("dumpster-fire", fill="#c00", scale_to_height=16)
        self.icon_generate = fa.icon_to_image("cogs", fill="#555", scale_to_height=16)
        self.icon_next = fa.icon_to_image("arrow-circle-right", fill="blue", scale_to_height=16)
        self.icon_reset = fa.icon_to_image("undo", fill="#c00", scale_to_height=16)
        self.icon_save = fa.icon_to_image("save", fill="blue", scale_to_height=16)
        self.icon_clear = fa.icon_to_image("broom", fill="#555", scale_to_height=16)
        self.icon_confirm = fa.icon_to_image("check-circle", fill="green", scale_to_height=16)
        self.icon_trophy = fa.icon_to_image("trophy", fill="gold", scale_to_height=16)
        self.icon_medal = fa.icon_to_image("medal", fill="royalblue", scale_to_height=24)
        self.icon_shield = fa.icon_to_image("shield-alt", fill="#888", scale_to_height=14)

        # --- 4. Inicialización de Variables de Estado de la GUI ---
        # Almacena la tupla del partido seleccionado en la lista de pendientes.
        self.partido_seleccionado = None
        # Diccionario para mantener referencias a los widgets de entrada de goles en las fases eliminatorias.
        self.match_row_widgets_por_fase = {}
        # Caché para almacenar los escudos ya coloreados y evitar regenerarlos.
        self.escudos_coloreados_cache = {}
        # Diccionario para acceder rápidamente a los datos de un equipo por su nombre.
        self.equipos_data = {}
        # Lista para mantener referencias a las etiquetas de colores en la tabla de equipos, para poder borrarlas.
        self.color_labels = []

        # --- 5. Construcción de la Estructura Principal de la GUI ---
        # Se empaqueta la BARRA DE ESTADO PRIMERO para que reserve su espacio en la parte inferior.
        self.status_bar = ttk.Frame(self, relief="sunken", height=25)
        self.status_bar.pack(side="bottom", fill="x", padx=1, pady=1)
        self.status_bar.pack_propagate(False) # Evita que el frame cambie de tamaño

        # Etiqueta para mostrar el total de equipos. Se alinea a la izquierda.
        self.status_label_equipos = ttk.Label(self.status_bar, text="Equipos: 0", anchor="w")
        self.status_label_equipos.pack(side="left", padx=10, pady=2)

        # Etiqueta para mostrar la fase actual del torneo.
        self.status_label_fase = ttk.Label(self.status_bar, text="Etapa: Equipos", anchor="w")
        self.status_label_fase.pack(side="left", padx=10, pady=2)

        # Etiqueta para mensajes de bloqueo.
        self.status_label_bloqueo = ttk.Label(self.status_bar, text="", foreground="blue", font=("Arial", 9, "italic"), anchor="w")
        self.status_label_bloqueo.pack(side="left", padx=10, pady=2)

        # Etiqueta para mensajes de estado. Se alinea a la derecha para que no
        # se solape con las otras etiquetas.
        self.status_label_mensaje = ttk.Label(self.status_bar, text="Listo", anchor="e")
        self.status_label_mensaje.pack(side="right", padx=10, pady=2)

        # AHORA se empaqueta el NOTEBOOK, que ocupará todo el espacio restante.
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")
        self.notebook.enable_traversal() # Permite navegar entre pestañas con Ctrl+Tab.

        # Se crean los Frames (contenedores) para cada pestaña.
        self.frame_equipos = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_equipos, text="Etapa 1: Equipos")
        self.frame_grupos = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_grupos, text="Etapa 2: Grupos")
        self.frame_eliminatorias = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_eliminatorias, text="Etapa 3: Eliminatorias")

        # --- 6. Llamada a los Métodos Constructores de Widgets ---
        # Se llama a un método separado para construir el contenido de cada pestaña,
        # manteniendo el constructor `__init__` más limpio y organizado.
        self.crear_widgets_equipos()
        self.crear_widgets_grupos()
        self.crear_widgets_eliminatorias()

        # --- 7. Sincronización Inicial de la GUI ---
        # Llama al método que carga todos los datos iniciales y establece el estado correcto de la UI.
        self.actualizar_todas_las_vistas()

    def _validar_solo_numeros(self, P):
        """
        Función de validación utilizada por los widgets Entry de goles.

        Esta función es llamada por Tkinter cada vez que el usuario intenta
        modificar el contenido del Entry. Devuelve `True` solo si el nuevo
        contenido (`P`) es una cadena de dígitos o una cadena vacía (para
        permitir que el usuario borre el campo).

        Args:
            P (str): El valor que tendría el Entry si se permitiera la edición.

        Returns:
            bool: True para permitir el cambio, False para rechazarlo.
        """
        if str.isdigit(P) or P == "":
            return True
        return False

    def _actualizar_barra_estado(self, mensaje="Listo"):
        """
        Actualiza la información mostrada en la barra de estado inferior.

        Este método centraliza la lógica para refrescar las etiquetas de la barra
        de estado, como el número total de equipos y la fase actual del torneo.
        También permite mostrar un mensaje temporal sobre la última acción realizada.

        Args:
            mensaje (str): El mensaje a mostrar en la parte derecha de la barra.
                           Por defecto es "Listo".
        """
        # Actualiza el contador de equipos consultando la base de datos.
        total_equipos = len(database.db.obtener_equipos())
        self.status_label_equipos.config(text=f"Equipos: {total_equipos}")

        # Determina y muestra la fase actual del torneo.
        etapa_actual_texto = "Equipos"
        if database.db.fase_grupos_bloqueada():
            etapa_actual_texto = "Eliminatorias"
        elif database.db.equipos_bloqueados():
            etapa_actual_texto = "Grupos"

        self.status_label_fase.config(text=f"Etapa: {etapa_actual_texto}")

        # Muestra el mensaje de estado pasado como argumento.
        self.status_label_mensaje.config(text=mensaje)

    def _update_ui_state(self):
        """
        Gestiona el estado de la interfaz (habilitar/deshabilitar widgets).
        Este método centraliza toda la lógica que decide qué puede hacer el
        usuario en cada momento del torneo. Se llama cada vez que ocurre una
        acción importante (agregar equipo, registrar partido, etc.).
        """
        # Obtiene el estado actual del torneo desde la base de datos.
        equipos_estan_bloqueados = database.db.equipos_bloqueados()
        grupos_estan_bloqueados = database.db.fase_grupos_bloqueada()

        # Actualiza el mensaje de bloqueo en la barra de estado
        bloqueo_msg = ""
        if grupos_estan_bloqueados:
            bloqueo_msg = "Etapa 2 y 3: Bloqueadas"
        elif equipos_estan_bloqueados:
            bloqueo_msg = "Etapa 1: Bloqueada"
        self.status_label_bloqueo.config(text=bloqueo_msg)

        # Calcula cuántos equipos hay en cada zona.
        equipos_por_zona = {zona: 0 for zona in config.ZONAS_DEL_TORNEO}
        num_equipos = 0
        equipos_db = database.db.obtener_equipos()
        for _, _, zona, _ in equipos_db:
            num_equipos += 1
            if zona in equipos_por_zona:
                equipos_por_zona[zona] += 1

        estado_botones_eliminar = 'normal' if num_equipos > 0 else 'disabled'
        todos_los_grupos_llenos = all(count == config.MAX_EQUIPOS_POR_ZONA for count in equipos_por_zona.values())

        # --- Lógica para la Pestaña "Gestionar Equipos" ---
        if hasattr(self, 'btn_agregar'):
            is_bloqueado = equipos_estan_bloqueados
            estado = 'disabled' if is_bloqueado else 'normal'

            self.entry_nombre.config(state=estado)
            self.combo_zona.config(state=estado)
            self.btn_agregar.config(state=estado)
            self.btn_modificar.config(state='disabled' if is_bloqueado or not self.tree_equipos.selection() else 'normal')
            self.btn_eliminar_seleccionado.config(state='disabled' if is_bloqueado or not self.tree_equipos.selection() else 'normal')
            self.btn_eliminar_datos_etapa1.config(state='disabled' if is_bloqueado else estado_botones_eliminar)
            if config.BOTONES_PRUEBA_VISIBLES:
                self.btn_generar_prueba_etapa1.config(state=estado)

            estado_confirmar = 'normal' if todos_los_grupos_llenos and not is_bloqueado else 'disabled'
            self.btn_confirmar_etapa1.config(state=estado_confirmar)

            if not is_bloqueado:
                zona_seleccionada = self.combo_zona.get()
                if zona_seleccionada and equipos_por_zona.get(zona_seleccionada, 0) >= config.MAX_EQUIPOS_POR_ZONA:
                    self.btn_agregar.config(state='disabled')
                    widgets.Tooltip(self.btn_agregar, f"La Zona '{zona_seleccionada}' está llena (máx: {config.MAX_EQUIPOS_POR_ZONA}).")
                else:
                    widgets.Tooltip(self.btn_agregar, "Añadir el equipo a la base de datos.")

        # Habilita o deshabilita la pestaña de Fase de Grupos.
        self.notebook.tab(1, state='normal' if equipos_estan_bloqueados else 'disabled')

        # --- Lógica para la Pestaña "Fase de Grupos" ---
        if hasattr(self, 'btn_confirmar_etapa2'):
            is_bloqueado = grupos_estan_bloqueados
            estado = 'disabled' if is_bloqueado else 'normal'

            for child in self.frame_grupos.winfo_children():
                try: child.config(state=estado)
                except tk.TclError: pass

            if is_bloqueado:
                self.btn_volver_etapa2.config(state='disabled')
                self.btn_eliminar_datos_etapa2.config(state='disabled')
                if config.BOTONES_PRUEBA_VISIBLES: self.btn_generar_prueba_etapa2.config(state='disabled')
                self.btn_confirmar_etapa2.config(state='disabled')
            else:
                todos_jugados = not any(logic.generar_fixture_zona(zona) for zona in config.ZONAS_DEL_TORNEO)
                partidos_de_grupo = database.db.obtener_partidos_fase('Grupo')

                self.btn_volver_etapa2.config(state='normal')
                self.btn_eliminar_datos_etapa2.config(state='normal' if partidos_de_grupo else 'disabled')
                if config.BOTONES_PRUEBA_VISIBLES: self.btn_generar_prueba_etapa2.config(state='normal')

                estado_confirmar = 'normal' if todos_jugados and num_equipos > 0 else 'disabled'
                self.btn_confirmar_etapa2.config(state=estado_confirmar)

        # Habilita o deshabilita la pestaña de Fases Eliminatorias.
        self.notebook.tab(2, state='normal' if grupos_estan_bloqueados else 'disabled')

        # --- Lógica para la Pestaña "Fases Eliminatorias" ---
        if hasattr(self, 'btn_volver_etapa3'):
            fases_map = {16: "Octavos", 8: "Cuartos", 4: "Semifinal", 2: "Final"}
            fases_posibles = [f for n, f in fases_map.items() if n <= len(config.ZONAS_DEL_TORNEO) * config.EQUIPOS_CLASIFICAN_POR_ZONA]
            hay_partidos_eliminatorios = any(database.db.obtener_partidos_fase(fase) for fase in fases_posibles)

            self.btn_volver_etapa3.config(state='normal' if grupos_estan_bloqueados else 'disabled')
            self.btn_eliminar_datos_etapa3.config(state='normal' if hay_partidos_eliminatorios and grupos_estan_bloqueados else 'disabled')

        # Lógica para el botón "Eliminar Todos los Datos" (siempre habilitado)
        if hasattr(self, 'btn_eliminar_todo1'):
            self.btn_eliminar_todo1.config(state='normal')
            self.btn_eliminar_todo2.config(state='normal')
            self.btn_eliminar_todo3.config(state='normal')


    def _on_zona_seleccionada(self, event=None):
        """Callback que se ejecuta cuando el usuario selecciona una zona en el Combobox."""
        self._update_ui_state()

    def _on_tree_hover(self, event):
        """Cambia el color de fondo de la fila del Treeview bajo el cursor."""
        tree = event.widget
        item = tree.identify_row(event.y)
        for row in tree.get_children():
            tree.item(row, tags=('' if row != item else 'hover'))

    def crear_widgets_equipos(self):
        """Construye todos los widgets para la pestaña 'Gestionar Equipos'."""
        # --- Frame del Formulario (Altura Fija) ---
        frame_form = ttk.LabelFrame(self.frame_equipos, text="Gestión de Equipos", height=65)
        frame_form.pack(side="top", fill="x", padx=10, pady=10)
        frame_form.pack_propagate(False)

        form_content = ttk.Frame(frame_form)
        form_content.pack(fill="x", expand=True, padx=10, pady=10)
        form_content.columnconfigure(1, weight=1)

        ttk.Label(form_content, text="Nombre:").grid(row=0, column=0, padx=(0, 5))
        self.entry_nombre = ttk.Entry(form_content)
        self.entry_nombre.grid(row=0, column=1, sticky="ew")
        self.entry_nombre.bind("<Return>", lambda event: self.agregar_equipo())
        ttk.Label(form_content, text="Zona:").grid(row=0, column=2, padx=(15, 5))
        self.combo_zona = ttk.Combobox(form_content, values=config.ZONAS_DEL_TORNEO, width=15)
        self.combo_zona.grid(row=0, column=3)
        self.combo_zona.bind("<<ComboboxSelected>>", self._on_zona_seleccionada)
        self.btn_agregar = ttk.Button(form_content, text=" Agregar", image=self.icon_add, compound="left", command=self.agregar_equipo)
        self.btn_agregar.grid(row=0, column=4, padx=(15, 5))
        widgets.Tooltip(self.btn_agregar, "Añadir el equipo a la base de datos.")
        self.btn_modificar = ttk.Button(form_content, text=" Modificar", image=self.icon_edit, compound="left", command=self.modificar_equipo, state='disabled')
        self.btn_modificar.grid(row=0, column=5)

        # --- Frame para Botones Inferiores (Altura Fija) ---
        botonera = widgets.ActionButtonBar(self.frame_equipos)
        self.btn_eliminar_seleccionado = botonera.add_button(text="Eliminar Seleccionado", image=self.icon_delete, compound="left", command=self.eliminar_equipo, state='disabled')
        self.btn_eliminar_datos_etapa1 = botonera.add_button(text="Eliminar Datos de Etapa", image=self.icon_delete_all, compound="left", command=self.eliminar_todos_los_equipos, style='Danger.TButton')
        self.btn_eliminar_todo1 = botonera.add_button(text="Eliminar Todos los Datos", image=self.icon_delete_all, compound="left", command=self.eliminar_todos_los_datos, style='Danger.TButton')
        if config.BOTONES_PRUEBA_VISIBLES:
            self.btn_generar_prueba_etapa1 = botonera.add_button(text="Generar Datos de Prueba", image=self.icon_generate, compound="left", command=self.autogenerar_equipos_prueba, style='Test.TButton')
        self.btn_confirmar_etapa1 = botonera.add_button(text="Confirmar Etapa", image=self.icon_next, compound="right", command=self.confirmar_lista_equipos)

        # --- Frame de la Lista (Altura Flexible) ---
        frame_lista = ttk.LabelFrame(self.frame_equipos, text="Lista de Equipos");
        frame_lista.pack(side="top", fill="both", expand=True, padx=10, pady=(0, 10))

        tree_container = ttk.Frame(frame_lista); tree_container.pack(fill="both", expand=True)
        columns = ("ID", "Nombre", "Zona", "Color")
        self.tree_equipos = ttk.Treeview(tree_container, columns=columns, show="headings")
        self.tree_equipos.tag_configure('hover', background='#E8F0FE')
        scrollbar_equipos = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree_equipos.yview)
        self.tree_equipos.configure(yscrollcommand=scrollbar_equipos.set)
        self.tree_equipos.heading("ID", text="ID"); self.tree_equipos.column("ID", width=50, anchor="center")
        self.tree_equipos.heading("Nombre", text="Nombre")
        self.tree_equipos.heading("Zona", text="Zona"); self.tree_equipos.column("Zona", width=80, anchor="center")
        self.tree_equipos.heading("Color", text="Color"); self.tree_equipos.column("Color", width=100, anchor="center")
        scrollbar_equipos.pack(side="right", fill="y"); self.tree_equipos.pack(side="left", fill="both", expand=True)
        self.tree_equipos.bind("<<TreeviewSelect>>", self.seleccionar_equipo)
        self.tree_equipos.bind("<Motion>", self._on_tree_hover)

        self.actualizar_lista_equipos()

    def confirmar_lista_equipos(self):
        """Acción del botón 'Confirmar Etapa'. Muestra una advertencia y bloquea la edición."""
        if messagebox.askyesno("Confirmar y Bloquear", "Está a punto de bloquear la lista de equipos.\n\nDespués de esto, no podrá agregar, modificar o eliminar equipos.\n¿Desea continuar?"):
            database.db.establecer_config('equipos_bloqueados', '1')
            logger.warning("¡Lista de equipos bloqueada!")
            self.actualizar_todas_las_vistas("Lista de equipos bloqueada. Puede proceder a la Etapa de Grupos.")
            messagebox.showinfo("Lista Bloqueada", "La lista de equipos ha sido bloqueada. Ahora puede proceder a la Etapa de Grupos.")
            self.notebook.select(self.frame_grupos)

    def eliminar_todos_los_datos(self):
        """Acción del botón 'Eliminar Todos los Datos'. Operación destructiva que reinicia el torneo."""
        if messagebox.askyesno("Confirmar Borrado Total", "¡ADVERTENCIA!\n\nEsto borrará permanentemente TODOS los equipos, partidos y configuraciones de la base de datos.\n\n¿Está absolutamente seguro de que desea continuar?"):
            database.db.borrar_todos_los_datos()
            logger.critical("¡TODOS LOS DATOS HAN SIDO BORRADOS POR EL USUARIO!")
            self.actualizar_todas_las_vistas("Todos los datos del torneo han sido eliminados.")
            messagebox.showinfo("Operación Completada", "Todos los datos del torneo han sido eliminados.")
            if self.notebook.index('current') != 0:
                self.notebook.select(self.frame_equipos)

    def crear_widgets_grupos(self):
        """Construye todos los widgets para la pestaña 'Fase de Grupos'."""
        # --- Frame de controles superiores (Altura Fija) ---
        top_frame = ttk.Frame(self.frame_grupos, height=150)
        top_frame.pack(side="top", fill="x", padx=10, pady=10)
        top_frame.pack_propagate(False)

        frame_pendientes = ttk.LabelFrame(top_frame, text="Partidos Pendientes"); frame_pendientes.pack(side="left", fill="both", expand=True, padx=(0, 5))
        control_frame = ttk.Frame(frame_pendientes); control_frame.pack(fill="x", padx=5, pady=5)
        control_frame.columnconfigure(1, weight=1)
        ttk.Label(control_frame, text="Seleccionar Zona:").grid(row=0, column=0, sticky="w")
        self.combo_zona_partidos = ttk.Combobox(control_frame, values=config.ZONAS_DEL_TORNEO); self.combo_zona_partidos.grid(row=0, column=1, sticky="ew", padx=5)
        self.combo_zona_partidos.bind("<<ComboboxSelected>>", self.cargar_partidos_pendientes)
        self.tree_pendientes_container = ttk.Frame(frame_pendientes)
        self.tree_pendientes_container.pack(fill="both", expand=True, pady=5, padx=5)
        self.msg_no_pendientes = ttk.Label(frame_pendientes, text="Todos los partidos de esta zona han sido jugados.", font=("Arial", 10, "italic"), anchor="center")
        self.tree_partidos_pendientes = self._crear_tabla_partidos_pendientes(self.tree_pendientes_container)
        self.tree_partidos_pendientes.bind("<<TreeviewSelect>>", self.seleccionar_partido)
        self.tree_partidos_pendientes.bind("<Motion>", self._on_tree_hover)
        self.tree_partidos_pendientes.tag_configure('hover', background='#E8F0FE')

        frame_registro = ttk.LabelFrame(top_frame, text="Registrar Resultado"); frame_registro.pack(side="right", fill="both", padx=(5, 0), expand=True)
        frame_registro.columnconfigure((0, 2), weight=1); frame_registro.rowconfigure((0, 2, 4), weight=1)
        self.lbl_local = ttk.Label(frame_registro, text="Seleccione un partido", font=("Arial", 10, "bold")); self.lbl_local.grid(row=0, column=0, columnspan=3, pady=(10,0))
        self.entry_goles_local = ttk.Entry(frame_registro, width=5, justify='center', validate='key', validatecommand=self.vcmd)
        self.entry_goles_local.grid(row=1, column=0, sticky='e', padx=(10,0))
        self.entry_goles_local.bind("<Return>", lambda e: self.registrar_partido_grupo())
        ttk.Label(frame_registro, text="vs").grid(row=1, column=1, padx=5)
        self.entry_goles_visitante = ttk.Entry(frame_registro, width=5, justify='center', validate='key', validatecommand=self.vcmd)
        self.entry_goles_visitante.grid(row=1, column=2, sticky='w', padx=(0,10))
        self.entry_goles_visitante.bind("<Return>", lambda e: self.registrar_partido_grupo())
        self.lbl_visitante = ttk.Label(frame_registro, text="", font=("Arial", 10, "bold")); self.lbl_visitante.grid(row=2, column=0, columnspan=3)
        btn_frame = ttk.Frame(frame_registro); btn_frame.grid(row=3, column=0, columnspan=3, pady=(0,10))
        self.btn_guardar_resultado_grupo = ttk.Button(btn_frame, text=" Guardar", image=self.icon_save, compound="left", command=self.registrar_partido_grupo)
        self.btn_guardar_resultado_grupo.pack(side="left", padx=5)
        self.btn_limpiar_formulario = ttk.Button(btn_frame, text=" Limpiar", image=self.icon_clear, compound="left", command=self._limpiar_formulario_partido)
        self.btn_limpiar_formulario.pack(side="left", padx=5)

        # --- Frame de botones inferiores (Altura Fija) ---
        botonera = widgets.ActionButtonBar(self.frame_grupos)
        self.btn_volver_etapa2 = botonera.add_button(text="Volver Etapa", image=self.icon_reset, compound="left", command=self.volver_a_gestion_equipos, style='Danger.TButton')
        self.btn_eliminar_datos_etapa2 = botonera.add_button(text="Eliminar Datos de Etapa", image=self.icon_delete, compound="left", command=self.reiniciar_fase_grupos_gui, style='Danger.TButton')
        self.btn_eliminar_todo2 = botonera.add_button(text="Eliminar Todos los Datos", image=self.icon_delete_all, compound="left", command=self.eliminar_todos_los_datos, style='Danger.TButton')
        if config.BOTONES_PRUEBA_VISIBLES:
            self.btn_generar_prueba_etapa2 = botonera.add_button(text="Generar Datos de Prueba", image=self.icon_generate, compound="left", command=self.autogenerar_resultados_prueba, style='Test.TButton')
        self.btn_confirmar_etapa2 = botonera.add_button(text="Confirmar Etapa", image=self.icon_next, compound="right", command=self.confirmar_fase_grupos)

        # --- Tabla de posiciones (Altura Flexible) ---
        frame_tabla = ttk.LabelFrame(self.frame_grupos, text="Tabla de Posiciones General")
        frame_tabla.pack(side="top", fill="both", expand=True, padx=10, pady=(0, 10))

        tree_pos_container = ttk.Frame(frame_tabla); tree_pos_container.pack(fill="both", expand=True, padx=5, pady=5)
        cols = ("Zona", "Equipo", "PJ", "PG", "PE", "PP", "GF", "GC", "DG", "Puntos")
        self.tree_posiciones = ttk.Treeview(tree_pos_container, columns=cols, show="headings")
        scrollbar_posiciones = ttk.Scrollbar(tree_pos_container, orient="vertical", command=self.tree_posiciones.yview)
        self.tree_posiciones.configure(yscrollcommand=scrollbar_posiciones.set)
        for col in cols:
            self.tree_posiciones.heading(col, text=col, command=lambda c=col: self.ordenar_tabla_posiciones(c, False))
            width = 80 if col not in ["Equipo"] else 150
            self.tree_posiciones.column(col, width=width, anchor="center")
        scrollbar_posiciones.pack(side="right", fill="y"); self.tree_posiciones.pack(side="left", fill="both", expand=True)

        self.actualizar_tablas()

    def ordenar_tabla_posiciones(self, col, reverse):
        """Ordena la tabla de posiciones por la columna clickeada."""
        # Obtiene todos los datos de la tabla.
        data = [(self.tree_posiciones.set(item, col), item) for item in self.tree_posiciones.get_children('')]

        # Intenta ordenar numéricamente, si falla, ordena alfabéticamente.
        try:
            data.sort(key=lambda x: int(x[0]), reverse=reverse)
        except ValueError:
            data.sort(key=lambda x: x[0], reverse=reverse)

        # Mueve las filas en la tabla a su nueva posición ordenada.
        for index, (val, item) in enumerate(data):
            self.tree_posiciones.move(item, '', index)

        # Vuelve a asociar el comando a la cabecera, pero invirtiendo el orden
        # para que el siguiente clic ordene en la dirección opuesta.
        self.tree_posiciones.heading(col, command=lambda: self.ordenar_tabla_posiciones(col, not reverse))
        logger.debug(f"Tabla de posiciones ordenada por '{col}' en orden {'descendente' if reverse else 'ascendente'}.")

    def _crear_tabla_partidos_pendientes(self, parent):
        """Función auxiliar para crear una tabla (Treeview) de partidos."""
        cols = ("Local", "Visitante")
        tree = ttk.Treeview(parent, columns=cols, show="headings", height=3)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.heading("Local", text="Equipo Local"); tree.column("Local", anchor="e")
        tree.heading("Visitante", text="Equipo Visitante"); tree.column("Visitante", anchor="w")
        scrollbar.pack(side="right", fill="y"); tree.pack(side="left", fill="both", expand=True)
        return tree

    def confirmar_fase_grupos(self):
        """Acción del botón 'Confirmar Etapa'. Bloquea la carga de resultados."""
        if messagebox.askyesno("Confirmar y Bloquear", "Está a punto de bloquear la fase de grupos.\n\nDespués de esto, no podrá registrar nuevos resultados.\n¿Desea continuar?"):
            database.db.establecer_config('fase_grupos_bloqueada', '1')
            logger.warning("¡Fase de grupos bloqueada!")
            self.actualizar_todas_las_vistas("Fase de grupos bloqueada. Puede generar las fases eliminatorias.")
            messagebox.showinfo("Fase Bloqueada", "La fase de grupos ha sido bloqueada. Ahora puede generar las fases eliminatorias.")
            self.notebook.select(self.frame_eliminatorias)

    def reiniciar_fase_grupos_gui(self):
        """Acción del botón 'Eliminar Datos de Etapa'. Borra todos los partidos de grupos."""
        if messagebox.askyesno("Eliminar Datos de Etapa", "Esto borrará TODOS los resultados de la fase de grupos.\nLos equipos no serán eliminados.\n\n¿Desea continuar?"):
            database.db.reiniciar_fase_grupos()
            self.actualizar_todas_las_vistas("Resultados de la fase de grupos eliminados.")
            messagebox.showinfo("Resultados Eliminados", "Todos los resultados de la fase de grupos han sido eliminados.")

    def reiniciar_fases_eliminatorias_gui(self):
        """Acción del botón 'Eliminar Datos de Etapa'. Borra todos los partidos de las fases de playoffs."""
        if messagebox.askyesno("Confirmar Reinicio de Eliminatorias", "¡ADVERTENCIA!\n\nEsto borrará TODOS los resultados de las fases eliminatorias (Octavos, Cuartos, etc.).\nLa fase de grupos no se verá afectada.\n\n¿Desea continuar?"):
            database.db.reiniciar_fases_eliminatorias()
            self.actualizar_todas_las_vistas("Fases eliminatorias reiniciadas.")
            messagebox.showinfo("Operación Completada", "Todos los resultados de las fases eliminatorias han sido eliminados.")

    def volver_a_gestion_equipos(self):
        """
        Acción del botón 'Volver Etapa'.
        Reinicia la fase de grupos y desbloquea la lista de equipos.
        """
        msg = ("¡ADVERTENCIA!\n\n"
               "Está a punto de volver a la etapa de gestión de equipos.\n"
               "Esto borrará permanentemente TODOS los resultados de la Fase de Grupos.\n\n"
               "¿Desea continuar?")
        if messagebox.askyesno("Confirmar Retroceso", msg):
            database.db.reiniciar_fase_grupos()
            database.db.desbloquear_equipos()
            logger.warning("Retrocediendo a la etapa de gestión de equipos.")
            self.actualizar_todas_las_vistas("Fase de Grupos reiniciada. Puede volver a gestionar los equipos.")
            messagebox.showinfo("Etapa Reiniciada", "Se han borrado los resultados de la fase de grupos y la lista de equipos ha sido desbloqueada.")
            self.notebook.select(self.frame_equipos)

    def volver_a_fase_grupos(self):
        """
        Acción del botón 'Volver Etapa'.
        Reinicia las eliminatorias y desbloquea la fase de grupos.
        """
        msg = ("¡ADVERTENCIA!\n\n"
               "Está a punto de volver a la Etapa de Grupos.\n"
               "Esto borrará permanentemente TODOS los resultados de las Fases Eliminatorias (Octavos, Cuartos, etc.).\n\n"
               "¿Desea continuar?")
        if messagebox.askyesno("Confirmar Retroceso", msg):
            database.db.reiniciar_fases_eliminatorias()
            database.db.desbloquear_fase_grupos()
            logger.warning("Retrocediendo a la etapa de grupos.")
            self.actualizar_todas_las_vistas("Fases eliminatorias reiniciadas. Puede volver a la Etapa de Grupos.")
            messagebox.showinfo("Etapa Reiniciada", "Se han borrado los resultados de las eliminatorias y la Etapa de Grupos ha sido desbloqueada.")
            self.notebook.select(self.frame_grupos)

    def autogenerar_equipos_prueba(self):
        """Acción del botón 'Generar Datos de Prueba'. Llena el torneo con datos de prueba."""
        if not messagebox.askyesno("Confirmar Autogeneración", "Esto borrará todos los datos existentes y generará equipos de prueba basados en la configuración actual."): return
        logger.info("Iniciando autogeneración de equipos de prueba.")
        database.db.borrar_todos_los_datos()

        equipos_por_zona_requeridos = config.MAX_EQUIPOS_POR_ZONA
        contador_equipo = 1
        for zona in config.ZONAS_DEL_TORNEO:
            for i in range(equipos_por_zona_requeridos):
                nombre_equipo = f"Equipo-{contador_equipo:02d}"
                database.db.agregar_equipo(nombre_equipo, zona)
                contador_equipo += 1

        self.actualizar_todas_las_vistas(f"Se generaron {contador_equipo - 1} equipos de prueba.")
        logger.info("Finalizada la autogeneración de equipos.")
        messagebox.showinfo("Éxito", f"Se han generado {contador_equipo - 1} equipos de prueba.")

    def actualizar_todas_las_vistas(self, mensaje="Listo"):
        """Método central para refrescar toda la información de la GUI."""
        zona_seleccionada_actualmente = self.combo_zona_partidos.get()

        self.actualizar_lista_equipos()

        if config.ZONAS_DEL_TORNEO:
            if zona_seleccionada_actualmente in config.ZONAS_DEL_TORNEO:
                self.combo_zona_partidos.set(zona_seleccionada_actualmente)
            else:
                self.combo_zona_partidos.set(config.ZONAS_DEL_TORNEO[0])

        self.cargar_partidos_pendientes()
        self.actualizar_tablas()
        self._actualizar_vista_eliminatorias()
        self._update_ui_state()
        self._actualizar_barra_estado(mensaje)

    def agregar_equipo(self):
        """Acción del botón 'Agregar'. Valida la entrada y llama a la base de datos."""
        # Obtiene los datos de los widgets, eliminando espacios en blanco del nombre.
        nombre = self.entry_nombre.get().strip()
        zona = self.combo_zona.get()
        # Valida que los campos no estén vacíos.
        if nombre and zona:
            exito = database.db.agregar_equipo(nombre, zona)
            if exito:
                # Si tuvo éxito, actualiza la tabla, limpia el formulario y actualiza el estado.
                self.actualizar_lista_equipos()
                self.entry_nombre.delete(0, tk.END)
                self._update_ui_state()
                self._actualizar_barra_estado(f"Equipo '{nombre}' agregado exitosamente.")
            else:
                # Si falló (equipo duplicado), muestra un error.
                messagebox.showerror("Error de Duplicado", f"El equipo '{nombre}' ya existe. Por favor, elija otro nombre.")
        else:
            # Si los campos estaban vacíos, muestra una advertencia.
            messagebox.showwarning("Campos vacíos", "Debe ingresar un nombre y seleccionar una zona.")

    def seleccionar_equipo(self, event):
        """Callback que se ejecuta al seleccionar una fila en la tabla de equipos."""
        selected_item = self.tree_equipos.selection()
        is_bloqueado = database.db.equipos_bloqueados()

        if selected_item and not is_bloqueado:
            self.btn_modificar.config(state='normal')
            self.btn_eliminar_seleccionado.config(state='normal')
            item_values = self.tree_equipos.item(selected_item, "values")
            self.entry_nombre.delete(0, tk.END)
            self.entry_nombre.insert(0, item_values[1])
            self.combo_zona.set(item_values[2])
        else:
            self.btn_modificar.config(state='disabled')
            self.btn_eliminar_seleccionado.config(state='disabled')

    def modificar_equipo(self):
        """Acción del botón 'Modificar'. Actualiza un equipo existente."""
        selected_item = self.tree_equipos.selection()
        if not selected_item:
            messagebox.showwarning("Sin selección", "Debe seleccionar un equipo para modificar.")
            return
        item = self.tree_equipos.item(selected_item)
        equipo_id = item['values'][0]
        nombre_original = item['values'][1]
        nuevo_nombre = self.entry_nombre.get().strip()
        nueva_zona = self.combo_zona.get()
        if nuevo_nombre and nueva_zona:
            exito = database.db.actualizar_equipo(equipo_id, nuevo_nombre, nueva_zona)
            if exito:
                self.actualizar_lista_equipos()
                self.entry_nombre.delete(0, tk.END)
                self.actualizar_todas_las_vistas(f"Equipo '{nombre_original}' actualizado a '{nuevo_nombre}'.")
            else:
                messagebox.showerror("Error de Duplicado", f"El nombre '{nuevo_nombre}' ya está en uso. Por favor, elija otro nombre.")
        else:
            messagebox.showwarning("Campos vacíos", "Debe ingresar un nuevo nombre y zona.")

    def eliminar_equipo(self):
        """Acción del botón 'Eliminar Seleccionado'."""
        selected_item = self.tree_equipos.selection()
        if not selected_item:
            messagebox.showwarning("Sin selección", "Debe seleccionar un equipo para eliminar.")
            return
        item = self.tree_equipos.item(selected_item)
        equipo_id = item['values'][0]
        nombre_equipo = item['values'][1]
        if messagebox.askyesno("Confirmar", f"¿Está seguro de que desea eliminar al equipo {nombre_equipo}?"):
            database.db.eliminar_equipo(equipo_id)
            self.actualizar_lista_equipos()
            self._update_ui_state()
            self._actualizar_barra_estado(f"Equipo '{nombre_equipo}' eliminado.")

    def eliminar_todos_los_equipos(self):
        """Acción del botón 'Eliminar Datos de Etapa'. Borra todos los equipos y partidos."""
        if messagebox.askyesno("Confirmar Eliminación de Datos de Etapa", "¡ADVERTENCIA!\n\nEsto eliminará permanentemente TODOS los equipos y sus partidos asociados para esta etapa.\n\n¿Está seguro que desea continuar?"):
            database.db.eliminar_todos_los_equipos()
            self.actualizar_todas_las_vistas("Todos los equipos han sido eliminados.")
            messagebox.showinfo("Operación Completada", "Todos los equipos y sus partidos han sido eliminados.")

    def actualizar_lista_equipos(self):
        """Refresca la tabla de equipos con los datos actuales de la base de datos."""
        # Limpia cualquier widget de color que exista.
        for label in self.color_labels:
            label.destroy()
        self.color_labels.clear()
        # Borra todas las filas existentes en la tabla.
        for i in self.tree_equipos.get_children():
            self.tree_equipos.delete(i)
        # Vuelve a insertar una fila por cada equipo de la base de datos.
        for i, (equipo_id, nombre, zona, color) in enumerate(database.db.obtener_equipos()):
            self.tree_equipos.insert("", "end", iid=equipo_id, values=(equipo_id, nombre, zona, ""))
        # `update_idletasks` fuerza a la GUI a redibujarse para que las coordenadas de las celdas estén disponibles.
        self.update_idletasks()
        # Llama a la función que dibuja los cuadros de colores sobre la tabla.
        self._render_color_boxes()
        # Asegurarse de que los botones de modificar/eliminar estén deshabilitados si no hay selección.
        self.seleccionar_equipo(None)

    def _render_color_boxes(self):
        """Dibuja los cuadros de color en la columna 'Color' de la tabla de equipos."""
        # Limpia los cuadros de color anteriores.
        for label in self.color_labels:
            label.destroy()
        self.color_labels.clear()
        # Oculta la columna de color si está deshabilitado en la configuración.
        if not config.ESCUDOS_VISIBLES:
            self.tree_equipos['displaycolumns'] = ("ID", "Nombre", "Zona")
            return
        else:
            self.tree_equipos['displaycolumns'] = ("ID", "Nombre", "Zona", "Color")

        # Itera sobre cada fila visible de la tabla.
        for item_id in self.tree_equipos.get_children():
            try:
                # Obtiene las coordenadas y tamaño de la celda de la columna "Color".
                bbox = self.tree_equipos.bbox(item_id, column="Color")
                if not bbox: continue
                x, y, width, height = bbox
                # Busca los datos del equipo correspondiente a esta fila.
                equipo = next((e for e in database.db.obtener_equipos() if e[0] == int(item_id)), None)
                if equipo:
                    color = equipo[3]
                    # Crea una nueva etiqueta (Label) con el color de fondo del equipo.
                    color_label = tk.Label(self.tree_equipos, background=color, relief="raised", borderwidth=1)
                    # `place` posiciona la etiqueta exactamente sobre la celda, creando la ilusión de una celda coloreada.
                    color_label.place(x=x, y=y, width=width, height=height)
                    self.color_labels.append(color_label)
            except Exception:
                # Ignora errores que puedan ocurrir si la ventana se está redibujando.
                pass

    def autogenerar_resultados_prueba(self):
        """Acción del botón 'Generar Datos de Prueba'. Registra resultados aleatorios."""
        if not messagebox.askyesno("Confirmar Autogeneración", "Esto generará resultados aleatorios para TODOS los partidos de grupo pendientes.\n¿Desea continuar?"): return
        logger.info("Iniciando autogeneración de resultados de prueba.")
        todos_pendientes = []
        for zona in config.ZONAS_DEL_TORNEO:
            todos_pendientes.extend(logic.generar_fixture_zona(zona))
        if not todos_pendientes:
            messagebox.showinfo("Información", "No hay partidos de grupo pendientes para generar.")
            return
        equipos_map = {nombre: id for id, nombre, zona, color in database.db.obtener_equipos()}
        for local_nombre, visitante_nombre in todos_pendientes:
            goles_local, goles_visitante = random.randint(0, 5), random.randint(0, 5)
            local_id, visitante_id = equipos_map.get(local_nombre), equipos_map.get(visitante_nombre)
            if local_id and visitante_id: database.db.registrar_partido("Grupo", local_id, visitante_id, goles_local, goles_visitante)
        logger.info("Finalizada la autogeneración de resultados.")
        messagebox.showinfo("Éxito", f"Se han generado y registrado los resultados de {len(todos_pendientes)} partidos.")
        self.actualizar_todas_las_vistas(f"Generados {len(todos_pendientes)} resultados de prueba.")

    def cargar_partidos_pendientes(self, event=None):
        """Carga la lista de partidos pendientes para la zona seleccionada."""
        zona = self.combo_zona_partidos.get()
        # Limpia la tabla.
        for i in self.tree_partidos_pendientes.get_children():
            self.tree_partidos_pendientes.delete(i)
        # Pide a la capa de lógica el fixture.
        pendientes = logic.generar_fixture_zona(zona) if zona else []
        # Rellena la tabla.
        for p in pendientes:
            self.tree_partidos_pendientes.insert("", "end", values=p)
        # Muestra un mensaje si no hay partidos pendientes.
        if not pendientes and zona:
            self.tree_pendientes_container.pack_forget()
            self.msg_no_pendientes.pack(fill="both", expand=True)
        else:
            self.msg_no_pendientes.pack_forget()
            self.tree_pendientes_container.pack(fill="both", expand=True, pady=5, padx=5)
        self._update_ui_state()

    def seleccionar_partido(self, event):
        """Callback al seleccionar un partido de la lista de pendientes."""
        selected_item = self.tree_partidos_pendientes.selection()
        if not selected_item: return
        local, visitante = self.tree_partidos_pendientes.item(selected_item)['values']
        # Almacena el partido seleccionado y actualiza el formulario de registro.
        self.partido_seleccionado = (local, visitante)
        self.lbl_local.config(text=local)
        self.lbl_visitante.config(text=visitante)

    def registrar_partido_grupo(self):
        """Acción del botón 'Guardar' resultado de un partido de grupo."""
        if not self.partido_seleccionado:
            messagebox.showerror("Error", "Debe seleccionar un partido de la lista.")
            return
        goles_local_str, goles_visitante_str = self.entry_goles_local.get(), self.entry_goles_visitante.get()
        if not goles_local_str or not goles_visitante_str:
            messagebox.showerror("Error", "Debe ingresar los goles para ambos equipos.")
            return
        try:
            goles_local, goles_visitante = int(goles_local_str), int(goles_visitante_str)
        except ValueError:
            # Este error ahora es menos probable gracias a la validación proactiva,
            # pero se mantiene como una segunda capa de seguridad.
            messagebox.showerror("Error", "Los goles deben ser números enteros.")
            return
        local_nombre, visitante_nombre = self.partido_seleccionado
        equipos_map = {e[1]: e[0] for e in database.db.obtener_equipos()}
        local_id, visitante_id = equipos_map.get(local_nombre), equipos_map.get(visitante_nombre)
        database.db.registrar_partido("Grupo", local_id, visitante_id, goles_local, goles_visitante)
        self._limpiar_formulario_partido()
        self.actualizar_todas_las_vistas(f"Resultado guardado: {local_nombre} {goles_local} - {goles_visitante} {visitante_nombre}.")

        # Auto-seleccionar el siguiente partido pendiente si existe
        items = self.tree_partidos_pendientes.get_children()
        if items:
            primer_partido_pendiente = items[0]
            self.tree_partidos_pendientes.selection_set(primer_partido_pendiente)
            self.tree_partidos_pendientes.focus(primer_partido_pendiente)
            self.seleccionar_partido(None) # Dispara el evento para rellenar el formulario

    def _limpiar_formulario_partido(self, event=None):
        """Limpia y resetea el formulario de registro de resultados."""
        self.partido_seleccionado = None
        self.lbl_local.config(text="Seleccione un partido")
        self.lbl_visitante.config(text="")
        self.entry_goles_local.delete(0, tk.END)
        self.entry_goles_visitante.delete(0, tk.END)
        if hasattr(self, 'tree_partidos_pendientes') and self.tree_partidos_pendientes.winfo_exists():
            if self.tree_partidos_pendientes.selection():
                self.tree_partidos_pendientes.selection_remove(self.tree_partidos_pendientes.selection())
        return "break"

    def actualizar_tablas(self):
        """Refresca la tabla de posiciones con los datos actuales."""
        if hasattr(self, 'tree_posiciones') and self.tree_posiciones.winfo_exists():
            for i in self.tree_posiciones.get_children():
                self.tree_posiciones.delete(i)
            for zona in config.ZONAS_DEL_TORNEO:
                tabla = database.db.calcular_tabla_posiciones(zona)
                for equipo in tabla:
                    self.tree_posiciones.insert("", "end", values=(zona,) + tuple(equipo.values()))
            self.ordenar_tabla_posiciones("Puntos", True)

    def crear_widgets_eliminatorias(self):
        """Construye la estructura base para la pestaña de 'Fases Eliminatorias'."""
        # Frame de botones inferiores (Altura Fija)
        botonera = widgets.ActionButtonBar(self.frame_eliminatorias)
        self.btn_volver_etapa3 = botonera.add_button(text="Volver Etapa", image=self.icon_reset, compound="left", command=self.volver_a_fase_grupos, style='Danger.TButton')
        self.btn_eliminar_datos_etapa3 = botonera.add_button(text="Eliminar Datos de Etapa", image=self.icon_delete, compound="left", command=self.reiniciar_fases_eliminatorias_gui, style='Danger.TButton')
        self.btn_eliminar_todo3 = botonera.add_button(text="Eliminar Todos los Datos", image=self.icon_delete_all, compound="left", command=self.eliminar_todos_los_datos, style='Danger.TButton')

        # El área de scroll (Canvas) ahora se empaqueta en la parte superior,
        # ocupando todo el espacio restante.
        canvas_container = ttk.Frame(self.frame_eliminatorias)
        canvas_container.pack(side="top", fill="both", expand=True, padx=10, pady=(10, 0))

        canvas = tk.Canvas(canvas_container)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)

        self.scrollable_frame = ttk.Frame(canvas)
        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.bind("<Configure>", _on_canvas_configure)
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.fases_container = self.scrollable_frame

    def _actualizar_vista_eliminatorias(self):
        """
        Renderiza dinámicamente el cuadro de eliminatorias.
        Borra todo el contenido anterior y lo reconstruye basado en el estado
        actual del torneo, mostrando fases jugadas, la fase activa o el campeón.
        """
        # Limpia el contenedor.
        for widget in self.fases_container.winfo_children():
            widget.destroy()

        # Carga los datos de los equipos para tener acceso a sus colores.
        self.equipos_data = {nombre: {'id': id, 'zona': zona, 'color': color} for id, nombre, zona, color in database.db.obtener_equipos()}

        # Lógica para determinar el orden y nombre de las fases.
        total_clasificados = len(config.ZONAS_DEL_TORNEO) * config.EQUIPOS_CLASIFICAN_POR_ZONA
        fases_map = {16: "Octavos", 8: "Cuartos", 4: "Semifinal", 2: "Final"}

        fases_ordenadas = []
        num_equipos = total_clasificados
        while num_equipos >= 2:
            if num_equipos in fases_map:
                fases_ordenadas.append(fases_map[num_equipos])
            num_equipos //= 2

        # Si la final ya se jugó, muestra al campeón.
        partidos_final = database.db.obtener_partidos_fase("Final")
        if partidos_final and len(partidos_final) >= 1:
             self._mostrar_campeon()

        fase_activa_encontrada = False
        # Itera a través de las fases en orden (Octavos, Cuartos...).
        for i, fase in enumerate(fases_ordenadas):
            partidos_jugados = database.db.obtener_partidos_fase(fase)
            if partidos_jugados:
                # Si la fase ya tiene partidos, la muestra como "jugada" y colapsada.
                frame_fase = widgets.CollapsibleFrame(self.fases_container, text=f"{fase} de Final - Jugado", expanded=False)
                frame_fase.pack(fill="x", padx=10, pady=5, expand=True)
                ttk.Separator(self.fases_container, orient='horizontal').pack(fill='x', padx=10, pady=5)
                for j, (_, local, visitante, goles_l, goles_v) in enumerate(partidos_jugados):
                    local_data = {'nombre': local, 'escudo': self._get_escudo(local)}
                    visitante_data = {'nombre': visitante, 'escudo': self._get_escudo(visitante)}
                    widgets.MatchRowWidget(frame_fase.container, local_data, visitante_data, resultado=(goles_l, goles_v)).pack(fill='x')
                    if j < len(partidos_jugados) - 1:
                        ttk.Separator(frame_fase.container, orient='horizontal').pack(fill='x', pady=8, padx=10)

            else:
                # Si encuentra una fase sin partidos, esa es la fase activa.
                fase_anterior = fases_ordenadas[i-1] if i > 0 else "Grupo"
                if database.db.fase_grupos_bloqueada():
                    self._generar_y_mostrar_fase(fase, fase_anterior)
                    fase_activa_encontrada = True
                break # Detiene el bucle, no muestra fases futuras.

        # Si no se encontró ninguna fase activa (porque no se ha generado la primera), muestra el botón para generarla.
        nombre_fase_inicial = fases_ordenadas[0] if fases_ordenadas else ""
        if not fase_activa_encontrada and not database.db.obtener_partidos_fase(nombre_fase_inicial) and database.db.fase_grupos_bloqueada():
             self.btn_generar_octavos = ttk.Button(self.fases_container, text=f" Generar {nombre_fase_inicial} de Final", image=self.icon_generate, compound="left", command=self._generar_y_mostrar_fase_inicial)
             self.btn_generar_octavos.pack(pady=10, padx=10)

    def _get_escudo(self, nombre_equipo):
        """Obtiene una imagen de escudo para un equipo, usando un caché."""
        if config.ESCUDOS_VISIBLES:
            if nombre_equipo not in self.escudos_coloreados_cache:
                color = self.equipos_data.get(nombre_equipo, {}).get('color', '#888888')
                self.escudos_coloreados_cache[nombre_equipo] = fa.icon_to_image("shield-alt", fill=color, scale_to_height=14)
            return self.escudos_coloreados_cache[nombre_equipo]
        return None

    def _generar_y_mostrar_fase_inicial(self):
        """Acción del botón 'Generar Octavos'. Simplemente refresca la vista."""
        self._actualizar_vista_eliminatorias()

    def _generar_y_mostrar_fase(self, fase, fase_anterior):
        """Genera y muestra los widgets para la fase eliminatoria activa."""
        enfrentamientos = []
        if fase_anterior == 'Grupo':
            enfrentamientos = logic.generar_enfrentamientos_iniciales()
            if enfrentamientos is None:
                messagebox.showerror("Error de Clasificación", "No se pudieron generar los enfrentamientos. Verifique que todas las zonas tengan suficientes equipos y resultados.")
                return
        else:
            enfrentamientos = logic.generar_enfrentamientos(fase_anterior)

        frame_fase = widgets.CollapsibleFrame(self.fases_container, text=f"{fase} de Final")
        frame_fase.pack(fill="x", padx=10, pady=5, expand=True)
        ttk.Separator(self.fases_container, orient='horizontal').pack(fill='x', padx=10, pady=5)

        if not enfrentamientos:
            return

        self.match_row_widgets_por_fase[fase] = []
        for i, (local, visitante) in enumerate(enfrentamientos):
            local_data = {'nombre': local, 'escudo': self._get_escudo(local)}
            visitante_data = {'nombre': visitante, 'escudo': self._get_escudo(visitante)}
            match_row = widgets.MatchRowWidget(frame_fase.container, local_data, visitante_data, vcmd=self.vcmd, editable=True)
            match_row.pack(fill='x')
            self.match_row_widgets_por_fase[fase].append((local, visitante, match_row))

            if i < len(enfrentamientos) - 1:
                ttk.Separator(frame_fase.container, orient='horizontal').pack(fill='x', pady=8, padx=10)

        ttk.Button(frame_fase.container, text=f" Registrar Todos los Partidos de {fase}", image=self.icon_confirm, compound="left", command=lambda f=fase: self.registrar_fase_completa(f)).pack(pady=10)

    def _mostrar_campeon(self):
        """Muestra una sección especial con el nombre del campeón del torneo."""
        ganador_final = logic.obtener_ganadores("Final")
        if ganador_final:
            frame_campeon = widgets.CollapsibleFrame(self.fases_container, text="Campeón del Torneo")
            frame_campeon.pack(pady=10, padx=10, fill="x")
            ttk.Separator(self.fases_container, orient='horizontal').pack(fill='x', padx=10, pady=5)
            inner_frame = ttk.Frame(frame_campeon.container, style='Champion.TFrame')
            inner_frame.pack(fill='x', expand=True, padx=10, pady=5)
            lbl_campeon = ttk.Label(inner_frame, text=f" {ganador_final[0]}", image=self.icon_medal, compound="left", font=("Arial", 16, "bold"), foreground="royalblue", background='#f0f0f0')
            lbl_campeon.pack(pady=15)
            self._actualizar_barra_estado(f"¡El campeón del torneo es {ganador_final[0]}!")

    def registrar_fase_completa(self, fase):
        """
        Acción del botón 'Registrar Todos'. Valida y guarda todos los resultados
        de una fase eliminatoria de una sola vez.
        """
        partidos_info = self.match_row_widgets_por_fase.get(fase, [])
        resultados_validados = []
        # Itera sobre cada partido y sus widgets de entrada.
        for i, (local, visitante, match_row) in enumerate(partidos_info):
            entry_local, entry_visitante = match_row.get_result_entries()
            try:
                # Intenta convertir los valores a enteros.
                goles_local, goles_visitante = int(entry_local.get()), int(entry_visitante.get())
                # Valida que los goles no sean negativos.
                if goles_local < 0 or goles_visitante < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error de Validación", f"Resultado inválido en el partido {i+1} ({local} vs {visitante}).\nPor favor, ingrese solo números enteros no negativos.")
                return # Detiene la ejecución si hay un error.

            # Valida que no haya empates en fases eliminatorias.
            if goles_local == goles_visitante:
                messagebox.showerror("Error de Validación", f"Hay un empate en el partido {local} vs {visitante}.\nNo se permiten empates en fases eliminatorias.")
                return # Detiene la ejecución.

            # Si todas las validaciones pasan, añade el resultado a una lista temporal.
            resultados_validados.append((fase, local, visitante, goles_local, goles_visitante))

        # Solo si TODOS los resultados son válidos, procede a guardarlos.
        equipos_map = {nombre: id for id, nombre, zona, color in database.db.obtener_equipos()}
        for fase_db, local_db, visitante_db, gl_db, gv_db in resultados_validados:
            local_id, visitante_id = equipos_map.get(local_db), equipos_map.get(visitante_db)
            database.db.registrar_partido(fase_db, local_id, visitante_id, gl_db, gv_db)

        messagebox.showinfo("Éxito", f"Se han registrado todos los partidos de {fase}.")
        logger.warning(f"¡Fase '{fase}' completada y registrada!")
        # Actualiza toda la vista para mostrar la siguiente fase y re-evaluar los estados de los botones.
        self.actualizar_todas_las_vistas(f"Resultados de {fase} de Final registrados.")