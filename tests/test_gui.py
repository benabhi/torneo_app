"""
Suite de Tests para el Módulo de Interfaz Gráfica (`gui.py`)

Este archivo contiene tests para la lógica de la clase `App`.
A diferencia de los otros tests, probar una GUI presenta desafíos únicos.
La estrategia aquí no es probar la apariencia visual (si un botón es azul),
sino verificar que la lógica que se ejecuta tras una interacción del usuario
(un clic, por ejemplo) funciona como se espera.

Para lograr esto, se utiliza una técnica llamada "Mocking" (simulación),
donde se reemplazan componentes externos (como la base de datos o las
ventanas emergentes) por "dobles" falsos que podemos controlar y espiar.
"""

import pytest
import tkinter as tk

# Se importa el módulo `database` para poder acceder a la variable `db` (que será parcheada).
import lib.database
# Se importa la clase `App` que se va a probar.
from lib.gui import App


@pytest.fixture
def app(mocker):
    """
    Crea y configura un entorno de GUI limpio y funcional para cada test.

    Este fixture es crucial para probar la GUI sin que aparezcan ventanas.
    1. Desactiva el logging.
    2. Reemplaza (`parchea`) la base de datos real con un Mock (un objeto falso).
    3. Crea una instancia real de la clase `App`.
    4. Oculta la ventana de la App para que los tests se ejecuten en segundo plano.
    5. Entrega la instancia de la App al test.
    6. Destruye la ventana de la App al finalizar el test para liberar memoria.
    """
    # Parchea la configuración para que los logs no aparezcan en la consola.
    mocker.patch('lib.config.LOGGING_ACTIVADO', False)

    # Crea un objeto Mock para simular la base de datos.
    mock_db = mocker.MagicMock()
    # Pre-configura el mock para que devuelva valores por defecto y no cause
    # errores durante la inicialización de la App.
    mock_db.obtener_equipos.return_value = []
    mock_db.equipos_bloqueados.return_value = False
    mock_db.fase_grupos_bloqueada.return_value = False

    # Reemplaza la instancia 'db' real en el módulo 'database' por nuestro mock.
    # Cualquier llamada a `database.db` desde la GUI será interceptada por este mock.
    mocker.patch('lib.database.db', mock_db)

    # Crea la instancia de la aplicación.
    app_instance = App()
    # Oculta la ventana principal.
    app_instance.withdraw()

    # Entrega la instancia de la App al test.
    yield app_instance

    # Limpieza: destruye la ventana de la App después de que el test se complete.
    app_instance.destroy()


# --- Suite de Tests para la Lógica de la GUI ---

def test_agregar_equipo_exitoso(app, mocker):
    """
    Verifica la lógica del método `agregar_equipo` en el caso de éxito.
    El test simula que el usuario ha introducido datos válidos.
    """
    # 1. Arrange (Preparar)
    # Simula que el usuario escribe "Equipo Test" en el campo de nombre.
    mocker.patch.object(app.entry_nombre, 'get', return_value="Equipo Test")
    # Simula que el usuario selecciona "A" en el desplegable de zona.
    mocker.patch.object(app.combo_zona, 'get', return_value="A")

    # Configura el mock de la base de datos para que simule una inserción exitosa.
    lib.database.db.agregar_equipo.return_value = True
    # Simula las funciones de la GUI que se llamarían tras el éxito para evitar errores.
    mocker.patch.object(app, 'actualizar_lista_equipos')
    mocker.patch.object(app.entry_nombre, 'delete')
    mocker.patch.object(app, '_update_ui_state')
    # Simula la ventana emergente de error para verificar que NO se llama.
    mock_showerror = mocker.patch('tkinter.messagebox.showerror')

    # 2. Act (Actuar): Llama directamente al método que se quiere probar.
    app.agregar_equipo()

    # 3. Assert (Verificar): Comprueba que todo ocurrió como se esperaba.
    # Verifica que el método de la base de datos fue llamado una vez con los datos correctos.
    lib.database.db.agregar_equipo.assert_called_once_with("Equipo Test", "A")
    # Verifica que los métodos de actualización de la GUI fueron llamados.
    app.actualizar_lista_equipos.assert_called_once()
    app.entry_nombre.delete.assert_called_once_with(0, tk.END)
    app._update_ui_state.assert_called_once()
    # Verifica que la ventana de error NO apareció.
    mock_showerror.assert_not_called()

def test_agregar_equipo_duplicado(app, mocker):
    """
    Verifica la lógica de `agregar_equipo` cuando la base de datos indica
    que el equipo ya existe (duplicado).
    """
    # Arrange: Simula la entrada del usuario y la respuesta de fallo de la DB.
    mocker.patch.object(app.entry_nombre, 'get', return_value="Equipo Repetido")
    mocker.patch.object(app.combo_zona, 'get', return_value="B")
    lib.database.db.agregar_equipo.return_value = False
    mock_showerror = mocker.patch('tkinter.messagebox.showerror')

    # Act: Llama al método.
    app.agregar_equipo()

    # Assert:
    # Verifica que se intentó agregar el equipo.
    lib.database.db.agregar_equipo.assert_called_once_with("Equipo Repetido", "B")
    # Verifica que se mostró una ventana de error al usuario.
    mock_showerror.assert_called_once()

def test_agregar_equipo_campos_vacios(app, mocker):
    """
    Verifica la lógica de `agregar_equipo` cuando el usuario no ha rellenado
    los campos obligatorios.
    """
    # Arrange: Simula que los campos devuelven cadenas vacías.
    mocker.patch.object(app.entry_nombre, 'get', return_value="   ") # Se prueba con espacios para verificar el .strip()
    mocker.patch.object(app.combo_zona, 'get', return_value="")
    mock_showwarning = mocker.patch('tkinter.messagebox.showwarning')

    # Act: Llama al método.
    app.agregar_equipo()

    # Assert:
    # Verifica que NUNCA se intentó llamar a la base de datos.
    lib.database.db.agregar_equipo.assert_not_called()
    # Verifica que se mostró la advertencia correcta al usuario.
    mock_showwarning.assert_called_once_with("Campos vacíos", "Debe ingresar un nombre y seleccionar una zona.")