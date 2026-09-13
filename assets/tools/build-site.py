#!/usr/bin/env python3
"""
Prépare le dossier à mettre en ligne pour PRIME ADVISORS SB, Inc.

    python assets/tools/build-site.py

Écrit un dossier « dist/ » à la racine du projet. C'est LUI que l'on
téléverse chez l'hébergeur, pas le dossier de travail.

Deux raisons à cela.

1. Le dossier de travail contient des fichiers qui n'ont rien à faire en
   ligne : le document de profil de la compagnie, le guide de maintenance,
   les photographies d'origine de plusieurs mégaoctets, les scripts. Sur un
   hébergement statique, tout fichier présent est un fichier téléchargeable
   par n'importe qui, même s'il n'est lié depuis aucune page.

2. Les commentaires du code servent à celui qui reprend le projet, pas au
   visiteur. Les sources les gardent, la version publiée ne les a pas.

Rien n'est modifié dans le dossier de travail : « dist/ » est reconstruit
de zéro à chaque appel.
"""

import os
import re
import shutil

RACINE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DIST = os.path.join(RACINE, "dist")

# Tout ce qui est publié, et rien d'autre. Liste blanche volontaire : un
# fichier ajouté à la racine ne part pas en ligne sans décision explicite.
PAGES = ["index.html", "la-compagnie.html", "nos-expertises.html",
         "nos-solutions.html", "nos-references.html", "contact.html"]
RACINE_FICHIERS = ["robots.txt", "sitemap.xml"]
DOSSIERS = ["assets/css", "assets/js", "assets/img"]


def nettoyer_html(texte):
    """Retire les commentaires de balisage."""
    texte = re.sub(r"<!--.*?-->", "", texte, flags=re.S)
    texte = re.sub(r"\n[ \t]*\n[ \t]*\n+", "\n\n", texte)
    return texte


def nettoyer_css(texte):
    texte = re.sub(r"/\*.*?\*/", "", texte, flags=re.S)
    texte = re.sub(r"\n[ \t]*\n[ \t]*\n+", "\n\n", texte)
    return texte.strip() + "\n"


def nettoyer_js(texte):
    """Retire les blocs /* */ et les lignes entièrement en commentaire.

    Les commentaires de fin de ligne sont laissés en place : « // » apparaît
    aussi dans « https:// », et distinguer les deux demanderait d'analyser
    le fichier. Le gain ne vaut pas le risque de casser le script."""
    texte = re.sub(r"/\*.*?\*/", "", texte, flags=re.S)
    texte = re.sub(r"^[ \t]*//.*$", "", texte, flags=re.M)
    texte = re.sub(r"\n[ \t]*\n[ \t]*\n+", "\n\n", texte)
    return texte.strip() + "\n"


NETTOYEURS = {".html": nettoyer_html, ".css": nettoyer_css, ".js": nettoyer_js}


def copier(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    nettoyeur = NETTOYEURS.get(os.path.splitext(src)[1].lower())
    if nettoyeur is None:
        shutil.copy2(src, dst)
        return os.path.getsize(src), os.path.getsize(dst)
    with open(src, encoding="utf-8") as f:
        avant = f.read()
    apres = nettoyeur(avant)
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write(apres)
    return len(avant.encode("utf-8")), len(apres.encode("utf-8"))


def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)

    total_avant = total_apres = 0
    fichiers = 0

    for nom in PAGES + RACINE_FICHIERS:
        chemin = os.path.join(RACINE, nom)
        if not os.path.exists(chemin):
            print("  ABSENT : %s" % nom)
            continue
        a, b = copier(chemin, os.path.join(DIST, nom))
        total_avant += a
        total_apres += b
        fichiers += 1
        if a != b:
            print("  %-26s %6d -> %6d o" % (nom, a, b))

    for dossier in DOSSIERS:
        source = os.path.join(RACINE, dossier.replace("/", os.sep))
        if not os.path.isdir(source):
            continue
        for base, _, noms in os.walk(source):
            for nom in noms:
                if nom.startswith("."):
                    continue
                chemin = os.path.join(base, nom)
                relatif = os.path.relpath(chemin, RACINE)
                a, b = copier(chemin, os.path.join(DIST, relatif))
                total_avant += a
                total_apres += b
                fichiers += 1
                if a != b:
                    print("  %-26s %6d -> %6d o" % (relatif.replace(os.sep, "/"), a, b))

    print()
    print("%d fichiers dans dist/  (%d Ko, %d Ko retirés)"
          % (fichiers, total_apres // 1024, (total_avant - total_apres) // 1024))
    print("C'est le contenu de ce dossier qui se téléverse chez l'hébergeur.")


if __name__ == "__main__":
    main()
