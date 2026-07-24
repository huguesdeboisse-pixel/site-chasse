#!/usr/bin/env python3
"""
Audit des données réglementaires du site (src/data/periodes/*.json).

Objectif : attraper les erreurs qu'un relecteur humain ne peut pas repérer à la main,
SANS demander de jugement métier. Trois volets :

  1. SUSPECT  — la classe d'erreur la plus dangereuse (donnée inventée / source faible) :
                statut « signé » sans PDF, source qui n'est qu'une page d'accueil de
                préfecture, champ vide, dates hors plage plausible.
  2. MANQUES  — complétude des espèces localisées (faux négatifs). On utilise un « filet de
                plausibilité » GROSSIER et volontairement large (par massif) : il ne décide
                RIEN à l'écran, il liste seulement les départements « plausibles mais non
                renseignés » à aller vérifier dans l'arrêté.
  3. COUVERTURE — départements non collectés, fiches pauvres.

Usage :  python3 scripts/audit_donnees.py          (audit hors-ligne)
         python3 scripts/audit_donnees.py --liens   (vérifie aussi les liens, réseau requis)
"""
import json, glob, os, re, sys, urllib.request
from collections import defaultdict

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_PERIODES = os.path.join(RACINE, 'src', 'data', 'periodes')
F_DEPTS = os.path.join(RACINE, 'src', 'data', 'departements-france.json')

DROM = {'Guadeloupe', 'Martinique', 'Guyane', 'La Réunion', 'Mayotte'}

# --- Filet de plausibilité (GROSSIER, généreux par design) : massifs -> départements ---
# Alpes « galliformes » (sans la frange méditerranéenne littorale, non montagnarde).
ALPES_GALL = {'01', '04', '05', '06', '07', '26', '38', '73', '74'}
# Alpes « chamois » : idem + populations introduites de Provence / basses Alpes.
ALPES_CHAMOIS = ALPES_GALL | {'13', '83', '84'}
PYRENEES = {'09', '11', '31', '64', '65', '66'}
JURA = {'01', '25', '39'}
VOSGES = {'67', '68', '70', '88', '90'}
# Massif central : seulement les départements à relief marqué (chamois), pas la plaine limousine.
MASSIF_CENTRAL = {'07', '12', '15', '19', '42', '43', '48', '63'}

# Aire plausible par espèce localisée. None = aire trop dispersée (audit de complétude non fiable).
AIRE_PLAUSIBLE = {
    'chamois': ALPES_CHAMOIS | PYRENEES | JURA | VOSGES | MASSIF_CENTRAL | {'71'},
    'tetras-lyre': ALPES_GALL,
    'lagopede-alpin': ALPES_GALL | PYRENEES,
    'perdrix-bartavelle': ALPES_GALL | PYRENEES,
    'mouflon-mediterraneen': None,  # introductions dispersées -> pas de filet fiable
}

def charger():
    depts = json.load(open(F_DEPTS))['departements']
    noms = {d['code']: d['nom'] for d in depts}
    regions = {d['code']: d['region'] for d in depts}
    periodes = {}
    for f in glob.glob(os.path.join(DIR_PERIODES, '*.json')):
        j = json.load(open(f))
        periodes[j['departement']] = j
    return depts, noms, regions, periodes

def url_faible(url):
    """Vrai si l'URL n'est qu'une racine de domaine (pas de chemin vers un document précis)."""
    if not url:
        return True
    m = re.match(r'https?://[^/]+(/.*)?$', url.strip())
    chemin = (m.group(1) or '') if m else ''
    return chemin in ('', '/')

def volet_suspect(periodes, noms):
    print('\n=== 1. SUSPECT (à contrôler en priorité) ===')
    n = 0
    for code, j in sorted(periodes.items()):
        etiquette = f'{code} {noms.get(code, "?")}'
        # a) ouverture générale : source faible ou confiance non haute
        og = j.get('ouverture_generale', {})
        if url_faible(og.get('source_url')):
            print(f'  [{etiquette}] ouverture générale : source faible (racine de domaine) -> {og.get("source_url")!r}'); n += 1
        if og.get('confiance') and og['confiance'] != 'haute':
            print(f'  [{etiquette}] ouverture générale : confiance = {og["confiance"]!r}'); n += 1
        # b) arrêtés « signés » sans PDF réel
        for a in j.get('arretes_officiels', []):
            if 'sign' in (a.get('statut', '').lower()) and url_faible(a.get('url_pdf')):
                print(f'  [{etiquette}] arrêté « {a.get("statut")} » SANS PDF : {a.get("reference","?")!r}'); n += 1
        # c) faits : détail ou source vide, source faible
        for e in j.get('especes', []):
            for fa in e.get('faits', []):
                if not fa.get('detail', '').strip():
                    print(f'  [{etiquette}] {e["slug"]} : fait « {fa.get("label")} » au détail vide'); n += 1
                if url_faible(fa.get('source_url')):
                    print(f'  [{etiquette}] {e["slug"]} : fait « {fa.get("label")} » à source faible -> {fa.get("source_url")!r}'); n += 1
    if not n:
        print('  (rien)')
    return n

def volet_manques(periodes, noms, regions):
    print('\n=== 2. MANQUES de complétude (espèces localisées plausibles mais non renseignées) ===')
    n = 0
    for slug, aire in AIRE_PLAUSIBLE.items():
        if aire is None:
            print(f'  {slug} : aire trop dispersée -> audit de complétude non fiable (vérif. par la seule collecte).')
            continue
        manquants = []
        for code in sorted(aire):
            j = periodes.get(code)
            if not j:
                manquants.append(f'{code}(non collecté)')
                continue
            a_donnee = any(e['slug'] == slug and e.get('faits') for e in j.get('especes', []))
            if not a_donnee:
                manquants.append(code)
        if manquants:
            print(f'  {slug} : à vérifier dans l\'arrêté de -> {", ".join(manquants)}')
            n += len(manquants)
    if not n:
        print('  (aucun manque plausible)')
    return n

def volet_couverture(depts, periodes, regions):
    print('\n=== 3. COUVERTURE ===')
    metro = [d for d in depts if d['region'] not in DROM]
    sans = [d for d in depts if d['code'] not in periodes]
    print(f'  {len(periodes)}/{len(depts)} départements avec fichier ; {len(sans)} sans.')
    print('  Sans fichier : ' + ', '.join(f'{d["code"]}' for d in sans))
    pauvres = []
    for d in metro:
        j = periodes.get(d['code'])
        if not j:
            continue
        nb = sum(1 for e in j.get('especes', []) if e.get('faits'))
        if nb < 5:
            pauvres.append(f'{d["code"]}({nb})')
    print(f'  Fiches pauvres (< 5 espèces avec faits) : ' + (', '.join(pauvres) or '(aucune)'))

def verifier_liens(periodes):
    print('\n=== LIENS (réseau) ===')
    urls = set()
    for j in periodes.values():
        urls.add(j.get('ouverture_generale', {}).get('source_url'))
        for a in j.get('arretes_officiels', []):
            urls.add(a.get('url_pdf'))
        for e in j.get('especes', []):
            for fa in e.get('faits', []):
                urls.add(fa.get('source_url'))
    urls = {u for u in urls if u and not url_faible(u)}
    morts = 0
    for u in sorted(urls):
        try:
            req = urllib.request.Request(u, method='HEAD', headers={'User-Agent': 'audit'})
            urllib.request.urlopen(req, timeout=12)
        except Exception as ex:
            print(f'  MORT/ERREUR : {u}  ({type(ex).__name__})'); morts += 1
    print(f'  {len(urls)} liens testés, {morts} en erreur.')

def main():
    depts, noms, regions, periodes = charger()
    print(f'Audit — {len(periodes)} fichiers periodes chargés.')
    s = volet_suspect(periodes, noms)
    m = volet_manques(periodes, noms, regions)
    volet_couverture(depts, periodes, regions)
    if '--liens' in sys.argv:
        verifier_liens(periodes)
    print(f'\nRésumé : {s} entrée(s) suspecte(s), {m} manque(s) plausible(s) à vérifier.')

if __name__ == '__main__':
    main()
