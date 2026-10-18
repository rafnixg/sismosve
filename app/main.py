# Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
# SPDX-License-Identifier: AGPL-3.0-only
# Additional author-attribution term under section 7(b): see repository-root NOTICE.
"""
Aplicación principal FastAPI para sismos de Venezuela - Modular
"""

import json
import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# from jinja2 import UndefinedError

from .config import lifespan, PUBLIC_URL
from .routers import sismos, admin, seo, legal
from .version import __version__
# from .exceptions import not_found_handler, jinja_undefined_handler, internal_error_handler


# Crear aplicación FastAPI
app = FastAPI(
    title="SismosVE API",
    description=(
        "API para datos de sismos de Venezuela desde FUNVISIS.\n\n"
        "SismosVE - desarrollado originalmente por Rafnix Guzman (@rafnixg). "
        "Copyright © 2025–2026. Software sin garantía; puedes modificarlo y "
        "redistribuirlo bajo [AGPLv3](/license), con la "
        "[condición de atribución de la sección 7(b)](/notice). "
        "[Código fuente de esta versión](/source)."
    ),
    version=__version__,
    license_info={
        "name": "GNU AGPLv3 with author attribution under section 7(b)",
        "url": PUBLIC_URL + "/license",
    },
    lifespan=lifespan,
)

# Configurar templates
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request):
    """Página principal de la aplicación"""
    manifest_path = Path('static/ui/.vite/manifest.json')
    entry = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        entry = manifest.get('src/main.ts', {})
    dev_url = os.getenv('VITE_DEV_URL', '').rstrip('/')
    context = {"request": request, "public_url": PUBLIC_URL,
               "ui_entry": entry, "vite_dev_url": dev_url}
    response = templates.TemplateResponse(request=request, name="index.html", context=context)

    # Headers para evitar caché del HTML principal (siempre obtener la versión más reciente)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


# Incluir routers
app.include_router(sismos.router)
app.include_router(admin.router)
app.include_router(seo.router)
app.include_router(legal.router)

# Configurar manejadores de excepciones (por implementar)
# app.add_exception_handler(UndefinedError, jinja_undefined_handler)

# Configurar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
