@echo off
title SismosVE - Instalar Dependencias
color 0B

echo.
echo ========================================
echo  SismosVE - Instalacion de Dependencias
echo ========================================
echo.

:: Verificar si Python esta instalado
"C:\Program Files\Miniconda\python.exe" --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no encontrado en Miniconda
    echo Verificar instalacion de Python
    pause
    exit /b 1
)

:: Instalar dependencias
echo Instalando dependencias de FastAPI...
"C:\Program Files\Miniconda\python.exe" -m pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo ✓ Dependencias instaladas correctamente
    echo Ya puedes ejecutar start_server.bat
) else (
    echo.
    echo ✗ Error al instalar dependencias
    echo Verificar conexion a internet y permisos
)

echo.
pause