import { defineConfig } from 'astro/config';

// Remplacer par l'URL finale (Netlify) au moment du déploiement.
export default defineConfig({
  site: 'https://site-chasse.netlify.app',
  build: { format: 'directory' }
});
