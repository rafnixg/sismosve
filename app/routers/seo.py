"""
Router para endpoints especiales de SEO y archivos estáticos especiales
"""

import logging
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response

from ..config import STATIC_DIR

logger = logging.getLogger(__name__)
router = APIRouter(include_in_schema=False)


@router.get("/robots.txt")
async def robots_txt():
    """Archivo robots.txt para crawlers"""
    try:
        robots_path = STATIC_DIR / "robots.txt"
        if robots_path.exists():
            content = robots_path.read_text(encoding='utf-8')
            return Response(content=content, media_type="text/plain")
        else:
            return Response(
                content="User-agent: *\nAllow: /\nSitemap: /sitemap.xml",
                media_type="text/plain"
            )
    except Exception as e:
        logger.error("Error serving robots.txt: %s", e)
        return Response(
            content="User-agent: *\nAllow: /",
            media_type="text/plain"
        )


@router.get("/sitemap.xml")
async def sitemap_xml(request: Request):
    """Sitemap XML para SEO"""
    try:
        sitemap_path = STATIC_DIR / "sitemap.xml"
        if sitemap_path.exists():
            content = sitemap_path.read_text(encoding='utf-8')
            # Reemplazar placeholder con URL real
            content = content.replace("https://sismo.rafnixg.dev", str(request.base_url).rstrip('/'))
            return Response(content=content, media_type="application/xml")
        else:
            # Sitemap básico si no existe el archivo
            basic_sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{request.base_url}</loc>
    <lastmod>2025-09-25</lastmod>
    <changefreq>hourly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>'''
            return Response(content=basic_sitemap, media_type="application/xml")
    except Exception as e:
        logger.error("Error serving sitemap.xml: %s", e)
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/humans.txt")
async def humans_txt():
    """Archivo humans.txt con información del equipo"""
    try:
        humans_path = STATIC_DIR / "humans.txt"
        if humans_path.exists():
            content = humans_path.read_text(encoding='utf-8')
            return Response(content=content, media_type="text/plain")
        else:
            return Response(
                content="# SismosVE Team\nDeveloped with ❤️ for Venezuela",
                media_type="text/plain"
            )
    except Exception as e:
        logger.error("Error serving humans.txt: %s", e)
        return Response(
            content="# SismosVE - Error loading team info",
            media_type="text/plain"
        )


@router.get("/llms.txt")
async def llms_txt():
    """Archivo llms.txt para crawlers de IA"""
    try:
        llms_path = STATIC_DIR / "llms.txt"
        if llms_path.exists():
            content = llms_path.read_text(encoding='utf-8')
            return Response(content=content, media_type="text/plain")
        else:
            return Response(
                content="# SismosVE - AI Guidelines\nThis site provides earthquake data for Venezuela.",
                media_type="text/plain"
            )
    except Exception as e:
        logger.error("Error serving llms.txt: %s", e)
        return Response(
            content="# SismosVE - Error loading AI guidelines",
            media_type="text/plain"
        )


@router.get("/.well-known/security.txt")
async def security_txt():
    """Archivo security.txt para reporte de vulnerabilidades"""
    try:
        security_path = STATIC_DIR / ".well-known" / "security.txt"
        if security_path.exists():
            content = security_path.read_text(encoding='utf-8')
            return Response(content=content, media_type="text/plain")
        else:
            return Response(
                content="Contact: security@sismo.rafnixg.dev\nExpires: 2026-09-25T23:59:59.000Z",
                media_type="text/plain"
            )
    except Exception as e:
        logger.error("Error serving security.txt: %s", e)
        return Response(
            content="Contact: security@sismo.rafnixg.dev",
            media_type="text/plain"
        )