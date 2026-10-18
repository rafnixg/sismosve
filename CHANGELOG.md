# Historial de cambios

Las versiones siguen [Semantic Versioning](https://semver.org/). Una entrada
«Sin publicar» describe código preparado para la próxima release; los tags y
las imágenes versionadas solo se consideran aprobados cuando el workflow de
release completa sus controles de seguridad.

## [0.3.1] - 2026-10-18

- Se centraliza la versión de la aplicación en `VERSION` y se sincronizan los
  manifiestos npm, las etiquetas Docker y la documentación.
- OpenAPI y `/api/health` exponen la misma versión del código.
- CI detecta versiones desactualizadas y el release rechaza un tag que no
  coincida con `VERSION`, antes de construir o publicar imágenes.
- Se corrigen las referencias históricas a versiones `1.0.0` y `2.0.0` que no
  correspondían a releases del proyecto.
- Runtime Python 3.14 sobre Alpine 3.24, sin pip, ensurepip ni curl; el
  healthcheck usa Python y comprueba que el estado sea `healthy`.

## [0.3.0] - 2026-10-18

- UI en Svelte 5 con mapa, filtros, listado y estadísticas sincronizados.
- Mejoras en las páginas de privacidad y términos y en el resumen de sismos.
- CTA a la encuesta oficial de FUNVISIS y conservación del SEO en el HTML.
- Persistencia del JSON en `/app/data/sismosve.json` entre despliegues.
- Construcción Docker exclusiva para tags de versión, con análisis en AMD64
  y ARM64 antes de promover `latest` y crear la release de GitHub.
- Actualización de dependencias y coordinación de los toolchains de Vite y Node.

## [0.2.0] - 2025-09-26

- Organización del backend FastAPI en configuración, routers y servicios.

## Versiones anteriores

El historial anterior se conserva en los [tags del repositorio](https://github.com/rafnixg/sismosve/tags).
Los primeros tags `v.0.1.0` y `v.0.1.1` usaron un punto adicional; los nuevos
tags siguen el formato `vMAJOR.MINOR.PATCH`.

[0.3.1]: https://github.com/rafnixg/sismosve/tree/v0.3.1
[0.3.0]: https://github.com/rafnixg/sismosve/tree/v0.3.0
[0.2.0]: https://github.com/rafnixg/sismosve/tree/v0.2.0
