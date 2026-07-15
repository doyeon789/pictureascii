# Picture ASCII

[English](../README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | [Español](README.es.md) | **Français**

Un programme Python qui convertit des images en caractères ASCII.

- Sortie texte ASCII simple
- Sortie terminal avec les couleurs RVB de l'image source
- Export PNG simple ou en couleur
- Palette de caractères, taille des cellules, arrière-plan et couleur du texte configurables
- Arrière-plan transparent et dimensions PNG personnalisées

## Exemples

- [Image source](https://github.com/doyeon789/pictureascii/tree/main/example/images/sample.png)
- [Texte ASCII (le ratio peut varier selon le rendu de la police GitHub)](https://github.com/doyeon789/pictureascii/tree/main/example/outputs/sample.txt)
- [Image ASCII simple](https://github.com/doyeon789/pictureascii/tree/main/example/outputs/sample_plain.png)
- [Image ASCII en couleur](https://github.com/doyeon789/pictureascii/tree/main/example/outputs/sample_color.png)

## Installation

Python 3.10 ou une version ultérieure est requis.

```bash
pip install pictureascii
```

Pour le développement local, exécutez cette commande à la racine du projet :

```bash
python -m pip install -e .
```

## Utilisation de base

```bash
pictureascii picture.png
pictureascii picture.png --width 200
```

Le résultat est enregistré sous `picture.txt` à côté de l'image source.

## Couleur et export PNG

```bash
pictureascii picture.png --color
pictureascii picture.png --save-image
pictureascii picture.png --color --save-image
```

Un terminal compatible avec les couleurs ANSI 24 bits est recommandé. Le fichier TXT ne contient aucun code couleur ANSI.

## Personnalisation

```bash
pictureascii picture.png --chars "@%#*+=-:. "
pictureascii picture.png --cell-width 8 --cell-height 12 --save-image
pictureascii picture.png --background "#101820" --foreground "#F2AA4C" --save-image
pictureascii picture.png --color --transparent --save-image
pictureascii picture.png --image-width 1200 --image-height 800 --save-image
```

La gauche de la palette représente les zones sombres et la droite les zones claires. Les couleurs acceptent les formats `#RGB` et `#RRGGBB`. Si une seule dimension PNG est définie, l'autre est calculée selon le ratio de l'image source.

## Options

| Option | Description | Valeur par défaut |
|---|---|---:|
| `image` | Chemin de l'image source | Requis |
| `-w`, `--width` | Nombre de colonnes en sortie | `120` |
| `-o`, `--output` | Chemin du fichier TXT | Nom source + `.txt` |
| `--ratio` | Correction du ratio des caractères | `0.5` |
| `--invert`, `--no-invert` | Inverse la luminosité des caractères | Activé |
| `--color` | Applique les couleurs RVB source | Désactivé |
| `--color-scale` | Multiplicateur de luminosité | `1.0` |
| `--save-image` | Enregistre un PNG | Désactivé |
| `--cell-width`, `--cell-height` | Largeur et hauteur des cellules | `10`, `14` |
| `--chars` | Palette de caractères | Intégrée |
| `--background`, `--foreground` | Arrière-plan et texte du PNG | Automatique |
| `--transparent` | Utilise un fond PNG transparent | Désactivé |
| `--image-width`, `--image-height` | Largeur et hauteur du PNG | Automatique |

```bash
pictureascii --help
python -m pictureascii picture.png --color
```

## Développement

```bash
python -m unittest discover -s tests -v
python -m build
python -m twine check dist/*
```
