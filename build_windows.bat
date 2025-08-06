@echo off
REM Script para construir el instalador de Windows

setlocal enabledelayedexpansion

:: Verificar si Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python no está instalado o no está en el PATH.
    echo Por favor, instala Python 3.8 o superior desde https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Verificar si pip está instalado
pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: pip no está instalado.
    echo Por favor, asegúrate de que pip esté correctamente instalado.
    pause
    exit /b 1
)

echo Instalando dependencias...
pip install cx_Freeze PyQt6

if %ERRORLEVEL% NEQ 0 (
    echo Error al instalar las dependencias.
    pause
    exit /b 1
)

echo Creando entorno virtual...
python -m venv venv

if %ERRORLEVEL% NEQ 0 (
    echo Error al crear el entorno virtual.
    pause
    exit /b 1
)

:: Activar el entorno virtual y continuar con la instalación
call venv\Scripts\activate

if %ERRORLEVEL% NEQ 0 (
    echo Error al activar el entorno virtual.
    pause
    exit /b 1
)

echo Instalando dependencias en el entorno virtual...
pip install cx_Freeze PyQt6

if %ERRORLEVEL% NEQ 0 (
    echo Error al instalar las dependencias en el entorno virtual.
    pause
    exit /b 1
)

echo Construyendo el ejecutable...
python setup.py build

if %ERRORLEVEL% NEQ 0 (
    echo Error al construir el ejecutable.
    pause
    exit /b 1
)

echo ¡Compilación completada con éxito!
echo El ejecutable se encuentra en la carpeta "build".

pause
