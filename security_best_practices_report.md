# Revisión de seguridad de GitHub Actions y contenedores

> Actualización del 18 de octubre de 2026: el [diagnóstico y la corrección para
> 0.3.1](docs/RELEASE_0.3.1.md) documentan el fallo real de `v0.3.0` y la
> validación de la imagen corregida. El informe siguiente conserva la evidencia
> histórica del análisis inicial.

Fecha: 17 de octubre de 2026. Base revisada: `5e12e25d942815accebcf2a7eed523ec42efa386` (`main`, después del PR #21).

## Resumen ejecutivo

El análisis de seguridad estaba roto: la imagen se publicaba, pero el job de Trivy fallaba antes de ejecutarse. Las 89 alertas abiertas de GitHub proceden de diciembre de 2025. Un análisis nuevo de la imagen publicada detectó **304 hallazgos de paquete: 52 altos, 96 medios, 153 bajos y 3 sin severidad; ninguno crítico**. Son detecciones del escáner, no una demostración de explotación de la aplicación.

Este PR corrige el flujo de publicación y sus controles, fija Actions por SHA, actualiza Vitest para eliminar avisos críticos de las herramientas de pruebas y añade auditorías reproducibles. **No resuelve las vulnerabilidades de la imagen base ni afirma que el contenedor esté libre de vulnerabilidades. El control nuevo bloquearía la promoción de la imagen analizada.**

## Alcance y evidencias

Se consultaron mediante la API autenticada de GitHub las alertas abiertas de Code Scanning, Dependabot y Secret Scanning, las configuraciones de seguridad, las últimas ejecuciones y los logs del job fallido. Se revisaron los seis workflows y la configuración de Dependabot. El proyecto utiliza Python/FastAPI y TypeScript/Svelte; esta revisión se limita a Actions, dependencias y contenedores, sin constituir una auditoría completa de endpoints o del despliegue Dokploy. La skill `security-best-practices` no incluye una referencia específica de Actions; para esa parte se utilizó la documentación oficial de GitHub y los proveedores.

| Fuente | Resultado observado |
|---|---|
| Code Scanning, alertas abiertas | 89, todas de Trivy 0.65.0; 38 identificadores de vulnerabilidad distintos |
| Severidades de esas alertas | 10 medias, 78 bajas y 1 sin severidad definida; ninguna alta o crítica |
| Último análisis publicado | `2025-12-29T06:13:42Z`, `main@d14489af30ca7d67a94616f4464483d1c3eb9480` |
| Dependabot alerts | HTTP 403 con mensaje explícito de que están deshabilitadas |
| Dependabot security updates | Deshabilitadas en la configuración devuelta por GitHub |
| Secret Scanning | Sin alertas abiertas devueltas; escaneo y protección de push habilitados |
| Imagen pública inspeccionada | `ghcr.io/rafnixg/sismosve@sha256:2728f22b7653999790604e83447e5aa60c586dfe9412b6a8ac4f76d146d99191` |
| Escáner utilizado ahora | Trivy v0.76.0, base de vulnerabilidades descargada el 17 de octubre de 2026 |

La ausencia de alertas abiertas de secretos no garantiza ausencia de secretos en todo el historial. Dependabot no puede evaluarse como «sin vulnerabilidades» mientras sus alertas estén deshabilitadas.

## Hallazgos críticos

### 1. Dependencias vulnerables en las herramientas de pruebas — corregido

**Impacto:** el lockfile anterior incluía dependencias de Vitest con avisos de ejecución de código condicionados a contaminación de prototipos y opciones de workers controlables; no se ha demostrado esa cadena de explotación en este proyecto.

Evidencia: `frontend/package.json:23` y `frontend/package-lock.json` de la base revisada. `npm audit` devolvió tres entradas de paquete: dos críticas y una moderada, correspondientes a `vitest`, `tinypool` y `@vitest/mocker`. Las entradas transitivas no representan tres explotaciones independientes.

Se actualizó Vitest de la rama 3 a `^4.1.11` (resuelto a 4.1.12), compatible con Vite 7 y Node 22, sin overrides de dependencias. La auditoría del lockfile actualizado devuelve **cero vulnerabilidades**, y pasan los seis tests y el build. El problema afecta a herramientas de desarrollo/pruebas; no se ha identificado tinypool como parte del bundle servido al navegador. Referencias: [aviso de tinypool](https://github.com/advisories/GHSA-85c8-ppgw-ccpr), [aviso de Vitest](https://github.com/advisories/GHSA-82fw-gwwq-j7x9).

## Hallazgos altos

### 2. Referencia de Trivy retirada y controles que no se ejecutaban — corregido; exposición histórica no confirmada

Evidencia: `.github/workflows/docker-build.yml:107` en la base revisada. El [job 117531031015](https://github.com/rafnixg/sismosve/actions/runs/39078226488/job/117531031015) falla en `Set up job` con `Unable to resolve action aquasecurity/trivy-action@0.33.1`. La construcción y publicación anterior sí terminó correctamente.

El proveedor retiró las referencias antiguas sin prefijo `v` tras el incidente de marzo de 2026. El [aviso oficial GHSA-69fq-xp46-6x23](https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23) describe el secuestro de tags de Actions y las versiones afectadas. Se sustituyó por `aquasecurity/trivy-action` v0.36.0 fijado a `ed142fd0673e97e23eac54620cfb913e5ce36c25`, con Trivy v0.76.0 explícito. La revisión del composite confirma que su dependencia `setup-trivy` también está fijada por SHA.

El intento de octubre no ejecutó el Action. La consulta de ejecuciones del workflow durante el 19–20 de marzo devolvió cero resultados; la disponibilidad de historial y logs limita lo que puede concluirse. No hay evidencia suficiente para afirmar un compromiso histórico. Si se encuentra una ejecución dentro de la ventana afectada, seguir la rotación de credenciales y la investigación que indica el proveedor.

### 3. La imagen publicada contiene hallazgos altos — pendiente de remediación de la imagen

El análisis nuevo, tanto de la imagen pública por el digest indicado como de la imagen local de revisión, produjo la misma distribución:

| Componente | Altos | Medios | Bajos | Sin severidad |
|---|---:|---:|---:|---:|
| Debian 13.7 | 48 | 94 | 153 | 3 |
| Paquetes Python | 4 | 2 | 0 | 0 |
| Paquetes Node identificados | 0 | 0 | 0 | 0 |

Los 52 hallazgos altos corresponden a **14 identificadores distintos**. Un mismo CVE puede afectar a varios paquetes binarios de una misma fuente. Los 48 altos de Debian no indican versión corregida en la base consultada. Por ejemplo, Debian registra [CVE-2026-76642](https://security-tracker.debian.org/tracker/CVE-2026-76642) como vulnerable en trixie y con corrección en otras ramas; no es correcto asumir que un simple `apt upgrade` en trixie lo resolverá.

| Identificadores altos de Debian | Familia | Detecciones |
|---|---|---:|
| CVE-2026-76642, CVE-2026-78408, CVE-2026-78409, CVE-2026-78410 | util-linux y bibliotecas derivadas | 36 |
| CVE-2026-12064, CVE-2026-8458 | curl y libcurl | 4 |
| CVE-2026-54369 | libacl | 1 |
| CVE-2025-69720 | ncurses y libtinfo | 4 |
| CVE-2026-16742 | libsystemd y libudev | 2 |
| CVE-2026-9538 | perl-base | 1 |

Cuatro detecciones altas indican correcciones disponibles en dependencias incluidas dentro de pip:

| Paquete detectado | Versión | Corrección indicada |
|---|---|---|
| msgpack | 1.1.2 | 1.2.1 |
| setuptools | 70.3.0 | 78.1.1 |
| urllib3, dos avisos | 2.7.0 | 2.8.0 |

Identificadores Python: GHSA-6v7p-g79w-8964, CVE-2025-47273, CVE-2026-97687 y CVE-2026-97689.

Se contrastó el entorno del contenedor: la aplicación importa urllib3 2.8.0 desde su virtualenv, mientras `pip/_vendor/vendor.txt` conserva urllib3 2.7.0, msgpack 1.1.2 y setuptools 70.3.0. Por eso `pip-audit -r requirements.txt` puede pasar y el contenedor seguir teniendo hallazgos. Actualizar únicamente `requirements.txt` no elimina las copias incluidas en pip. Referencia de ejemplo: [aviso de msgpack](https://github.com/advisories/GHSA-6v7p-g79w-8964).

Evidencia de composición: `Dockerfile:27` usa una imagen Python slim para runtime y `Dockerfile:39` instala curl; el virtualenv se copia al runtime en `Dockerfile:47`. Recomendaciones para un PR posterior: evaluar retirar pip del runtime después de instalar dependencias, sustituir el healthcheck de curl por la biblioteca estándar de Python y comparar una base mantenida con menos paquetes. Cualquier cambio requiere construir y probar ambas arquitecturas, el usuario sin privilegios y el volumen de datos. Las detecciones relativas a montajes, herramientas locales o pip no prueban exposición remota de FastAPI; se necesita evaluar las precondiciones antes de emitir VEX o aceptar excepciones.

No se añadieron exclusiones de CVE ni se descartaron alertas. El nuevo control conserva también las vulnerabilidades sin parche y bloquea HIGH/CRITICAL. **Con el estado analizado, una próxima release quedaría bloqueada hasta remediar o revisar explícitamente estos hallazgos.** Solo se analizó amd64 en local; los nuevos jobs cubren además arm64.

### 4. Análisis de una imagen distinta y publicación sin esperar a seguridad — corregido

Evidencia original: `.github/workflows/docker-build.yml:85` y `:109` analizan `latest`, aunque otro run pudiera haber cambiado ese tag; `release.yml:3` inicia la release en paralelo al workflow Docker. El SBOM y los resultados podían referirse a otra imagen, y una release podía anunciar una imagen inexistente o no verificada.

Ahora release espera pruebas → construcción → análisis por digest de las dos arquitecturas. Solo después se promueve ese manifiesto a `latest` y se crea la release. Los informes se suben antes de aplicar el bloqueo, conservando evidencia incluso cuando hay vulnerabilidades. Los tags de versión se publican antes del análisis; no deben desplegarse automáticamente por su mera existencia.

### 5. Actions mutables y credenciales disponibles más tiempo del necesario — corregido

Evidencia original: todos los workflows usaban referencias como `actions/checkout@v4`, `docker/build-push-action@v6` y `actions/github-script@v8`; checkout conservaba sus credenciales por defecto. No demuestra un ataque, pero permite que una referencia modificada cambie el código ejecutado con los permisos del job.

Todos los Actions externos quedan fijados por SHA completo, verificado contra su repositorio de origen. Se usa `persist-credentials: false` y permisos de lectura por defecto, con escrituras limitadas a cada job. Dependabot seguirá proponiendo actualizaciones de Actions. Fundamento: [guía oficial de uso seguro de Actions](https://docs.github.com/en/actions/reference/security/secure-use).

## Hallazgos medios

### 6. Versiones de release interpoladas directamente en shell — corregido

Evidencia original: `.github/workflows/release.yml:41`, `:106` y `:114` insertaban expresiones de la versión en scripts, heredocs y comandos. La capacidad de crear un tag ya requiere permisos de escritura, lo que reduce la exposición, pero no sustituye validar datos antes de ejecutar shell con permisos de publicación.

Se valida un formato restringido de SemVer antes de cualquier escritura, se pasan valores por variables de entorno y se citan los argumentos de shell. Se eliminó el job que intentaba editar documentación, alterar la versión de Compose y hacer push desde un tag.

### 7. Mantenimiento podía borrar releases y ocultar fallos — corregido

Evidencia original: `.github/workflows/maintenance.yml:131` y `:151` borraban versiones de GHCR más allá de diez, preservando solo las etiquetadas `latest`. Esto podía eliminar versiones de release y manifiestos necesarios. En `:38` y `:52`, `|| true` ocultaba fallos de las herramientas; el tamaño del JSON se interpretaba como prueba de vulnerabilidades. El job auditaba herramientas instaladas, sin instalar los requisitos de la aplicación, y creaba issues sin declarar `issues: write`.

Se retiraron el borrado y las issues automáticas; las auditorías de requisitos y lockfile mantienen sus códigos de error y suben informes. El mantenimiento no publica paquetes ni necesita permisos de escritura sobre código o issues. El healthcheck comprueba la respuesta JSON y limpia el contenedor incluso si falla.

### 8. Dependencias fuera de la cobertura de CI y Dependabot — corregido parcialmente

Evidencia original: `.github/workflows/ci.yml:8` y `:16` excluían todos los `.txt`, incluido `requirements.txt`; `.github/dependabot.yml` no incluía npm. Se retiró esa exclusión, se agregó `/frontend` y se incorporaron pip-audit y npm audit. Los nuevos requisitos resueltos con Python 3.13 no muestran vulnerabilidades conocidas en pip-audit; esto no representa el inventario completo de una imagen ni todas las versiones permitidas por los rangos abiertos.

**Pendiente en Settings → Advanced Security:** habilitar Dependabot alerts y Dependabot security updates. Añadir `dependabot.yml` no activa esos ajustes y este PR no modifica la configuración remota del repositorio.

## Validación y límites de entrega

Pasan localmente las nueve pruebas de política de workflows y helpers, actionlint 1.7.12, la auditoría offline de zizmor 1.31.1, Svelte check, seis tests de frontend, el build y 21 tests de API/SEO/almacenamiento. La auditoría npm actualizada y pip-audit de los requisitos no devuelven vulnerabilidades conocidas. Se probaron con datos reales las conversiones de Trivy a SARIF y SPDX y el código de salida de bloqueo del informe con vulnerabilidades.

Zizmor mantiene cuatro excepciones explícitas y puntuales para usar la sintaxis local `./.github/workflows/`, válida en GitHub y compatible con actionlint 1.7.12. No hay exclusiones de permisos, inyección, referencias SHA o CVE. El análisis offline no consulta vulnerabilidades nuevas de Actions remotos.

No se construyó ni publicó una imagen nueva para este PR ni se creó un tag de prueba. El envío de SARIF, los permisos efectivos de GHCR, la construcción multi-arquitectura y la creación de la release deberán verificarse con el próximo tag. La configuración antigua de Code Scanning puede conservar sus 89 alertas hasta comparar un análisis nuevo en la rama por defecto y retirar la configuración obsoleta, si procede.

Para reproducir el análisis publicado con Trivy v0.76.0 (el contenido de la base de vulnerabilidades puede cambiar):

```bash
trivy image --image-src remote --scanners vuln --list-all-pkgs --format json \
  --output trivy.json \
  ghcr.io/rafnixg/sismosve@sha256:2728f22b7653999790604e83447e5aa60c586dfe9412b6a8ac4f76d146d99191
python .github/scripts/check_vulnerabilities.py trivy.json
```
