# Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
# SPDX-License-Identifier: AGPL-3.0-only
# Additional author-attribution term under section 7(b): see repository-root NOTICE.
"""Serve the license, author notice and corresponding-source offer."""
import os

from fastapi import APIRouter
from fastapi.responses import FileResponse, RedirectResponse

from ..config import BASE_DIR


router = APIRouter(include_in_schema=False)


@router.get('/license')
async def license_text():
    return FileResponse(BASE_DIR / 'LICENSE', media_type='text/plain',
                        headers={'Link': '</notice>; rel="describedby"'})


@router.get('/notice')
async def attribution_notice():
    return FileResponse(BASE_DIR / 'NOTICE', media_type='text/plain')


@router.get('/source')
async def corresponding_source():
    source_url = os.getenv('SOURCE_URL', 'https://github.com/rafnixg/sismosve')
    return RedirectResponse(source_url, status_code=302)
