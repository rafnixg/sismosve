# GitHub Actions de SismosVE

Las imágenes Docker se construyen **exclusivamente al hacer push de un tag de versión**. Los PR y los pushes a ramas ejecutan validaciones sin construir ni publicar imágenes.

| Evento | Pruebas y auditorías | Construcción Docker | Release |
|---|---|---|---|
| PR hacia `main` | Sí | No | No |
| Push a `main` o `develop` | Sí | No | No |
| Push de `vX.Y.Z` | Sí, antes del build | amd64 y arm64 | Después del análisis |
| Push de `vX.Y.Z-rc.1` u otra preversión | Sí, antes del build | amd64 y arm64 | Prerelease |
| Tag fuera de `v*` | No | No | No |
| Tag `v*` inválido | Falla la validación | No | No |
| Mantenimiento semanal o manual | Dependencias, imagen publicada y salud | No | No |

## Flujo de release

`release.yml` es la única entrada de publicación y solo escucha `push.tags: ['v*']`.

1. `release_metadata.py` valida SemVer con prefijo `v`, normaliza el nombre del repositorio para GHCR y detecta cualquier preversión.
2. Se reutiliza `ci.yml`: actionlint, zizmor, pruebas de la política de publicación, auditorías de dependencias, Svelte y pruebas de API, SEO y almacenamiento.
3. `docker-build.yml`, disponible solo como workflow reutilizable y con una segunda condición de tag, construye `linux/amd64` y `linux/arm64`. Publica los tags exactos `vX.Y.Z` y `X.Y.Z`, con SBOM y procedencia de BuildKit. `pull: true` actualiza las imágenes base.
4. `container-scan.yml` analiza el **digest recién publicado** en ambas arquitecturas. Guarda JSON, SARIF y SBOM como artefactos durante 30 días y envía los resultados a Code Scanning. Incluye vulnerabilidades sin parche.
5. Cualquier hallazgo HIGH o CRITICAL bloquea la promoción a `latest` y la creación de la release. Un informe ausente o inválido también falla. Los tags de versión ya publicados permanecen disponibles para investigar; su existencia por sí sola no demuestra que hayan superado el análisis.
6. Si todo pasa, una versión estable actualiza `latest` mediante el mismo manifiesto, sin reconstruir. Una preversión nunca cambia `latest`.
7. Se crea la release de GitHub con el digest verificado, notas automáticas y los archivos de despliegue. El workflow no modifica el código ni los tags.

`latest` corresponde a la última publicación estable que terminó correctamente, no necesariamente al mayor número SemVer si se publican versiones antiguas fuera de orden. Conviene publicar las versiones estables en orden y configurar reglas de repositorio que protejan `v*` contra modificaciones y borrados.

Los formatos históricos `v.0.1.0` y `v.0.1.1` se conservan en Git; las nuevas publicaciones requieren `v0.1.0`, sin el punto adicional. No se admite metadato `+build`, incompatible con los nombres de tags Docker.

Ejemplo para una próxima versión **después del merge**:

```bash
git switch main
git pull --ff-only
git tag v0.2.1
git push origin v0.2.1
```

El workflow de Docker no tiene `workflow_dispatch`. El mantenimiento manual solo inspecciona la imagen que ya está publicada.

## CI y permisos

El frontend se compila una sola vez y se comparte con Python 3.11, 3.12, 3.13 y 3.14. Python 3.9 y 3.10 [ya terminaron su soporte](https://devguide.python.org/versions/); las actualizaciones actuales de Uvicorn y python-multipart requieren al menos 3.10. La versión mínima soportada por este proyecto es 3.11 y la imagen de producción usa 3.14. El artefacto incluye `.vite/manifest.json`, necesario para las pruebas de integración. También se comprueban cambios en `requirements.txt`; ya no se excluyen todos los `.txt`.

Los workflows parten de `contents: read`; cada job solicita únicamente las escrituras que necesita: GHCR para publicar, `security-events` para SARIF y `contents` para crear la release. Los PR no reciben permisos de publicación ni secretos de despliegue. Todos los Actions externos están fijados por SHA completo y checkout usa `persist-credentials: false`.

Se mantiene la sintaxis local `./.github/workflows/...` para compatibilidad con actionlint 1.7.12. Cuatro comentarios `zizmor: ignore[self-repository]` documentan esa única excepción de estilo; no desactivan las comprobaciones de permisos, inyección o fijación de SHA.

## Mantenimiento y alertas

El domingo a las 02:00 UTC, o manualmente, `maintenance.yml`:

- Audita los requisitos Python reales con pip-audit y el lockfile npm, conservando ambos informes y los códigos de error.
- Resuelve `latest` a un digest y reutiliza el análisis de ambas arquitecturas sin generar imágenes.
- Prueba la salud del contenedor publicado, comprueba `status == healthy` y elimina siempre el contenedor de prueba.

Se retiraron las issues semanales basadas en el tamaño del JSON y la eliminación automática de versiones de GHCR. Un JSON no vacío no demuestra vulnerabilidades y borrar versiones por antigüedad puede destruir releases o manifiestos de varias arquitecturas.

Dependabot contempla Python, npm en `/frontend`, Docker y Actions. **La configuración YAML de actualizaciones no activa Dependabot alerts ni security updates:** esas opciones deben habilitarse en Settings → Advanced Security del repositorio. El estado observado y las limitaciones del análisis están en [el informe de seguridad](security_best_practices_report.md).

Vite, su plugin de Svelte y Vitest se actualizan en un mismo grupo para respetar sus dependencias entre sí. TypeScript 7 se aplaza mientras `svelte-check` solo acepte las ramas 5 y 6. Se conserva Node 22 LTS en CI y en el builder Docker; Node 26 se reconsiderará cuando entre en LTS según el [calendario oficial de Node.js](https://nodejs.org/en/about/previous-releases). Estas excepciones afectan únicamente a esas versiones y deben retirarse cuando se cumplan las condiciones de compatibilidad. Se mantienen las actualizaciones de parches y las auditorías de seguridad.

Las alertas históricas del antiguo análisis `docker-build.yml:security-scan` pueden seguir visibles al cambiar de configuración. Después de un análisis nuevo en la rama por defecto, comparar los resultados por digest y retirar la configuración antigua desde Code Scanning si corresponde; no descartar alertas en bloque como falsos positivos.

## Verificación local

```bash
python -m pip install PyYAML==6.0.3 zizmor==1.31.1
python .github/scripts/check_workflows.py
go install github.com/rhysd/actionlint/cmd/actionlint@v1.7.12
actionlint
zizmor --offline --no-config --strict-collection .github/workflows

cd frontend
npm ci
npm audit --audit-level=high
npm run check
npm test
npm run build
cd ..
TESTING=true python -m pytest test_app.py test_ui.py test_storage.py -q
```

La validación de publicación es estática y prueba los helpers con casos válidos, inválidos y hallazgos simulados. La construcción, el acceso a GHCR y la creación real de una release solo pueden verificarse en GitHub al publicar un tag; un PR no realiza esas operaciones.
