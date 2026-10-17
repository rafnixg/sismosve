// Run with playwright-cli run-code --filename frontend/checks/review-regressions.js
async page => {
  const assert = (value, message) => { if (!value) throw new Error(message); };
  const fixture = {
    type: 'sismos',
    features: Array.from({ length: 20 }, (_, index) => ({
      type: 'Sismo', geometry: { type: 'Point', coordinates: [-66 + (index % 3) * .03, 8 + index * .03] },
      properties: {
        value: '2.9', date: '17-10-2026', time: `${String(index).padStart(2, '0')}:00`,
        addressFormatted: `Registro ${index}`, depth: '10 km', country: 'Venezuela',
        lat: String(8 + index * .03), long: String(-66 + (index % 3) * .03),
      },
    })),
  };
  let reads = 0;
  let updates = 0;
  let failRead = false;
  let failUpdate = true;
  const errors = [];
  const onError = error => errors.push(error.message);
  page.on('pageerror', onError);
  await page.route('**/api/sismos', async route => {
    reads++;
    if (failRead) {
      failRead = false;
      await route.fulfill({ status: 503, json: { detail: 'offline' } });
    } else await route.fulfill({ json: fixture });
  });
  await page.route('**/api/update', async route => {
    updates++;
    await route.fulfill({ json: { success: !failUpdate } });
  });
  const ready = () => page.getByRole('status').filter({ hasText: 'Consultado' }).waitFor();
  const error = text => page.getByRole('alert').filter({ hasText: text }).waitFor();
  try {
    await page.goto('http://localhost:8001/');
    await ready();
    assert(reads === 1 && updates === 0, 'Unexpected initial requests');

    await page.getByRole('button', { name: 'Actualizar desde FUNVISIS' }).click();
    await error('FUNVISIS');
    assert(updates === 1 && reads === 1, 'Failed update unexpectedly reread records');
    await page.getByRole('button', { name: 'Reintentar' }).click();
    await error('FUNVISIS');
    assert(updates === 2 && reads === 1, 'Retry must repeat POST /api/update');
    assert(await page.locator('.event-row').count() === 20, 'Retry discarded saved records');

    failUpdate = false;
    await page.getByRole('button', { name: 'Reintentar' }).click();
    await ready();
    assert(updates === 3 && reads === 2, 'Successful update retry must reload records');
    assert(await page.getByRole('alert').count() === 0, 'Recovered update retained error');

    failRead = true;
    await page.getByRole('button', { name: 'Recargar', exact: true }).click();
    await error('503');
    const updatesBeforeReadRetry = updates;
    const readsBeforeReadRetry = reads;
    await page.getByRole('button', { name: 'Reintentar' }).click();
    await ready();
    assert(updates === updatesBeforeReadRetry && reads === readsBeforeReadRetry + 1,
      'A failed GET retry must not force a FUNVISIS update');

    failRead = true;
    await page.getByRole('button', { name: 'Actualizar desde FUNVISIS' }).click();
    await error('503');
    const updatesAfterSuccessfulPost = updates;
    await page.getByRole('button', { name: 'Reintentar' }).click();
    await ready();
    assert(updates === updatesAfterSuccessfulPost,
      'Do not repeat an already successful POST when its subsequent GET failed');

    for (const width of [375, 768, 1440]) {
      await page.setViewportSize({ width, height: 900 });
      await page.reload();
      await ready();
      await page.evaluate(() => {
        const map = document.querySelector('.map-panel');
        window.scrollTo(0, map.getBoundingClientRect().top + scrollY - 16);
      });
      const scrollBefore = await page.evaluate(() => scrollY);
      // Target the marker's click handler directly: the fixture deliberately
      // packs nearby events whose circle markers can overlap at low zoom.
      await page.locator('.leaflet-interactive').last().dispatchEvent('click');
      await page.waitForFunction(() => {
        const row = document.querySelector('.event-row[aria-pressed="true"]');
        const list = document.querySelector('.event-list');
        return row && row.textContent.includes('Registro 0') && list.scrollTop > 0;
      }, null, { timeout: 5000 });
      assert(Math.abs(await page.evaluate(() => scrollY) - scrollBefore) < 1,
        `Map selection scrolled the page at ${width}px`);
      assert(await page.locator('.leaflet-popup-content').isVisible(), 'Map popup was lost');
      const visible = await page.locator('.event-list').evaluate(list => {
        const row = list.querySelector('.event-row[aria-pressed="true"]').getBoundingClientRect();
        const box = list.getBoundingClientRect();
        return row.top >= box.top - 1 && row.bottom <= box.bottom + 1;
      });
      assert(visible, `Selected row is not visible in its list at ${width}px`);

      // Exercise upward synchronization independently, with the list scrolled down.
      await page.reload();
      await ready();
      await page.locator('.event-list').evaluate(list => list.scrollTop = list.scrollHeight);
      await page.evaluate(() => {
        const map = document.querySelector('.map-panel');
        window.scrollTo(0, map.getBoundingClientRect().top + scrollY - 16);
      });
      const scrollBeforeUp = await page.evaluate(() => scrollY);
      await page.locator('.leaflet-interactive').first().dispatchEvent('click');
      await page.waitForFunction(() => document.querySelector('.event-list').scrollTop === 0, null, { timeout: 5000 });
      assert(Math.abs(await page.evaluate(() => scrollY) - scrollBeforeUp) < 1,
        `Upward selection scrolled the page at ${width}px`);
    }
    assert(errors.length === 0, errors.join('\n'));
    return { passed: true, retryModes: ['failed POST', 'failed GET', 'GET after successful POST'], scrollWidths: [375, 768, 1440] };
  } finally {
    page.off('pageerror', onError);
    await page.unroute('**/api/sismos');
    await page.unroute('**/api/update');
    await page.reload();
  }
}
