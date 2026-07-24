// Oiseaux de passage : dates fixées au niveau NATIONAL (et non par l'arrêté préfectoral).
//   - Ouverture  : arrêté du 24 mars 2006 (modifié).
//   - Fermeture  : arrêté du 19 janvier 2009 (modifié).
// Pour la plupart de ces oiseaux, l'ouverture est fixée « à la date d'ouverture générale du
// département » : on réutilise donc la date d'ouverture générale déjà connue pour le
// département, et seule la fermeture est une date nationale. La caille des blés ouvre au
// dernier samedi d'août.
//
// ATTENTION : pour les grives et le merle noir, la fermeture est le 10 février PARTOUT SAUF
// dans 17 départements du Sud (fermeture au 20 février). Pour le pigeon ramier, fermeture au
// 10 février partout, prolongée au 20 février à poste fixe dans 13 départements du Sud-Ouest.
// (Le canard colvert est du gibier d'eau, régime différent : traité à part, pas ici.)

// 17 départements du Sud où grives + merle ferment le 20 février (art. 2 de l'arrêté du 19/01/2009).
const GRIVES_SUD = ['04', '05', '06', '07', '11', '12', '13', '26', '2A', '2B', '30', '34', '48', '66', '81', '83', '84'];
// 13 départements du Sud-Ouest où le pigeon ramier est chassable jusqu'au 20 février à poste fixe (art. 4).
const RAMIER_SUD_OUEST = ['09', '12', '24', '31', '32', '33', '40', '46', '47', '64', '65', '81', '82'];

export interface OiseauPassage {
  ouverture: 'generale' | 'dernier-samedi-aout';
  fermeture: { mois: number; jour: number };
  // Dérogation de fermeture dans certains départements (liste + date + mention à afficher).
  fermetureDerogation?: { mois: number; jour: number; departements: string[]; note: string };
  statut?: 'moratoire'; // chasse suspendue : on n'affiche pas de dates
  note?: string;        // mention permanente (ex. plafond de prélèvement bécasse)
}

const posteFixeGrives = "Du 10 au 20 février, chasse autorisée uniquement à poste fixe matérialisé de main d'homme.";
const posteFixeRamier = "Du 11 au 20 février, chasse autorisée uniquement à poste fixe matérialisé de main d'homme.";
const grive: OiseauPassage = {
  ouverture: 'generale',
  fermeture: { mois: 2, jour: 10 },
  fermetureDerogation: { mois: 2, jour: 20, departements: GRIVES_SUD, note: posteFixeGrives },
};

export const OISEAUX_DE_PASSAGE: Record<string, OiseauPassage> = {
  'grive-draine': grive,
  'grive-litorne': grive,
  'grive-mauvis': grive,
  'grive-musicienne': grive,
  'merle-noir': grive,
  'pigeon-ramier': {
    ouverture: 'generale',
    fermeture: { mois: 2, jour: 10 },
    fermetureDerogation: { mois: 2, jour: 20, departements: RAMIER_SUD_OUEST, note: posteFixeRamier },
  },
  'pigeon-colombin': { ouverture: 'generale', fermeture: { mois: 2, jour: 10 } },
  'pigeon-biset': { ouverture: 'generale', fermeture: { mois: 2, jour: 10 } },
  'alouette-champs': { ouverture: 'generale', fermeture: { mois: 1, jour: 31 } },
  'tourterelle-turque': { ouverture: 'generale', fermeture: { mois: 2, jour: 20 } },
  'tourterelle-bois': { ouverture: 'generale', fermeture: { mois: 2, jour: 20 }, statut: 'moratoire' },
  'caille-bles': { ouverture: 'dernier-samedi-aout', fermeture: { mois: 2, jour: 20 } },
  'becasse-bois': {
    ouverture: 'generale',
    fermeture: { mois: 2, jour: 20 },
    note: "Prélèvement maximal autorisé national : 30 oiseaux par saison et par chasseur ; les plafonds journalier et hebdomadaire sont fixés par arrêté préfectoral.",
  },
};

// Source nationale à citer pour ces dates.
export const SOURCE_PASSAGE = {
  label:
    "Arrêté du 24 mars 2006 (ouverture) et arrêté du 19 janvier 2009 (fermeture) relatifs à la chasse aux oiseaux de passage, modifiés",
  url: 'https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000456442',
};

// Dernier samedi d'août pour une année donnée (renvoie une date ISO AAAA-MM-JJ).
export function dernierSamediAout(annee: number): string {
  const d = new Date(Date.UTC(annee, 7, 31)); // 31 août
  d.setUTCDate(31 - ((d.getUTCDay() + 1) % 7)); // recule jusqu'au samedi (getUTCDay: 6 = samedi)
  return d.toISOString().slice(0, 10);
}
