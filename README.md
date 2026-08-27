# Site institutionnel | PRIME ADVISORS SB, Inc.

Site vitrine institutionnel et commercial, en HTML/CSS/JavaScript statique.
Aucune étape de compilation, aucune dépendance à installer : les fichiers
livrés sont ceux qui sont mis en ligne.

---

## 1. Mise en ligne

Déposer le contenu du dossier à la racine de l'hébergement. Le site fonctionne
sur n'importe quel hébergeur statique (Netlify, Vercel, GitHub Pages, OVH, cPanel…).

```
index.html              Accueil
la-compagnie.html       La compagnie
nos-expertises.html     Nos expertises
nos-solutions.html      Nos solutions
nos-references.html     Nos références
contact.html            Contact
robots.txt              Indexation
sitemap.xml             Plan de site
assets/css/style.css    Système de design (couleurs, typographie, composants)
assets/js/main.js       Menu mobile, animations, filtres, formulaire
assets/img/             Logos et favicon
```

Pour prévisualiser en local :

```bash
python -m http.server 4321
```

Puis ouvrir <http://localhost:4321>.

---

## 2. Points à compléter avant la mise en production

Ces éléments n'ont pas été inventés : ils attendent une information officielle.
Chacun est signalé par un commentaire `À COMPLÉTER` dans le code.

| Élément | Fichier | Action |
|---|---|---|
| **Nom de domaine** | toutes les pages + `sitemap.xml`, `robots.txt` | Les balises `canonical`, Open Graph et le sitemap utilisent `https://www.primeadvisors-sb.com` (déduit de l'adresse e-mail). À confirmer, puis rechercher/remplacer si le domaine diffère. |
| **Destination du formulaire** | `contact.html` | Voir section 3 ci-dessous. |
| **Lien LinkedIn** | pied de page des 6 pages, `contact.html` | Décommenter le bloc et remplacer `HREF_LINKEDIN`. |
| **Références clients** | `nos-references.html` | Voir section 4 ci-dessous. |
| **Logos clients** | `nos-references.html` | Section « Ils nous font confiance » désactivée tant que les fichiers **et** les autorisations d'utilisation ne sont pas fournis. |

WhatsApp est en place : le numéro **+225 05 66 42 72 72** (`https://wa.me/2250566427272`)
est branché sur l'icône de l'en-tête, le pied de page, la page Contact et les
appels à l'action de fin de page. Pour en changer, rechercher `2250566427272`
dans les six pages HTML.

---

## 3. Formulaire de contact

Le formulaire valide les champs côté navigateur (messages en français, résumé
d'erreurs accessible au clavier et aux lecteurs d'écran), puis envoie la demande.

**Deux adresses, deux rôles à ne pas confondre :**

| Attribut du `<form>` | Valeur | Rôle |
|---|---|---|
| `data-mailto` | `contact@primeadvisors-sb.com` | Boîte qui **reçoit** les demandes du formulaire. Jamais affichée. |
| `data-public-email` | `corporate@primeadvisors-sb.com` | Adresse **publiée**, la seule montrée au visiteur (coordonnées, pied de page, messages de repli). |

Elles n'ont pas à coïncider et peuvent évoluer séparément. Si
`data-public-email` est retiré, les messages retombent sur l'adresse de
réception plutôt que d'afficher un texte tronqué.

**Aujourd'hui, sans configuration**, le formulaire ouvre le logiciel de
messagerie du visiteur avec un message pré-rempli vers l'adresse de
réception. C'est fonctionnel, mais dépendant du poste du visiteur.

**Pour un envoi direct**, renseigner un service de traitement de formulaire
(Formspree, Web3Forms, Netlify Forms, ou une API interne) dans l'attribut
`data-endpoint` de la balise `<form>` :

```html
<form id="contact-form" novalidate
      data-endpoint="https://formspree.io/f/VOTRE_IDENTIFIANT"
      data-mailto="mailto:contact@primeadvisors-sb.com"
      data-public-email="corporate@primeadvisors-sb.com">
```

Dès que `data-endpoint` est renseigné, la demande part en `POST` JSON et le
visiteur voit un message de confirmation ou d'erreur. Le repli par e-mail reste
actif si l'envoi échoue.

Les liens « Échanger avec un expert » des pages Expertises et Solutions
pré-sélectionnent l'objet du formulaire via l'URL
(`contact.html?objet=gouvernance`).

---

## 4. Ajouter une référence

Les fiches sont du HTML réel : elles sont indexées par les moteurs de recherche
et s'affichent même si JavaScript est désactivé.

1. Ouvrir `nos-references.html`.
2. Copier le modèle ci-dessous **à l'intérieur** de `<div id="ref-list">`.
3. Supprimer le bloc `empty-state` dès la première fiche publiée.

```html
<article class="ref-card reveal" data-secteur="Secteur d'activité">
  <p class="ref-card__sector">Secteur d'activité</p>
  <h3>Nom du client</h3>
  <p>Nature de la mission réalisée.</p>
  <p class="ref-card__year">2025</p>
</article>
```

Les **filtres par secteur se construisent automatiquement** à partir de
l'attribut `data-secteur` dès qu'au moins deux secteurs distincts sont publiés.
Aucune autre modification n'est nécessaire.

> **Règle éditoriale.** Ne publier que des références validées par le client.
> Ne jamais renseigner de résultats, de chiffres, de témoignages ou de
> certifications sans autorisation écrite.

---

## 5. Système de design

Toutes les valeurs sont centralisées dans les variables CSS en haut de
`assets/css/style.css`. Modifier une variable met à jour tout le site.

**Palette de marque**

| Rôle | Valeur |
|---|---|
| Bleu marine profond | `#0A1138` |
| Or / bronze | `#B98344` |
| Blanc | `#FFFFFF` |
| Gris clair | `#F5F5F3` |
| Gris foncé | `#222222` |

**Une règle à respecter lors des évolutions :** l'or de marque `#B98344`
n'atteint que **3.3:1** sur fond blanc. Il est donc réservé aux filets, aux
grands chiffres (≥ 24 px) et à tous les accents sur fond marine. Pour le texte
de petite taille sur fond clair, utiliser `--gold-600` (`#8F6129`), qui atteint
5.4:1 sur blanc et 4.9:1 sur gris clair. Ne pas remplacer l'un par l'autre.

**Typographie.** EB Garamond (titres) et Inter (textes), chargées depuis
Google Fonts. Pour un site totalement autonome, héberger les fichiers de police
et remplacer le `<link>` par un `@font-face`.

---

## 5 bis. Imagerie de marque

Les visuels de marque du site sont **générés** par un script : courbes de
niveau topographiques, ondes de rayonnement depuis Abidjan et trame
structurelle qui se déforme : un vocabulaire graphique qui traduit la
promesse « vers les sommets ». Les quatre cartes du carrousel d'expertises
sont, elles, des photographies fournies par PRIME (voir plus bas).

```bash
python assets/tools/generate-visuals.py
```

**Le cavalier dans le relief.** La composition `img-compagnie.webp` porte la
silhouette du cavalier du logo, non pas posée dessus mais inscrite dans le
relief : les courbes de niveau s'apaisent à l'intérieur de la forme, qu'un
liseré fin vient cerner. C'est ce contraste de densité qui la fait
apparaître, sans qu'aucun tracé ne la dessine.

Elle occupe presque toute la hauteur du cadre et **déborde volontairement du
bord droit** : coupée par le cadre, elle le tient au lieu d'y flotter.

Réglages, dans l'appel à `knight_mask` de `img_compagnie` :

| Paramètre | Valeur | Effet |
|---|---|---|
| `height_frac` | `0.98` | Hauteur, en fraction de l'image |
| `cx` | `0.84` | Centre horizontal ; au-delà de 0,65 la forme déborde à droite. À 0,84, 29 % de la silhouette est coupée par le cadre |
| `cy` | `0.50` | Centre vertical |

Trois coefficients suivent, pour la présence : apaisement des courbes
(`0.38`), souffle d'or (`0.050`) et liseré (`0.24`). **Ils dépendent de la
taille** : les valeurs qui convenaient à une petite silhouette
(`0.55` / `0.085` / `0.22`) donnaient un aplat pâle une fois la forme
agrandie. En cas de nouvelle mise à l'échelle, les réviser ensemble.

| Fichier | Rôle |
|---|---|
| `img-compagnie.webp` | Massif et ligne de crête, avec le cavalier en filigrane. Portrait de l'accueil, bandeau des références |
| `img-rayonnement.webp` | Fond marine et texture topographique, sous les ondes animées |
| `img-expertise.webp` | Photographie duotonée sous la trame structurelle. Bandeau de la page Expertises et bandeau « Notre promesse » de l'accueil |
| `img-partenaire.webp` | Poignée de main devant un tableau blanc. Bandeau de la page La compagnie |
| `img-solutions.webp` | Photographie de plan de travail, ralliée au marine. Bandeau de la page Solutions |
| `img-methode.webp` | Engrenages mis en prise, duotone marine sur gris clair. Bloc « cadrage » de la page Solutions |
| `motif-topo.webp` | Texture de courbes de niveau, en fond de section marine |
| `motif-knight.png` | Filigrane du cavalier, extrait du logo officiel |

**Bandeau Contact : un visage sous les ondes.** Le fond de ce bandeau
attend une photographie déposée sous le nom `images/contact-bg.jpg` (ou
`.jpeg`/`.png`). Le script la recadre, la duotone plus clair que le bandeau
Expertises — cette page est un accueil, un sourire noyé dans le sombre ne
dirait plus rien — et écrit `img-contact.webp`. Les ondes animées passent
par-dessus : la photo est en `z-index: -2`, les ondes en `-1`.

Le sourire de la source fournie est centré, or le texte du bandeau occupe la
moitié gauche. Le script resserre donc le cadrage à 82 % de la largeur
(`HERO_CONTACT_ZOOM`) et le cale complètement à gauche
(`HERO_CONTACT_FOCUS = 0.41`), ce qui pousse le sujet vers la droite, là où
le voile s'éclaircit. Le voile de cette page est d'ailleurs propre à elle
(`.page-hero--portrait`) : il descend à 0,34 d'opacité à droite au lieu de
0,58, sans quoi le visage disparaîtrait. Mesuré sur le composite, le pire
fond de la zone de texte reste à 13,6:1 en blanc et 7,5:1 pour le texte
atténué. Le duotone est ici en gamma 0,86, donc éclaircissant, à l'inverse
du bandeau Expertises.

**Tant que le fichier est absent, le script écrit la texture
marine d'origine** : la page reste exactement telle qu'elle est aujourd'hui,
sans jamais casser. Il en va de même pour `images/solutions-bg.jpg`,
`images/methode.jpg` et `images/compagnie-bg.jpg`.

**Bandeau La compagnie.** Le titre de la page est « Un partenaire de
confiance pour les décideurs » : la poignée de main en est l'illustration
directe. Même principe de cadrage que le bandeau Contact, le sujet étant
là aussi centré dans la source (`HERO_COMPAGNIE_ZOOM` à 0,78,
`HERO_COMPAGNIE_FOCUS` à 0,422). Ce bandeau portait jusqu'ici la
composition au cavalier, un portrait de 900x1150 étiré en 16/9, dont
les deux tiers de la hauteur étaient rognés.

**Photographie duotonée.** Le bandeau de la page Expertises repose sur une
photographie (`images/expertise-bg.jpg`) projetée sur
la rampe marine vers bronze par la fonction `duotone`. Une photographie
brute jurerait avec une charte aussi serrée : le duotone ne retient que les
valeurs de luminance et les rejoue dans la palette, ce qui neutralise
notamment le rouge vif du sujet. La trame structurelle d'origine est
conservée et vient se poser par-dessus. Source absente, la composition
retombe sur le dégradé seul sans faire échouer le script.

**Un seul gabarit par bloc.** Chaque expertise se lit sur quatre cellules
identiques : filet doré, intitulé en capitales, corps de même graisse. Les
trois colonnes portaient auparavant trois traitements différents (paragraphe
nu, liste à losanges, liste à tirets) et les organisations accompagnées
formaient une enfilade séparée par des points médians ; tout passe désormais
par `.exp-list` et `.exp-tags`.

**Le survol répond partout, selon la même logique.** Le filet doré d'une
colonne ne couvre qu'un sixième de sa largeur au repos et se déroule
entièrement au survol ; un item de liste avance de 5 px pendant que son
marqueur s'allonge ; le cadre doré d'un visuel se rapproche de l'image
pendant qu'elle zoome, et le numéro monte avec lui. Les jetons, eux, ne
changent que de teinte : ce ne sont pas des liens, rien ne doit laisser
croire qu'on peut cliquer. Tout repose sur `transform` et la couleur, donc
rien ne déplace la mise en page.

### Deux familles de visuels pour les expertises

Les quatre expertises sont illustrées deux fois, par des photographies
différentes. Il ne faut pas les confondre :

| Où | Fichiers | Sujet |
|---|---|---|
| Carrousel de l'accueil | `expertise-*.webp` | Échiquier, silhouettes reliées, ampoule, clavier |
| Page Nos expertises | `page-*.webp` | Dame d'échecs, mains sur un rapport, pièces ascendantes, écrans de données |

L'accueil annonce, la page montre. Sur la page, chaque bloc s'ouvre sur sa
photographie, le côté alternant d'un bloc à l'autre, l'intitulé aligné sur
le bord supérieur de l'image et **le numéro posé sur le visuel** plutôt qu'à
côté du titre : il ancre l'image, libère l'intitulé et évite de compter deux
fois.

Les quatre photographies arrivent de sources et de températures très
différentes, du bleu profond au blanc froid. Un étalonnage commun
(désaturation à 0,82, contraste à 1,05) les rallie ; sans lui elles ne
feraient pas famille sur une page blanche. Cette désaturation calme aussi
la flèche verte du visuel économique, étrangère à la palette, sans effacer
le signal de croissance qu'elle porte.

> **Attention au sens de l'image.** Une première photographie proposée pour
> le développement économique montrait des piles de pièces *décroissantes*
> et une courbe rouge en chute : le contraire du propos. Elle a été écartée
> au profit d'une version ascendante. Vérifier ce que dit l'image, pas
> seulement ce qu'elle montre.

### Photographies d'expertise

Les quatre cartes du carrousel sont des **photographies fournies par PRIME**,
et non des visuels générés. Le script les recadre au carré, les étalonne
légèrement pour qu'elles tiennent ensemble malgré leurs origines
différentes, et les optimise.

| Source attendue | Sortie | Sujet |
|---|---|---|
| `strategie.jpg` | `expertise-conseil.webp` | Échiquier, la dame dorée face au roi |
| `gouvernance.jpg` | `expertise-gouvernance.webp` | Silhouettes reliées autour d'un nœud central |
| `economie.jpg` | `expertise-developpement.webp` | Ampoule renfermant une courbe ascendante |
| `inovation.jpg` | `expertise-innovation.webp` | Mains sur un clavier, flux de données |
| `contact-bg.jpg` | `img-contact.webp` | Sourire en gros plan, bandeau Contact |
| `solutions-bg.jpg` | `img-solutions.webp` | Mains au clavier sous une surimpression de données |
| `methode.jpg` | `img-methode.webp` | Engrenages assemblés à la main |
| `compagnie-bg.jpg` | `img-partenaire.webp` | Poignée de main devant un tableau blanc |

Les originaux vivent dans `images/`, **hors du suivi Git** (plusieurs
mégaoctets chacun) :
seules les sorties optimisées le sont. Pour les régénérer ou changer de
photo, déposer les fichiers dans le dossier `images/` du projet (fouillé en
premier, puis `~/Downloads` en secours), ajuster si besoin le
cadrage (chaque entrée du dictionnaire `PHOTOS` porte un centre horizontal,
un centre vertical et un facteur de zoom), puis relancer la commande. Si les
sources sont absentes, le script conserve les images existantes au lieu
d'échouer.

> **Licence.** Ces photographies doivent être couvertes par une licence
> commerciale au nom de PRIME ADVISORS SB, Inc. Conserver les justificatifs
> d'achat avec les fichiers originaux.

**Le titre n'est pas incrusté dans l'image.** Il est posé en HTML par-dessus
un voile dégradé (`.coverflow__media::after`), ce qui le garde net à toutes
les densités d'écran, sélectionnable, traduisible et lisible par les lecteurs
d'écran. Le voile est calibré pour rester conforme même au-dessus d'une photo
sur fond blanc : mesuré sur les pixels composités, le titre atteint 17,6:1 au
minimum et le numéro doré 6,0:1. La description reste sous le carrousel.

Modifier les couleurs, les dimensions ou la densité des tracés en haut du
script, puis relancer la commande : les fichiers sont réécrits sur place.

**Carrousel des expertises.** La section « Nos expertises » de l'accueil
utilise un carrousel coverflow écrit en JavaScript natif (module 3 quater de
`assets/js/main.js`) : rotation en perspective, recul en profondeur, inertie
au lâcher et bouclage sans clonage de nœuds. Il se pilote à la souris, au
doigt, au clavier (flèches gauche/droite), par les deux boutons latéraux ou
par les pastilles. **Sans JavaScript, la piste retombe sur une grille de
quatre vignettes légendées** : le contenu et les liens restent accessibles et
indexables. Pour ajouter ou retirer une expertise, ajouter ou retirer une
`<figure class="coverflow__card">` : pastilles et légendes se construisent
automatiquement à partir des cartes présentes.

**Défilement automatique.** Le carrousel avance seul toutes les 6 secondes
(`AUTOPLAY_MS` dans le module). Trois règles l'encadrent :

- il ne démarre pas si le visiteur a activé « réduire les animations » :
  chaque changement serait alors un saut sec, et la commande de pause est
  masquée puisqu'elle n'aurait rien à piloter ;
- il se **suspend** au survol, dès que le focus entre dans le carrousel,
  quand l'onglet passe en arrière-plan et quand le carrousel sort de
  l'écran : l'état « en lecture » est conservé et reprend tout seul ;
- la moindre action explicite (flèche, pastille, glissé, clavier) l'**arrête**
  définitivement : le visiteur a pris la main. Le bouton pause/lecture,
  à gauche des pastilles, permet de le relancer.

Ce bouton n'est pas décoratif : tout contenu qui s'anime seul plus de cinq
secondes doit offrir un moyen de l'arrêter (WCAG 2.2.2, niveau A). Pendant le
défilement automatique, la légende passe en `aria-live="off"`, sans quoi un
lecteur d'écran annoncerait un changement toutes les six secondes ; elle
redevient `polite` dès que le défilement s'arrête, pour les changements
demandés par le visiteur.

**Progression Côte d'Ivoire vers l'international.** Le schéma en quatre
étapes de l'accueil s'anime à l'entrée dans le champ de vision : le trait de
liaison se trace d'Abidjan vers l'international en 1,4 s, puis chaque étape
apparaît dans son sillage, décalée de 0,32 s. Une fois la séquence jouée,
chaque cercle émet une onde en écho au motif de rayonnement, l'impulsion
partant d'Abidjan pour gagner l'international. Comme les ondes des bandeaux,
ce pulse se met en veille hors écran, et sous « animations réduites » le
schéma s'affiche d'emblée complet, sans mouvement.

**Ondes de rayonnement animées.** Le motif des ondes concentriques figurait
autrefois dans le pixel de `img-rayonnement.webp`. Il est désormais vectoriel
(composant `.waves`, présent sur les six pages) : les ondes s'élargissent
réellement depuis Abidjan, en boucle de 11 secondes, cinq anneaux décalés.
Le fichier matriciel ne porte plus que la matière : dégradé, courbes de
niveau, grain.

Trois précautions encadrent ce composant :

- **Plafond d'opacité à 0,38.** Les ondes passent au-dessus du voile
  sombre, donc derrière le texte des bandeaux. À cette valeur, même une onde
  tombant exactement sur un paragraphe laisse 4,5:1 au texte atténué : la
  lisibilité ne dépend pas de l'endroit où l'onde se trouve. Au-delà de 0,45
  elle échouerait, donc ne pas relever ce plafond sans revérifier.
- **Veille hors écran.** Une animation perpétuelle empêche le navigateur de
  se mettre au repos ; les ondes sont gelées quand le bandeau sort du champ
  de vision.
- **Repli figé.** Sans JavaScript comme sous « animations réduites », les
  cinq anneaux se figent à des échelles échelonnées : on retrouve la
  composition statique d'origine plutôt qu'un bandeau vide.

Les autres motifs (massif et lignes de crête, trame structurelle, filigrane
du cavalier) restent matriciels : ils ne représentent pas un mouvement, et
les animer aurait chargé la page sans rien apporter au propos.

**Animations.** La courbe du hero se trace au chargement (barres en cascade,
trajectoire, jalons, point mobile en boucle) ; le reste du site se limite à
des révélations au défilement, un parallaxe très léger et des survols. Tout
est neutralisé si le visiteur a activé « réduire les animations ». Les
révélations disposent d'un filet de sécurité : si l'observateur d'intersection
ne répond pas, l'intégralité du contenu s'affiche au bout de 2,5 s : la page
ne peut jamais rester blanche.

---

## 6. Accessibilité et référencement

Vérifiés sur l'ensemble des pages :

- un seul `<h1>` par page, hiérarchie de titres sans saut de niveau ;
- `lang="fr"`, balise `description`, `canonical` et Open Graph sur chaque page ;
- données structurées `schema.org` (`ProfessionalService`, `ContactPage`) ;
- lien d'évitement, `aria-current` sur l'onglet actif, fil d'Ariane ;
- tous les contrastes de texte conformes WCAG AA ;
- zones tactiles de 44 px minimum, aucun débordement horizontal de 320 px à 1440 px ;
- animations désactivées si `prefers-reduced-motion` est activé ;
- le site reste entièrement lisible et navigable sans JavaScript.

---

## 7. Évolutions prévues

L'architecture est prête à accueillir, sans refonte : Publications, Insights,
Blog, Études, Actualités, Newsletter et espace Carrière.

Pour ajouter une rubrique : dupliquer une page existante, remplacer le contenu
de `<main>`, ajouter l'entrée dans le menu (les six pages partagent le même
bloc `<header>` et `<footer>`) et référencer la page dans `sitemap.xml`.
