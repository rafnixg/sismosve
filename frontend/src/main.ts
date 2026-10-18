/*
Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
SPDX-License-Identifier: AGPL-3.0-only
Additional author-attribution term under section 7(b): see repository-root NOTICE.
*/
import { mount } from 'svelte';
import '@fontsource/source-sans-3/latin-400.css';
import '@fontsource/source-sans-3/latin-600.css';
import '@fontsource/source-sans-3/latin-700.css';
import 'leaflet/dist/leaflet.css';
import './styles.css';
import App from './App.svelte';

mount(App, { target: document.getElementById('sismos-app')! });
