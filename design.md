# SismosVE — sistema visual

## Dirección
Interfaz cartográfica clara para consultar actividad sísmica en Venezuela.
Género modern-minimal; estructura Workbench: encabezado compacto, reporte a
FUNVISIS, filtros, resumen y mapa con lista lateral. Sin decoración animada.
En móvil el mapa precede a la lista. Las páginas legales conservan su contenido.

## Tokens y tipografía
`tokens.css` es la fuente de colores, espacios, tamaños y radios del frontend.
Source Sans 3 local, pesos 400, 600 y 700; números tabulares para magnitudes.
Superficie blanca, fondo azul grisáceo, texto azul oscuro y acciones azules.
Verde, ámbar y rojo indican magnitud, nunca intensidad ni nivel de peligro.
El texto y la leyenda acompañan al color.

## Interacción
Foco visible, controles con etiquetas, errores recuperables, estados vacíos,
selección compartida entre lista y mapa. Sin notificaciones de éxito invasivas.
Respetar movimiento reducido. El CTA «Reportar a FUNVISIS» siempre está
disponible y avisa de que abre otra pestaña.

## HTML y SEO
Jinja mantiene documento, metadatos, H1, descripción, CTA y enlaces rastreables.
Svelte controla la herramienta interactiva. Canonical y sitemap comparten
`PUBLIC_URL`; no se generan URLs indexables para combinaciones de filtros.
