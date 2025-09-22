@echo off
setlocal enabledelayedexpansion

REM -----------------------------------------------------
REM Determina carpetas: scripts (donde corre el .bat) y raiz del proyecto (una carpeta arriba)
REM -----------------------------------------------------
for %%I in ("%~dp0..") do set "PROJECT_ROOT=%%~fI"
set "SCRIPTS_DIR=%~dp0"

REM Nombre y ruta del archivo de salida
set "OUTPUT_FILE=%SCRIPTS_DIR%codigo_unificado_con_lineas.txt"

REM Elimina el archivo de salida si ya existe
if exist "%OUTPUT_FILE%" del /f /q "%OUTPUT_FILE%"

REM --- Funcion auxiliar: agrega un archivo con numeracion de linea precisa ---
goto start

:append_file
REM %~1 = ruta de origen, %~2 = texto de encabezado
if exist "%~1" (
    >> "%OUTPUT_FILE%" echo %~2
    >> "%OUTPUT_FILE%" echo.

    set "line_num=1"
    set "first_line_processed=false"

    for /f "usebackq delims=" %%L in ("%~1") do (
        set "line=%%L"

        REM Manejo especial para la primera linea para ignorarla si esta vacia
        if !first_line_processed!==false (
            set "first_line_processed=true"
            REM Si la primera linea esta vacia, no la imprimimos y el contador no avanza para la proxima.
            if "!line!" NEQ "" (
                >> "%OUTPUT_FILE%" echo !line_num!:!line!
                set /a line_num+=1
            )
        ) else (
            >> "%OUTPUT_FILE%" echo !line_num!:!line!
            set /a line_num+=1
        )
    )

    >> "%OUTPUT_FILE%" echo.
    >> "%OUTPUT_FILE%" echo.
) else (
    >> "%OUTPUT_FILE%" echo %~2
    >> "%OUTPUT_FILE%" echo.
    >> "%OUTPUT_FILE%" echo [ADVERTENCIA] Archivo no encontrado: %~1
    >> "%OUTPUT_FILE%" echo.
    >> "%OUTPUT_FILE%" echo.
)
goto :eof

:start
REM --- Llama a la funcion para cada archivo ---
call :append_file "%PROJECT_ROOT%\main.py" "main.py"
call :append_file "%PROJECT_ROOT%\lib\gui.py" "lib\gui.py"
call :append_file "%PROJECT_ROOT%\lib\logic.py" "lib\logic.py"
call :append_file "%PROJECT_ROOT%\lib\config.py" "lib\config.py"
call :append_file "%PROJECT_ROOT%\lib\database.py" "lib\database.py"
call :append_file "%PROJECT_ROOT%\lib\widgets.py" "lib\widgets.py"
call :append_file "%PROJECT_ROOT%\lib\logger.py" "lib\logger.py"

echo Proceso completado. El archivo generado es: "%OUTPUT_FILE%"
pause
endlocal