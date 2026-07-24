// Gibier d'eau : dates fixées au niveau NATIONAL.
//   - Ouverture : arrêté du 24 mars 2006 (modifié), échelonnée selon le territoire.
//   - Fermeture : arrêté du 19 janvier 2009 (modifié).
//
// Ouverture échelonnée :
//   - Domaine public maritime (départements côtiers) : 1er samedi d'août.
//   - Marais, étangs et plans d'eau intérieurs : 3e décade d'août (21 août) pour la plupart des
//     espèces ; 15 septembre pour 6 espèces plus tardives (chipeau, milouin, nette rousse, foulque,
//     poule d'eau, râle d'eau).
// Fermeture : 31 janvier (intérieur), repoussée sur le domaine public maritime pour certaines espèces.
//
// NB : des ouvertures anticipées locales existent dans quelques départements (Gironde : 2e décade
// d'août ; Hérault/Gard : 15 août sur certains étangs ; Ain/Indre/Loire : septembre) — non encore
// intégrées ici, à ajouter comme raffinement.

// Départements côtiers métropolitains ouvrant le gibier d'eau au 1er samedi d'août sur le domaine
// public maritime. On retient les 25 à façade maritime ouverte ; l'Eure (estuaire de la Seine),
// 26e « littoral » au sens de la loi Littoral, est volontairement exclue : son domaine maritime pour
// la chasse au gibier d'eau est incertain (décision validée avec l'utilisateur).
export const DEPARTEMENTS_COTIERS = [
  '06', '11', '13', '14', '17', '22', '29', '2A', '2B', '30', '33', '34', '35',
  '40', '44', '50', '56', '59', '62', '64', '66', '76', '80', '83', '85',
];

export interface GibierEau {
  ouvertureInterieur: 'troisieme-decade-aout' | '15-septembre';
  fermeture: { mois: number; jour: number };
  statut?: 'moratoire' | 'mer-uniquement'; // chasse suspendue, ou autorisée seulement en mer
  note?: string;                            // mention permanente (restriction, gestion adaptative…)
}

const PRECOCE: GibierEau = { ouvertureInterieur: 'troisieme-decade-aout', fermeture: { mois: 1, jour: 31 } };
const TARDIF: GibierEau = { ouvertureInterieur: '15-septembre', fermeture: { mois: 1, jour: 31 } };

export const GIBIER_EAU: Record<string, GibierEau> = {
  // --- Vague 2a : canards de surface, plongeurs courants, oies, rallidés ---
  'canard-colvert': PRECOCE,
  'sarcelle-hiver': PRECOCE,
  'sarcelle-ete': PRECOCE,
  'canard-siffleur': PRECOCE,
  'canard-pilet': PRECOCE,
  'canard-souchet': PRECOCE,
  'fuligule-morillon': PRECOCE,
  'oie-cendree': PRECOCE,
  'oie-rieuse': PRECOCE,
  'oie-moissons': PRECOCE,
  'canard-chipeau': TARDIF,
  'fuligule-milouin': {
    ...TARDIF,
    note: "Espèce en gestion adaptative : la chasse ferme dès l'atteinte du quota national.",
  },
  'nette-rousse': TARDIF,
  'foulque-macroule': TARDIF,
  'poule-eau': TARDIF,
  'rale-eau': TARDIF,

  // --- Vague 2b : canards marins / plongeurs rares ---
  'fuligule-milouinan': PRECOCE,
  'garrot-oeil-dor': PRECOCE,
  'harelde-boreale': PRECOCE,
  'macreuse-brune': PRECOCE,
  'macreuse-noire': PRECOCE,
  'eider-a-duvet': { ...PRECOCE, statut: 'mer-uniquement' },

  // --- Vague 2b : limicoles ---
  'barge-rousse': PRECOCE,
  'barge-queue-noire': { ...PRECOCE, statut: 'moratoire' },
  'becasseau-maubeche': PRECOCE,
  'chevalier-aboyeur': PRECOCE,
  'chevalier-arlequin': PRECOCE,
  'chevalier-combattant': PRECOCE,
  'chevalier-gambette': PRECOCE,
  'courlis-corlieu': PRECOCE,
  'courlis-cendre': { ...PRECOCE, statut: 'moratoire' },
  'huitrier-pie': PRECOCE,
  'pluvier-dore': PRECOCE,
  'pluvier-argente': PRECOCE,
  'vanneau-huppe': PRECOCE,
  'becassine-marais': { ...PRECOCE, note: "Jusqu'au 21 août à 6 h, chasse autorisée seulement sur les prairies humides et les marais aménagés." },
  'becassine-sourde': { ...PRECOCE, note: "Jusqu'au 21 août à 6 h, chasse autorisée seulement sur les prairies humides et les marais aménagés." },
};

export const SOURCE_GIBIER_EAU = {
  label:
    "Arrêté du 24 mars 2006 (ouverture) et arrêté du 19 janvier 2009 (fermeture) relatifs à la chasse au gibier d'eau, modifiés",
  url: 'https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000456442',
};

// 1er samedi d'août pour une année donnée (renvoie une date ISO AAAA-MM-JJ).
export function premierSamediAout(annee: number): string {
  const d = new Date(Date.UTC(annee, 7, 1)); // 1er août
  d.setUTCDate(1 + ((6 - d.getUTCDay() + 7) % 7)); // avance jusqu'au samedi (getUTCDay: 6 = samedi)
  return d.toISOString().slice(0, 10);
}
