# JSON persistente en Dokploy

El volumen de Dokploy ya está creado. Debe estar montado en **`/app/data`**.
La imagen configura `DATA_FILE=/app/data/sismosve.json`; API, health check,
scheduler y `updater.py` usan esa misma ruta. Los respaldos quedan junto al
archivo: `/app/data/sismosve.json.backup_*` (se conservan los cinco últimos).

Dokploy documenta los montajes de volúmenes persistentes en
[Advanced → Volumes/Mounts](https://docs.dokploy.com/docs/core/applications/advanced).
Comprueba el montaje existente; no hace falta crear otro. El nombre usado en
los ejemplos es `sismove-data`; sustituirlo si el volumen real tiene otro nombre.
No montar el volumen sobre `/app`, porque allí está el código de cada versión.

## Comportamiento al arrancar

- Si existe un JSON válido, se conserva byte por byte y se programa la próxima
  consulta a FUNVISIS para cinco minutos después. No se descarga encima del
  respaldo al iniciar. El botón de actualización manual sigue disponible.
- Solo cuando falta el JSON se copia la muestra incluida en la imagen. No es
  un mecanismo de recuperación de datos de producción: restaura antes tu respaldo.
- Un JSON existente ilegible/corrupto o un volumen sin escritura hacen fallar
  el inicio con un error explícito. No se usa silenciosamente otra ruta.
- Las actualizaciones escriben un archivo temporal en el mismo volumen y
  reemplazan el JSON solo después de completar la escritura. Un fallo conserva
  el archivo anterior. El actualizador independiente también valida la descarga.

El proceso corre como `sismosve`, con **UID/GID `10001:10001`** estables. Un
volumen ya existente puede necesitar el ajuste de permisos que se muestra abajo.
El contenedor no arranca como root ni cambia permisos sobre el código.

## Migración del archivo anterior al volumen existente

Ejecutar en el host Linux de Dokploy. Tener disponible la imagen **con este
cambio**, antes de iniciar la nueva versión. Ajustar estas tres variables:

```bash
APP="nombre-del-contenedor-actual"
IMAGE="imagen-con-este-cambio:etiqueta"
VOLUME="sismove-data"
BACKUP="$PWD/sismosve-pre-migracion-$(date -u +%Y%m%dT%H%M%SZ).json"
```

Verificar el volumen y detener la versión anterior antes de copiar el JSON para
evitar escrituras concurrentes durante la copia. Esto implica una pausa del
servicio hasta desplegar la nueva versión.

```bash
docker volume inspect "$VOLUME"
docker inspect "$APP" --format '{{json .Mounts}}'
docker stop "$APP"
docker cp "$APP:/app/sismosve.json" "$BACKUP"
```

Conservar esa copia fuera del volumen. Cargarla únicamente si todavía no hay
un JSON en el volumen y asignar permisos al usuario de la imagen nueva:

```bash
docker volume inspect "$VOLUME" >/dev/null && \
docker run --rm --user 0 --entrypoint sh \
  --mount "type=volume,source=$VOLUME,target=/app/data" \
  --mount "type=bind,source=$BACKUP,target=/tmp/restore.json,readonly" \
  "$IMAGE" -ec '
    python -c "from pathlib import Path; from app.storage import initialize_data_file; initialize_data_file(Path(\"/app/data/sismosve.json\"), Path(\"/tmp/restore.json\"))"
    chown -R 10001:10001 /app/data
    chmod 750 /app/data
    chmod 640 /app/data/sismosve.json
  '
```

La inicialización conserva un JSON válido que ya exista en el volumen; no lo
reemplaza con la copia de `/tmp/restore.json`. Si el JSON existente es inválido,
se detiene sin tocarlo para permitir una recuperación explícita desde respaldo.

En Dokploy, verificar que el montaje existente apunte a `/app/data` y desplegar
la imagen nueva. La variable `DATA_FILE` no necesita configurarse otra vez si
se conserva el valor de la imagen; eliminar cualquier override hacia la ruta vieja.
Después actualizar `APP` al nombre del nuevo contenedor y comprobar:

```bash
docker inspect "$APP" --format '{{json .Mounts}}'
docker exec "$APP" python -c 'from app.config import sismos_service; print(sismos_service.data_file)'
docker exec "$APP" sh -c 'id; ls -ld /app/data; ls -l /app/data/sismosve.json; test -w /app/data && test -w /app/data/sismosve.json'
docker exec "$APP" python -c 'import json,urllib.request; print(json.load(urllib.request.urlopen("http://localhost:8000/api/health")))'
```

La ruta efectiva debe ser `/app/data/sismosve.json`. Comparar el hash del JSON
antes y después del despliegue, antes de que transcurran los cinco minutos de
la siguiente actualización, permite verificar su conservación.

## Uso local

Sin Docker, el valor por defecto es `<repositorio>/data/sismosve.json`, sin
depender del directorio desde el que se ejecuta Python. `DATA_FILE` permite
seleccionar otra ruta. La inicialización de FastAPI aplica las mismas garantías.

El Compose principal monta `sismove-data` por defecto; `SISMOSVE_DATA_VOLUME`
permite reutilizar otro nombre existente. El contenedor de revisión usa un
volumen separado, `sismosve-review-data`, montado también en `/app/data`.
Detener o recrear los contenedores conserva los volúmenes. No usar `down -v`
si se quieren conservar los datos.
