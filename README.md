# Site de référence chasse — France entière

Site statique **Astro** déployé sur **Netlify**. Les données sont versionnées dans `src/data/` et chaque donnée porte sa source officielle.

## Démarrer en local

```bash
npm install
npm run dev
```

Puis ouvrir http://localhost:4321

## Build

```bash
npm run build   # génère le dossier dist/
```

## Déploiement Netlify

1. Pousser ce dépôt sur GitHub.
2. Sur Netlify : « Add new site » → « Import from GitHub » → sélectionner le dépôt.
3. Build command `npm run build`, publish directory `dist` (déjà dans `netlify.toml`).
4. Renseigner l'URL finale dans `astro.config.mjs` (champ `site`).

## Structure

- `src/data/departements-france.json` — les 101 départements (carte + fiche) + sources officielles connues (FDC, préfecture). Le détail réglementaire réel (`periodes/`) est collecté région par région, pas encore disponible partout.
- `src/data/especes.json` — liste de référence des espèces.
- `src/data/periodes/{code}.json` — dates/quotas par département (ex. `74.json`), avec leur source.
- `src/pages/index.astro` — accueil (liste des départements).
- `src/pages/departements/[code].astro` — fiche département (données + sources).
- `src/pages/methodologie.astro` — règles de sourcing.

## Données & sourcing

Règle dure : **aucune donnée sans `source_url` officielle**. Le pipeline (à venir dans `pipeline/`) récupère les pages préfecture/FDC, parse les PDF d'arrêtés, applique le contrôle qualité et écrit `src/data/periodes/{code}.json`. Chaque changement = un commit Git (journal d'audit).

## Prochaines briques

- Pipeline d'extraction (`pipeline/`) : itérer les 101 départements, parser les arrêtés, remplir `periodes/`. Aujourd'hui fait à la main, région par région.
- Comparateur inter-départemental, recherche (Pagefind), carte Leaflet/IGN.
- Analytics Matomo + bandeau de consentement (RGPD).
