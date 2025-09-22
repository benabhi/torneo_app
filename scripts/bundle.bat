@echo off
setlocal enabledelayedexpansion

REM -----------------------------------------------------
REM Determina carpetas: scripts (donde corre el .bat) y raiz del proyecto (una carpeta arriba)
REM -----------------------------------------------------
for %%I in ("%~dp0..") do set "PROJECT_ROOT=%%~fI"
set "SCRIPTS_DIR=%~dp0"

REM Nombre y ruta del archivo de salida (dentro de scripts)
set "OUTPUT_FILE=%SCRIPTS_DIR%codigo_unificado.txt"

REM Elimina el archivo de salida si ya existe (para empezar limpio)
if exist "%OUTPUT_FILE%" del /f /q "%OUTPUT_FILE%"

REM --- Funcion auxiliar: agrega un archivo al output con encabezado ---
REM Llamar con: call :append_file "ruta_completa_origen" "etiqueta_de_encabezado"
goto start

:append_file
REM %~1 = ruta de origen, %~2 = texto de encabezado
if exist "%~1" (
    >> "%OUTPUT_FILE%" echo %~2
    >> "%OUTPUT_FILE%" echo.
    type "%~1" >> "%OUTPUT_FILE%"
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
REM --- Archivo: main.py (ahora una carpeta arriba) ---
call :append_file "%PROJECT_ROOT%\main.py" "main.py"

REM --- Archivo: lib\gui.py (ahora una carpeta arriba) ---
call :append_file "%PROJECT_ROOT%\lib\gui.py" "lib\gui.py"

REM --- Archivo: lib\logic.py ---
call :append_file "%PROJECT_ROOT%\lib\logic.py" "lib\logic.py"

REM --- Archivo: lib\config.py ---
call :append_file "%PROJECT_ROOT%\lib\config.py" "lib\config.py"

REM --- Archivo: lib\database.py ---
call :append_file "%PROJECT_ROOT%\lib\database.py" "lib\database.py"

REM --- Archivo: lib\widgets.py ---
call :append_file "%PROJECT_ROOT%\lib\widgets.py" "lib\widgets.py"

REM --- Archivo: lib\logger.py ---
call :append_file "%PROJECT_ROOT%\lib\logger.py" "lib\logger.py"

echo Proceso completado. El archivo generado es: "%OUTPUT_FILE%"
pause
endlocal
