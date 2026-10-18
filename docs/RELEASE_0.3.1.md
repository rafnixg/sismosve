# Corrección de la publicación 0.3.1

## Fallo de v0.3.0

El [run 39151713755](https://github.com/rafnixg/sismosve/actions/runs/39151713755)
construyó y publicó los tags Docker de `v0.3.0`. Las pruebas pasaron y ambos
análisis de Trivy se ejecutaron, generaron informes y enviaron SARIF a GitHub.
El paso que falló fue el control de vulnerabilidades, con estos resultados
en **cada** arquitectura:

| Severidad | Hallazgos de paquete |
|---|---:|
| CRITICAL | 0 |
| HIGH | 52 |
| MEDIUM | 96 |
| LOW | 153 |
| UNKNOWN | 3 |

Digest analizado: `sha256:5c0ea8aedf19f15f2b5d980dec404a60502c9034855d6e6506a492c144aeed69`.
Los 48 HIGH del sistema correspondían a paquetes Debian; los otros 4, a
dependencias incluidas en pip. Los hallazgos no equivalen a 52 vulnerabilidades
distintas ni demuestran explotación de FastAPI. `latest` y la release de GitHub
quedaron bloqueados. Reejecutar el mismo código no corrige esas detecciones.

Los logs están disponibles para [AMD64](https://github.com/rafnixg/sismosve/actions/runs/39151713755/job/117747553183)
y [ARM64](https://github.com/rafnixg/sismosve/actions/runs/39151713755/job/117747553182).

## Cambios

- `VERSION` define `0.3.1`. La API lo lee directamente para OpenAPI y health.
  `project_version.py --set` sincroniza los manifiestos npm, el valor por defecto
  de Docker, README y llms.txt. `--check` detecta diferencias y exige changelog.
- El release compara el tag con el código antes de generar outputs. El build
  comprueba también que `APP_VERSION` coincida con el archivo. Las etiquetas
  Docker locales y de GHCR usan el mismo número; Compose hereda esas etiquetas.
- La base de builder y runtime pasa a `python:3.14-alpine3.24`, una
  [variante oficial de Python](https://github.com/docker-library/official-images/blob/master/library/python).
  El runtime aplica las actualizaciones de Alpine. No se copian compiladores.
- Se instalan únicamente wheels compatibles con cada arquitectura y musl.
  Si una dependencia futura deja de ofrecerlos, el build falla y requiere revisión.
  La compilación del frontend se ejecuta en la arquitectura del builder; su
  salida estática sirve para ambas arquitecturas.
- Se retiran pip, sus dependencias incluidas y ensurepip del runtime. La instalación
  de paquetes ocurre durante el build, no en contenedores desplegados.
- Se elimina curl y el healthcheck usa la biblioteca estándar de Python,
  comprobando `status == healthy`. Los logs dejan de usar permisos globales `777`.
- Se mantienen UID/GID `10001:10001`, `/app/data`, `DATA_FILE`, el volumen de
  Dokploy y el JSON existente. No se introducen exclusiones de vulnerabilidades
  ni cambios en el umbral de seguridad.

Alpine utiliza musl en lugar de glibc. Por ello se comprobaron los wheels y el
arranque en ambas arquitecturas, además de la API, el volumen y HTTPS. Estos
resultados cubren la configuración probada; no sustituyen la validación del
despliegue real en Dokploy.

## Validación local del 18 de octubre de 2026

- 12 pruebas de workflows y versionado, incluyendo metadatos desactualizados y
  rechazo de un tag diferente sin escribir outputs.
- actionlint 1.7.12 y zizmor 1.31.1, sin nuevas excepciones de seguridad.
- `npm ci`, auditoría sin vulnerabilidades conocidas, Svelte sin errores ni
  advertencias, 6 pruebas y compilación de producción.
- 24 pruebas Python de API, SEO, almacenamiento y healthcheck.
- Builds Linux AMD64 y ARM64; ejecución ARM64 mediante emulación local.
- Pruebas HTTP de health, OpenAPI, sismos, páginas legales, llms.txt, sitemap,
  canonical y CTA. Verificación de UID, permisos del volumen, persistencia al
  recrear el contenedor, ausencia de instaladores y conexión HTTPS con certificados.
- Trivy 0.76.0 sobre ambas imágenes finales y ejecución del mismo
  `check_vulnerabilities.py` usado por CI: **0 CRITICAL, 0 HIGH, 0 MEDIUM,
  0 LOW y 0 UNKNOWN en cada arquitectura**, con la base consultada ese día.

Los informes completos se conservan localmente en
`.local/trivy-version-amd64.json` y `.local/trivy-version-arm64.json`; los logs
de construcción están en `.local/docker-version-*.log`. El workflow del próximo
tag volverá a construir y analizar los digests publicados con una base nueva;
el resultado local no garantiza que una base futura arroje los mismos datos.

`v0.3.0` permanece intacto. La corrección requiere merge y un nuevo tag
`v0.3.1` desde el commit que incluya estos cambios. El PR no publica imágenes.
