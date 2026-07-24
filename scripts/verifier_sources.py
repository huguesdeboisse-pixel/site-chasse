#!/usr/bin/env python3
"""
Niveau 3 — Fidélité à la source.

Pour chaque département, télécharge le PDF de l'arrêté cité pour l'ouverture générale,
en extrait le texte, et vérifie que les dates COLLECTÉES (ouverture / fermeture) y
FIGURENT bien. C'est la parade à l'invention : une date absente du PDF est signalée.

Verdicts par département :
  OK        toutes les dates de l'ouverture générale retrouvées dans le PDF
  ABSENTE   au moins une date collectée introuvable dans le PDF  -> à contrôler
  SCANNE    PDF sans texte extractible (image)  -> OCR / vérif. manuelle
  ERREUR    téléchargement / extraction impossible

Usage :
  python3 scripts/verifier_sources.py 03 63 19      # départements précis
  python3 scripts/verifier_sources.py --tous        # tous les collectés (long)
"""
import json, glob, os, re, sys, subprocess, tempfile, urllib.request

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_PERIODES = os.path.join(RACINE, 'src', 'data', 'periodes')
CACHE = os.path.join(tempfile.gettempdir(), 'audit_pdf_cache')
os.makedirs(CACHE, exist_ok=True)

MOIS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet',
        'août', 'septembre', 'octobre', 'novembre', 'décembre']

def variantes_date(iso):
    """Formes sous lesquelles une date ISO peut apparaître dans un PDF."""
    y, m, d = (int(x) for x in iso.split('-'))
    mois = MOIS[m - 1]
    formes = [
        rf'\b0?{d}\s*(?:er)?\s*{mois}',                       # 20 septembre / 1er août
        rf'\b0?{d}\s*[/.\-]\s*0?{m}\s*[/.\-]\s*(?:{y}|{y%100})',  # 20/09/2026 / 20.09.26
    ]
    # août peut être écrit "aout" sans accent
    if mois == 'août':
        formes.append(rf'\b0?{d}\s*(?:er)?\s*aout')
    return formes

def texte_pdf(url):
    """Télécharge (cache) et extrait le texte d'un PDF. ('' si scanné, None si erreur)."""
    nom = re.sub(r'\W+', '_', url)[-120:] + '.pdf'
    chemin = os.path.join(CACHE, nom)
    if not os.path.exists(chemin):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 audit'})
            data = urllib.request.urlopen(req, timeout=30).read()
            open(chemin, 'wb').write(data)
        except Exception as ex:
            return None, f'{type(ex).__name__}'
    try:
        out = subprocess.run(['pdftotext', '-layout', chemin, '-'],
                             capture_output=True, timeout=60)
        return out.stdout.decode('utf-8', 'ignore'), None
    except Exception as ex:
        return None, f'extraction:{type(ex).__name__}'

def verifier(code):
    p = os.path.join(DIR_PERIODES, f'{code}.json')
    if not os.path.exists(p):
        return code, 'ERREUR', 'pas de fichier'
    j = json.load(open(p))
    og = j.get('ouverture_generale', {})
    url = og.get('source_url')
    if not url:
        return code, 'ERREUR', 'pas de source'
    texte, err = texte_pdf(url)
    if texte is None:
        return code, 'ERREUR', err
    if len(texte.strip()) < 200:
        return code, 'SCANNE', 'texte non extractible (image)'
    t = texte.lower()
    manquantes = []
    for champ in ('date', 'fermeture'):
        iso = og.get(champ)
        if not iso:
            continue
        if not any(re.search(f, t) for f in variantes_date(iso)):
            manquantes.append(f'{champ}={iso}')
    if manquantes:
        return code, 'ABSENTE', ', '.join(manquantes)
    return code, 'OK', ''

def main():
    args = sys.argv[1:]
    if '--tous' in args:
        codes = sorted(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(DIR_PERIODES, '*.json')))
    else:
        codes = [a for a in args if not a.startswith('--')]
    if not codes:
        print(__doc__); return
    compte = {}
    for code in codes:
        c, verdict, detail = verifier(code)
        compte[verdict] = compte.get(verdict, 0) + 1
        marque = {'OK': '✓', 'ABSENTE': '✗', 'SCANNE': '⚠', 'ERREUR': '⚠'}[verdict]
        print(f'  {marque} {c:>3} {verdict:8} {detail}')
    print('\nRésumé :', ', '.join(f'{k}={v}' for k, v in sorted(compte.items())))

if __name__ == '__main__':
    main()
