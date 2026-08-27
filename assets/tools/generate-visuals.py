#!/usr/bin/env python3
"""
Génère l'imagerie de marque de PRIME ADVISORS SB, Inc.

Toutes les images du site sont produites par ce script : aucune banque
d'images, aucun visuel sous licence tierce. Le vocabulaire graphique
reprend la promesse de marque, « vers les sommets », sous forme de
courbes de niveau topographiques, d'ondes de rayonnement et de trames
structurelles, dans la palette officielle.

Régénérer après toute modification :
    python assets/tools/generate-visuals.py

Dépendances : numpy, Pillow.
"""

import os
import numpy as np
from PIL import Image

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "img")
OUT = os.path.normpath(OUT)

NAVY     = np.array([10, 17, 56], float)
NAVY_700 = np.array([20, 28, 74], float)
NAVY_900 = np.array([6, 11, 36], float)
GOLD     = np.array([185, 131, 68], float)
GOLD_400 = np.array([207, 160, 106], float)


# --------------------------------------------------------------------------
# Primitives
# --------------------------------------------------------------------------
def value_noise(w, h, octaves=4, seed=0, base=(6, 4)):
    """Bruit de valeur lissé, sommé sur plusieurs octaves (0..1)."""
    rng = np.random.default_rng(seed)
    field = np.zeros((h, w), float)
    amp, total = 1.0, 0.0
    gw, gh = base
    for _ in range(octaves):
        grid = rng.random((gh, gw))
        layer = np.asarray(
            Image.fromarray((grid * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC),
            float,
        ) / 255.0
        field += layer * amp
        total += amp
        amp *= 0.5
        gw, gh = gw * 2, gh * 2
    field /= total
    return (field - field.min()) / (np.ptp(field) + 1e-9)


def contour_alpha(field, levels=22, width=1.15, aa=1.0):
    """Courbes de niveau anti-aliasées, d'épaisseur constante à l'écran."""
    f = field * levels
    gy, gx = np.gradient(f)
    grad = np.sqrt(gx ** 2 + gy ** 2) + 1e-6
    frac = f - np.floor(f)
    dist = np.minimum(frac, 1.0 - frac) / grad          # distance en pixels
    return np.clip(1.0 - (dist - width * 0.5) / aa, 0.0, 1.0)


def radial(w, h, cx, cy):
    """Distance radiale normalisée depuis un point exprimé en fraction."""
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    return np.sqrt((xx - cx * w) ** 2 + (yy - cy * h) ** 2)


def linear_gradient(w, h, top, bottom, angle_x=0.0):
    """Dégradé linéaire vertical, avec dérive horizontale optionnelle."""
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    t = yy / max(h - 1, 1) + angle_x * (xx / max(w - 1, 1) - 0.5)
    t = np.clip(t, 0, 1)[..., None]
    return top * (1 - t) + bottom * t


def add_grain(rgb, amount=5.0, seed=7):
    rng = np.random.default_rng(seed)
    noise = rng.normal(0.0, amount, rgb.shape[:2])[..., None]
    return np.clip(rgb + noise, 0, 255)


def knight_mask(w, h, height_frac, cx, cy):
    """Silhouette du cavalier du logo, en masque flottant (0..1).

    Sert à moduler une composition existante plutôt qu'à dessiner le logo :
    la marque s'inscrit dans la matière au lieu d'y être apposée."""
    src = Image.open(os.path.join(OUT, "logo-dark.png")).convert("RGBA").crop((0, 0, 215, 342))
    kh = max(1, int(h * height_frac))
    kw = max(1, int(kh * src.width / src.height))
    alpha = src.resize((kw, kh), Image.LANCZOS).split()[3]
    canvas = Image.new("L", (w, h), 0)
    canvas.paste(alpha, (int(cx * w - kw / 2), int(cy * h - kh / 2)))
    return np.asarray(canvas, float) / 255.0


def save(rgb, name, alpha=None, quality=88):
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    if alpha is None:
        img = Image.fromarray(rgb, "RGB")
    else:
        a = np.clip(alpha * 255, 0, 255).astype(np.uint8)
        img = Image.fromarray(np.dstack([rgb, a]), "RGBA")
    path = os.path.join(OUT, name)
    if name.endswith(".webp"):
        img.save(path, quality=quality, method=6)
    else:
        img.save(path, optimize=True)
    print("  %-28s %s  %d Ko" % (name, img.size, os.path.getsize(path) // 1024))


# --------------------------------------------------------------------------
# 1. Motif topographique réutilisable (or sur fond transparent)
# --------------------------------------------------------------------------
def motif_topo():
    w, h = 800, 500
    field = value_noise(w, h, octaves=4, seed=11, base=(5, 3))
    a = contour_alpha(field, levels=24, width=1.0, aa=1.1)
    # atténuation vers les bords pour un raccord discret
    fade = np.clip(1.0 - radial(w, h, 0.5, 0.5) / (0.78 * w), 0, 1) ** 0.7
    rgb = np.broadcast_to(GOLD, (h, w, 3)).copy()
    # WebP avec canal alpha : ~40 Ko contre ~590 Ko en PNG, pour un rendu
    # identique sur une trame de lignes fines.
    save(rgb, "motif-topo.webp", alpha=a * fade * 0.85, quality=60)


# --------------------------------------------------------------------------
# 2. Composition « La compagnie », massif et lignes de crête
# --------------------------------------------------------------------------
def img_compagnie():
    w, h = 900, 1150
    rgb = linear_gradient(w, h, NAVY_700, NAVY_900, angle_x=0.25)

    # halo doré en haut à droite, le « sommet »
    glow = np.clip(1.0 - radial(w, h, 0.78, 0.16) / (0.85 * w), 0, 1) ** 2.4
    rgb += GOLD * glow[..., None] * 0.55

    # Cavalier du logo, inscrit DANS le relief et non posé dessus : à
    # l'intérieur de la silhouette, l'altitude est décalée d'une demi-
    # équidistance, si bien que les courbes de niveau se rompent le long du
    # contour. Une carte lit ce décrochement comme une faille ; l'œil y
    # reconnaît la forme sans qu'aucun trait ne la dessine. Placé au-dessus
    # de l'horizon, donc loin du bandeau de légende.
    # Volontairement débordant : la silhouette est coupée par le bord droit,
    # ce qui la fait tenir le cadre au lieu d'y flotter.
    knight = knight_mask(w, h, height_frac=0.98, cx=0.84, cy=0.50)

    # courbes de niveau, plus serrées vers le sommet
    field = value_noise(w, h, octaves=5, seed=23, base=(4, 5))
    peak = np.clip(1.0 - radial(w, h, 0.74, 0.20) / (0.95 * w), 0, 1)
    a = contour_alpha(field * 0.75 + peak * 0.45, levels=30, width=1.0, aa=1.15)
    strength = (0.16 + 0.62 * peak)[..., None]
    # Le relief s'apaise à l'intérieur de la silhouette : c'est ce contraste
    # de densité, et non un tracé, qui fait apparaître la forme.
    # Coefficients volontairement bas : la silhouette couvre désormais la
    # majeure partie du cadre, et les valeurs qui convenaient à une petite
    # forme en feraient ici un aplat pâle. Grand ne doit pas vouloir dire
    # appuyé.
    strength = strength * (1 - (knight * 0.38)[..., None])
    rgb = rgb * (1 - a[..., None] * strength) + GOLD_400 * a[..., None] * strength

    # Souffle d'or dans la silhouette, liseré fin sur son arête.
    gy, gx = np.gradient(knight)
    edge = np.clip(np.sqrt(gx ** 2 + gy ** 2) * 3.0, 0, 1)
    rgb += GOLD * (knight * 0.050)[..., None]
    rgb += GOLD_400 * (edge * 0.24)[..., None]

    # horizon : un filet net qui structure la composition
    for y, alpha in ((int(h * 0.615), 0.85), (int(h * 0.63), 0.28)):
        rgb[y:y + 1] = rgb[y:y + 1] * (1 - alpha) + GOLD * alpha

    save(add_grain(rgb, 4.0), "img-compagnie.webp", quality=78)


# --------------------------------------------------------------------------
# 3. Fond « Rayonnement », dégradé marine et texture topographique
#
#    Les ondes et le foyer ne sont plus incrustés ici : ils sont tracés en
#    SVG par-dessus (composant .waves), pour rayonner réellement depuis
#    Abidjan plutôt que d'être figés dans le pixel. Ce fichier ne porte
#    donc plus que la matière : dégradé, courbes de niveau et grain.
# --------------------------------------------------------------------------
def img_rayonnement():
    w, h = 1400, 790
    rgb = linear_gradient(w, h, NAVY_700, NAVY_900, angle_x=-0.2)

    # Texture un peu plus présente : elle porte désormais l'image à elle seule.
    field = value_noise(w, h, octaves=4, seed=41, base=(6, 4))
    a_topo = contour_alpha(field, levels=20, width=0.9, aa=1.2)
    rgb = rgb * (1 - a_topo[..., None] * 0.13) + GOLD * a_topo[..., None] * 0.13

    save(add_grain(rgb, 4.0), "img-rayonnement.webp", quality=80)


def duotone(img, dark, light, gamma=1.0):
    """Projette une photographie sur une rampe à deux couleurs.

    Une photographie brute jure avec une charte serrée : ici, le rouge vif
    du cœur n'a aucune place à côté du marine et de l'or. Le duotone ne
    conserve que les valeurs de luminance et les rejoue sur la rampe de la
    marque, ce qui rallie n'importe quelle image à la palette."""
    a = np.asarray(img.convert("RGB"), float) / 255.0
    lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    lum = np.clip(lum, 0, 1) ** gamma
    return dark + (light - dark) * lum[..., None]


# --------------------------------------------------------------------------
# 4. Composition « Expertises » : photographie duotonée sous la trame
#
#    La trame structurelle qui s'y trouvait est conservée telle quelle ;
#    la photographie vient s'ajouter dessous, ralliée à la palette.
#    Source attendue dans PHOTOS_SRC. Absente, la composition retombe sur
#    le dégradé d'origine et le script n'échoue pas.
# --------------------------------------------------------------------------
HERO_EXPERTISE = ("expertise-bg.jpg", "une exigence.jpg")

# --------------------------------------------------------------------------
# 4 bis. Fond du bandeau Contact : un visage, sous les ondes animées
#
#    Le sujet est placé à droite, le texte du bandeau occupant la gauche.
#    Le duotone est ici plus clair que sur le bandeau Expertises : le propos
#    de cette page est un accueil, et un sourire noyé dans le sombre ne
#    dirait plus rien.
#
#    Source absente : on retombe sur la texture marine, soit exactement le
#    rendu actuel. La page n'est jamais cassée par un fichier manquant.
# --------------------------------------------------------------------------
HERO_CONTACT = ("contact-bg.jpg", "contact-bg.jpeg", "contact-bg.png")
# Le sourire est centré dans la source et le texte du bandeau occupe la
# moitié gauche : on resserre le cadrage et on le cale complètement à
# gauche, ce qui pousse le sujet vers la droite, là où le voile s'éclaircit.
HERO_CONTACT_ZOOM  = 0.82      # largeur retenue, en fraction de la source
HERO_CONTACT_FOCUS = 0.41      # centre horizontal du recadrage, 0 = gauche
HERO_CONTACT_CY    = 0.48      # centre vertical


def img_contact():
    w, h = 1400, 790
    photo = trouver_photo(*HERO_CONTACT)

    if not photo:
        print("  photo de bandeau Contact absente : texture marine seule")
        rgb = linear_gradient(w, h, NAVY_700, NAVY_900, angle_x=-0.2)
        field = value_noise(w, h, octaves=4, seed=41, base=(6, 4))
        a = contour_alpha(field, levels=20, width=0.9, aa=1.2)
        rgb = rgb * (1 - a[..., None] * 0.13) + GOLD * a[..., None] * 0.13
        save(add_grain(rgb, 4.0), "img-contact.webp", quality=80)
        return

    src = Image.open(photo).convert("RGB")
    sw, sh = src.size
    target = w / h
    nw = int(sw * HERO_CONTACT_ZOOM)
    nh = int(nw / target)
    if nh > sh:
        nh = sh
        nw = int(nh * target)
    x = max(0, min(sw - nw, int(HERO_CONTACT_FOCUS * sw - nw / 2)))
    y = max(0, min(sh - nh, int(HERO_CONTACT_CY * sh - nh / 2)))
    src = src.crop((x, y, x + nw, y + nh)).resize((w, h), Image.LANCZOS)

    # Duotone clair, à l'inverse du bandeau Expertises : gamma inférieur à 1
    # pour relever les demi-teintes, et un tiers seulement de marine ajouté.
    # Le voile CSS du bandeau assombrit déjà l'image de 60 à 95 % ; un
    # duotone sombre par-dessus n'en laisserait rien voir.
    rgb = duotone(src, NAVY_900, GOLD_400, gamma=0.86)
    rgb = rgb * 0.90 + linear_gradient(w, h, NAVY, NAVY_900, angle_x=0.18) * 0.10
    save(add_grain(rgb, 3.5), "img-contact.webp", quality=82)


# --------------------------------------------------------------------------
# 4 ter. Fond du bandeau « Nos solutions » : le geste opérationnel
#
#    La photographie source est un plan rapproché de mains au clavier sous
#    une surimpression de données. Elle est déjà chaude et sombre, donc
#    proche de la charte ; le duotone reste léger pour ne pas effacer les
#    verts et cyans des courbes, qui font tout l'intérêt de l'image, mais
#    suffisant pour la rallier au marine.
#
#    Le voile CSS du bandeau couvre ensuite la gauche à 96 % : le recadrage
#    est décalé à droite pour que le sujet tombe dans la zone claire.
# --------------------------------------------------------------------------
HERO_SOLUTIONS = ("solutions-bg.jpg", "solutions-bg.jpeg", "solutions-bg.png")
HERO_SOLUTIONS_FOCUS = 0.56


def img_solutions():
    w, h = 1400, 790
    photo = trouver_photo(*HERO_SOLUTIONS)

    if not photo:
        print("  photo de bandeau Solutions absente : texture marine seule")
        rgb = linear_gradient(w, h, NAVY_700, NAVY_900, angle_x=-0.2)
        field = value_noise(w, h, octaves=4, seed=63, base=(6, 4))
        a = contour_alpha(field, levels=20, width=0.9, aa=1.2)
        rgb = rgb * (1 - a[..., None] * 0.13) + GOLD * a[..., None] * 0.13
        save(add_grain(rgb, 4.0), "img-solutions.webp", quality=80)
        return

    src = Image.open(photo).convert("RGB")
    sw, sh = src.size
    target = w / h
    if sw / sh > target:
        nw = int(sh * target)
        x = max(0, min(sw - nw, int(HERO_SOLUTIONS_FOCUS * sw - nw / 2)))
        src = src.crop((x, 0, x + nw, sh))
    else:
        nh = int(sw / target)
        y = max(0, min(sh - nh, int(0.50 * sh - nh / 2)))
        src = src.crop((0, y, sw, y + nh))
    src = src.resize((w, h), Image.LANCZOS)

    # 62 % de photographie, 38 % de duotone : les teintes d'origine restent
    # lisibles, mais l'ensemble bascule dans la gamme de la marque.
    a = np.asarray(src, float)
    rgb = a * 0.62 + duotone(src, NAVY_900, GOLD_400, gamma=1.30) * 0.38
    rgb = rgb * 0.88 + linear_gradient(w, h, NAVY, NAVY_900, angle_x=0.18) * 0.12
    save(add_grain(rgb, 3.5), "img-solutions.webp", quality=80)


# --------------------------------------------------------------------------
# 4 quinquies. Fond du bandeau « La compagnie » : la poignée de main
#
#    Le titre de la page est « Un partenaire de confiance pour les
#    décideurs » : la poignée de main en est l'illustration directe. Elle
#    est centrée dans la source, donc sous la colonne de texte ; le cadrage
#    est resserré à 70 % et calé à gauche pour la faire glisser vers la
#    droite, dans la partie claire du voile.
#
#    Le bandeau portait jusqu'ici la composition au cavalier, un format
#    portrait de 900x1150 étiré en 16/9 : elle reste en place sur l'accueil
#    et sur le bandeau des références, où son cadrage est respecté.
# --------------------------------------------------------------------------
HERO_COMPAGNIE = ("compagnie-bg.jpg", "compagnie-bg.jpeg", "compagnie-bg.png")
HERO_COMPAGNIE_ZOOM  = 0.78
HERO_COMPAGNIE_FOCUS = 0.422
HERO_COMPAGNIE_CY    = 0.545


def img_partenaire():
    w, h = 1400, 790
    photo = trouver_photo(*HERO_COMPAGNIE)
    if not photo:
        print("  photo de bandeau Compagnie absente : ignorée")
        return

    src = Image.open(photo).convert("RGB")
    sw, sh = src.size
    target = w / h
    nw = int(sw * HERO_COMPAGNIE_ZOOM)
    nh = int(nw / target)
    if nh > sh:
        nh = sh
        nw = int(nh * target)
    x = max(0, min(sw - nw, int(HERO_COMPAGNIE_FOCUS * sw - nw / 2)))
    y = max(0, min(sh - nh, int(HERO_COMPAGNIE_CY * sh - nh / 2)))
    src = src.crop((x, y, x + nw, y + nh)).resize((w, h), Image.LANCZOS)

    # Photographie plutôt froide et grise : le duotone y pèse plus lourd que
    # sur le bandeau Solutions, sans quoi le tableau blanc du fond tirerait
    # l'ensemble vers un gris d'écran de bureau, étranger à la charte.
    a = np.asarray(src, float)
    rgb = a * 0.52 + duotone(src, NAVY_900, GOLD_400, gamma=1.10) * 0.48
    rgb = rgb * 0.88 + linear_gradient(w, h, NAVY, NAVY_900, angle_x=0.18) * 0.12
    save(add_grain(rgb, 3.5), "img-partenaire.webp", quality=80)


# --------------------------------------------------------------------------
# 4 quater. Illustration « cadrage » : des engrenages assemblés à la main
#
#    Image en niveaux de gris sur fond quasi blanc. Laissée telle quelle,
#    elle poserait un rectangle noir et blanc au milieu d'une page marine
#    et or. Le duotone la rejoue du marine profond vers le gris clair de la
#    charte, si bien que le fond de l'image se confond avec le fond de la
#    page ; une pointe d'or est réintroduite dans les demi-teintes pour
#    éviter le rendu entièrement froid.
# --------------------------------------------------------------------------
ILLUSTRATION_METHODE = ("methode.jpg", "methode.jpeg", "methode.png")
LIGHT = np.array([245, 245, 243], float)


def img_methode():
    w, h = 1100, 880
    photo = trouver_photo(*ILLUSTRATION_METHODE)
    if not photo:
        print("  illustration « cadrage » absente : ignorée")
        return

    src = Image.open(photo).convert("RGB")
    sw, sh = src.size
    target = w / h
    if sw / sh > target:
        nw = int(sh * target)
        x = max(0, min(sw - nw, int(0.50 * sw - nw / 2)))
        src = src.crop((x, 0, x + nw, sh))
    else:
        nh = int(sw / target)
        y = max(0, min(sh - nh, int(0.46 * sh - nh / 2)))
        src = src.crop((0, y, sw, y + nh))
    src = src.resize((w, h), Image.LANCZOS)

    lum = np.asarray(src.convert("L"), float) / 255.0
    rgb = duotone(src, NAVY_900, LIGHT, gamma=0.92)
    # Cloche centrée sur les demi-teintes : seuls les gris intermédiaires,
    # c'est-à-dire les arêtes des engrenages, prennent la teinte or.
    cloche = np.exp(-((lum - 0.52) ** 2) / (2 * 0.16 ** 2))[..., None]
    rgb = rgb * (1 - cloche * 0.16) + GOLD_400 * cloche * 0.16
    save(add_grain(rgb, 2.5), "img-methode.webp", quality=82)


def img_expertise():
    w, h = 1400, 790

    photo = trouver_photo(*HERO_EXPERTISE)
    if photo:
        src = Image.open(photo)
        sw, sh = src.size
        # recadrage « cover » centré sur le cadre du bandeau
        target = w / h
        if sw / sh > target:
            nw = int(sh * target); src = src.crop(((sw - nw) // 2, 0, (sw - nw) // 2 + nw, sh))
        else:
            nh = int(sw / target); src = src.crop((0, (sh - nh) // 2, sw, (sh - nh) // 2 + nh))
        src = src.resize((w, h), Image.LANCZOS)
        # gamma > 1 : on assombrit les demi-teintes, le bandeau reste un fond
        # duotone rend déjà des valeurs 0-255 : les couleurs de rampe le sont.
        # gamma élevé et forte part de marine : ce bandeau porte du texte,
        # il doit rester un fond et non une illustration.
        rgb = duotone(src, NAVY_900, GOLD, gamma=1.85)
        rgb = rgb * 0.72 + linear_gradient(w, h, NAVY, NAVY_900, angle_x=0.18) * 0.28
    else:
        print("  photo de bandeau absente : trame seule pour img-expertise")
        rgb = linear_gradient(w, h, NAVY, NAVY_900, angle_x=0.18)

    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    warp = value_noise(w, h, octaves=3, seed=57, base=(4, 3))
    amp = (xx / w) ** 2.1                                # trame régulière à gauche, déformée à droite

    # verticales
    fx = (xx / 66.0) + warp * 5.4 * amp
    gyx, gxx = np.gradient(fx)
    gradx = np.sqrt(gxx ** 2 + gyx ** 2) + 1e-6
    fr = fx - np.floor(fx)
    av = np.clip(1.0 - (np.minimum(fr, 1 - fr) / gradx - 0.55) / 1.0, 0, 1)

    # horizontales
    fy = (yy / 66.0) + warp * 3.0 * amp
    gyy, gxy = np.gradient(fy)
    grady = np.sqrt(gxy ** 2 + gyy ** 2) + 1e-6
    fr2 = fy - np.floor(fy)
    ah = np.clip(1.0 - (np.minimum(fr2, 1 - fr2) / grady - 0.5) / 1.0, 0, 1)

    a = np.clip(av * 0.85 + ah * 0.45, 0, 1) * (0.20 + 0.62 * amp)
    rgb = rgb * (1 - a[..., None]) + GOLD_400 * a[..., None]

    glow = np.clip(1.0 - radial(w, h, 0.88, 0.5) / (0.62 * w), 0, 1) ** 2.2
    rgb += GOLD * glow[..., None] * 0.35

    save(add_grain(rgb, 3.5), "img-expertise.webp", quality=80)


# --------------------------------------------------------------------------
# 5. Filigrane cavalier, tiré du logo officiel
# --------------------------------------------------------------------------
def pattern_knight():
    src = os.path.join(OUT, "logo-dark.png")
    knight = Image.open(src).convert("RGBA").crop((0, 0, 215, 342))
    knight = knight.resize((430, 684), Image.LANCZOS)
    gold = Image.new("RGBA", knight.size, tuple(GOLD.astype(int)) + (255,))
    gold.putalpha(knight.split()[3])
    gold.save(os.path.join(OUT, "motif-knight.png"), optimize=True)
    print("  %-28s %s  %d Ko" % ("motif-knight.png", gold.size,
          os.path.getsize(os.path.join(OUT, "motif-knight.png")) // 1024))


# --------------------------------------------------------------------------
# 6. Photographies d'expertise : recadrage carré et optimisation
#
#    Les originaux (plusieurs mégaoctets chacun) ne sont pas versionnés :
#    seules les sorties optimisées le sont. Poser les quatre fichiers dans
#    PHOTOS_SRC puis relancer le script pour les régénérer.
#
#    Le titre n'est PAS incrusté dans l'image : il est posé en HTML sur un
#    voile dégradé (voir .coverflow__card::after). Le texte reste ainsi
#    sélectionnable, traduisible, lisible par les lecteurs d'écran, et net
#    à toutes les densités d'écran.
# --------------------------------------------------------------------------
# Emplacements fouillés dans l'ordre pour trouver les photographies sources.
# Le dossier images/ du projet vient en premier : un chemin relatif au dépôt
# fonctionne sur n'importe quelle machine, là où ~/Downloads ne vaut que pour
# le poste où les fichiers ont été téléchargés.
PHOTOS_DIRS = [
    os.path.normpath(os.path.join(OUT, "..", "..", "images")),
    os.path.join(os.path.expanduser("~"), "Downloads"),
]
PHOTOS_SRC = PHOTOS_DIRS[0]


def trouver_photo(*noms):
    """Premier fichier trouvé parmi les noms donnés, dans les dossiers connus."""
    for dossier in PHOTOS_DIRS:
        for nom in noms:
            chemin = os.path.join(dossier, nom)
            if os.path.exists(chemin):
                return chemin
    return None

# fichier source -> (sortie, centre horizontal, centre vertical, zoom)
PHOTOS = {
    "strategie.jpg":   ("expertise-conseil.webp",       0.56, 0.50, 1.00),
    "gouvernance.jpg": ("expertise-gouvernance.webp",   0.50, 0.50, 1.00),
    "economie.jpg":    ("expertise-developpement.webp", 0.50, 0.46, 0.78),
    "inovation.jpg":   ("expertise-innovation.webp",    0.48, 0.50, 1.00),
}


def expertise_photos(src_dir=PHOTOS_SRC):
    from PIL import ImageEnhance
    trouvees = {n: trouver_photo(n) for n in PHOTOS}
    manquantes = [n for n, c in trouvees.items() if not c]
    if manquantes:
        print("  photographies introuvables : %s" % ", ".join(manquantes))
        print("  (les visuels d'expertise existants sont conservés)")
        return

    for name, (out_name, cx, cy, zoom) in PHOTOS.items():
        im = Image.open(trouvees[name]).convert("RGB")
        w, h = im.size
        side = int(min(w, h) * zoom)
        x = max(0, min(w - side, int(cx * w - side / 2)))
        y = max(0, min(h - side, int(cy * h - side / 2)))
        im = im.crop((x, y, x + side, y + side)).resize((760, 760), Image.LANCZOS)
        # Étalonnage léger : juste assez pour que les quatre photographies,
        # d'origines et de températures différentes, tiennent ensemble.
        im = ImageEnhance.Color(im).enhance(0.90)
        im = ImageEnhance.Contrast(im).enhance(1.06)
        path = os.path.join(OUT, out_name)
        im.save(path, quality=76, method=6)
        print("  %-28s %s  %d Ko" % (out_name, im.size, os.path.getsize(path) // 1024))


# --------------------------------------------------------------------------
# 7. Photographies de la page Expertises
#
#    Quatre photographies distinctes de celles du carrousel : l'accueil
#    annonce, la page montre. Chacune a été choisie pour ce qu'elle dit de
#    l'expertise, pas seulement pour son sujet.
#
#    Un étalonnage commun les rallie : leurs températures d'origine vont du
#    bleu profond au blanc froid, et laissées brutes elles ne feraient pas
#    famille sur une page blanche.
# --------------------------------------------------------------------------
PHOTOS_PAGE = {
    # source -> (sortie, centre horizontal, centre vertical, zoom)
    "stra.jpg":  ("page-conseil.webp",       0.52, 0.52, 1.00),
    "gv.jpg":    ("page-gouvernance.webp",   0.50, 0.55, 1.00),
    "green-arrow-is-going-up-stacks-coins-arranged-bar-graph.jpg":
                 ("page-developpement.webp", 0.56, 0.66, 0.82),
    "innov.jpg": ("page-innovation.webp",    0.58, 0.52, 1.00),
}


def expertise_page_photos():
    from PIL import ImageEnhance
    trouvees = {n: trouver_photo(n) for n in PHOTOS_PAGE}
    manquantes = [n for n, c in trouvees.items() if not c]
    if manquantes:
        print("  photographies de page introuvables : %s" % ", ".join(manquantes))
        print("  (les visuels existants sont conservés)")
        return

    for name, (out_name, cx, cy, zoom) in PHOTOS_PAGE.items():
        im = Image.open(trouvees[name]).convert("RGB")
        w, h = im.size
        side = int(min(w, h) * zoom)
        x = max(0, min(w - side, int(cx * w - side / 2)))
        y = max(0, min(h - side, int(cy * h - side / 2)))
        im = im.crop((x, y, x + side, y + side)).resize((900, 900), Image.LANCZOS)
        # Désaturation légère : elle calme notamment la flèche verte du
        # visuel économique, très étrangère à la palette, sans effacer le
        # signal de croissance qu'elle porte.
        im = ImageEnhance.Color(im).enhance(0.82)
        im = ImageEnhance.Contrast(im).enhance(1.05)
        path = os.path.join(OUT, out_name)
        im.save(path, quality=78, method=6)
        print("  %-28s %s  %d Ko" % (out_name, im.size, os.path.getsize(path) // 1024))


if __name__ == "__main__":
    print("Génération de l'imagerie de marque -> %s" % OUT)
    motif_topo()
    img_compagnie()
    img_rayonnement()
    img_expertise()
    img_contact()
    img_solutions()
    img_partenaire()
    img_methode()
    pattern_knight()
    expertise_photos()
    expertise_page_photos()
    print("Terminé.")
