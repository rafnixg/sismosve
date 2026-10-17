import { mount } from 'svelte';
import '@fontsource/source-sans-3/latin-400.css';
import '@fontsource/source-sans-3/latin-600.css';
import '@fontsource/source-sans-3/latin-700.css';
import 'leaflet/dist/leaflet.css';
import './styles.css';
import App from './App.svelte';

mount(App, { target: document.getElementById('sismos-app')! });
