@echo off
REM Script de Docker para SismosVE en Windows
REM Facilita la construcción y ejecución del contenedor

setlocal enabledelayedexpansion

:main
if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="build" goto build
if "%1"=="run" goto run
if "%1"=="prod" goto prod
if "%1"=="stop" goto stop
if "%1"=="clean" goto clean
if "%1"=="logs" goto logs
if "%1"=="shell" goto shell
if "%1"=="health" goto health
if "%1"=="rebuild" goto rebuild
goto help

:help
echo.
echo 🐳 Scripts de Docker para SismosVE
echo =================================
echo.
echo Uso: %0 [comando]
echo.
echo Comandos disponibles:
echo   build     - Construir la imagen Docker
echo   run       - Ejecutar contenedor en modo desarrollo
echo   prod      - Ejecutar con docker-compose (producción)
echo   stop      - Detener todos los contenedores
echo   clean     - Limpiar imágenes y contenedores
echo   logs      - Ver logs del contenedor
echo   shell     - Acceder al shell del contenedor
echo   health    - Verificar estado de salud
echo   rebuild   - Reconstruir imagen desde cero
echo.
goto end

:build
echo 🔨 Construyendo imagen Docker...
docker build -t sismosve:latest .
if !errorlevel! equ 0 (
    echo ✅ Imagen construida exitosamente
) else (
    echo ❌ Error construyendo imagen
)
goto end

:run
echo 🚀 Ejecutando SismosVE en modo desarrollo...
call :build
docker run -d --name sismosve-dev -p 8000:8000 -v "sismove-data:/app/data" -v "%cd%\logs:/app/logs" --restart unless-stopped sismosve:latest
if !errorlevel! equ 0 (
    echo ✅ Contenedor iniciado
    echo 🌐 Aplicación disponible en: http://localhost:8000
    echo 📚 API Docs en: http://localhost:8000/docs
) else (
    echo ❌ Error iniciando contenedor
)
goto end

:prod
echo 🚀 Ejecutando SismosVE en modo producción...
call :build
docker-compose up -d
if !errorlevel! equ 0 (
    echo ✅ Servicios iniciados con docker-compose
    echo 🌐 Aplicación disponible en: http://localhost:8000
) else (
    echo ❌ Error iniciando servicios
)
goto end

:stop
echo 🛑 Deteniendo contenedores...
docker stop sismosve-dev 2>nul
docker-compose down 2>nul
echo ✅ Contenedores detenidos
goto end

:clean
echo 🧹 Limpiando Docker...
call :stop
docker rm sismosve-dev 2>nul
docker rmi sismosve:latest 2>nul
docker system prune -f
echo ✅ Limpieza completada
goto end

:logs
echo 📋 Mostrando logs...
docker ps --format "{{.Names}}" | findstr sismosve-dev >nul
if !errorlevel! equ 0 (
    docker logs -f sismosve-dev
) else (
    docker-compose ps | findstr sismosve >nul
    if !errorlevel! equ 0 (
        docker-compose logs -f sismosve
    ) else (
        echo ❌ No hay contenedores de SismosVE ejecutándose
    )
)
goto end

:shell
echo 🐚 Accediendo al shell del contenedor...
docker ps --format "{{.Names}}" | findstr sismosve-dev >nul
if !errorlevel! equ 0 (
    docker exec -it sismosve-dev /bin/bash
) else (
    docker-compose ps | findstr sismosve >nul
    if !errorlevel! equ 0 (
        docker-compose exec sismosve /bin/bash
    ) else (
        echo ❌ No hay contenedores de SismosVE ejecutándose
    )
)
goto end

:health
echo 🏥 Verificando estado de salud...
curl -f http://localhost:8000/api/health >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Aplicación saludable
) else (
    echo ❌ Aplicación no responde
)
goto end

:rebuild
echo 🔄 Reconstruyendo imagen desde cero...
call :stop
docker rmi sismosve:latest 2>nul
docker build --no-cache -t sismosve:latest .
if !errorlevel! equ 0 (
    echo ✅ Imagen reconstruida exitosamente
) else (
    echo ❌ Error reconstruyendo imagen
)
goto end

:end
endlocal