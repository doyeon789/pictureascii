# Picture ASCII

[English](../README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [Español](README.es.md) | **Français**

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
pascii picture.png
pascii picture.png --width 200
```

`pascii` est l'alias court de `pictureascii` ; les deux commandes fonctionnent de la même manière. Le résultat est enregistré sous `picture.txt` à côté de l'image source.

## Couleur et export PNG

```bash
pictureascii picture.png --color
pictureascii picture.png --save-image
pictureascii picture.png --color --save-image
```

Un terminal compatible avec les couleurs ANSI 24 bits est recommandé. Le fichier TXT ne contient aucun code couleur ANSI.
`--color-scale` nécessite `--color`. Les options propres au PNG nécessitent `--save-image`.

## Ratio des caractères du terminal

`--terminal-ratio` ajuste le ratio des caractères dans le terminal et le fichier TXT. Le nom court existant `--ratio` reste disponible et fonctionne de la même manière.

```bash
pictureascii picture.png --terminal-ratio 0.6
```

Cette option ne contrôle pas les proportions du PNG enregistré. La sortie PNG utilise la taille de cellule configurée.

## Personnalisation

```bash
pictureascii picture.png --chars "@%#*+=-:. "
pictureascii picture.png --cell-width 8 --cell-height 12 --image-font-size 10 --save-image
pictureascii picture.png --background "#101820" --foreground "#F2AA4C" --save-image
pictureascii picture.png --color --transparent --save-image
pictureascii picture.png --image-width 1200 --image-height 800 --save-image
```

La gauche de la palette représente les zones sombres et la droite les zones claires. Les couleurs acceptent les formats `#RGB` et `#RRGGBB`. Si une seule dimension PNG est définie, l'autre est calculée selon le ratio de l'image source.

`--image-font-size` définit la taille de police réellement utilisée dans chaque cellule. Choisissez une valeur adaptée à la cellule pour éviter les caractères rognés ou superposés. `--foreground` ne peut pas être combiné avec `--color`, et `--background` ne peut pas être combiné avec `--transparent`.

## Options

| Option | Description | Valeur par défaut |
|---|---|---:|
| `image` | Chemin de l'image source | Requis |
| `-w`, `--width` | Nombre de colonnes en sortie | `120` |
| `-o`, `--output` | Chemin du fichier TXT | Nom source + `.txt` |
| `--ratio`, `--terminal-ratio` | Correction du ratio pour le terminal et le TXT | `0.5` |
| `--invert`, `--no-invert` | Inverse la luminosité des caractères | Activé |
| `--color` | Applique les couleurs RVB source | Désactivé |
| `--color-scale` | Multiplicateur de luminosité ; nécessite `--color` | `1.0` |
| `--save-image` | Enregistre un PNG | Désactivé |
| `--image-font-size` | Taille de police utilisée dans le PNG | `14` |
| `--cell-width`, `--cell-height` | Largeur et hauteur des cellules | `10`, `14` |
| `--chars` | Palette de caractères | Intégrée |
| `--background` | Arrière-plan PNG ; incompatible avec `--transparent` | Automatique |
| `--foreground` | Texte du PNG simple ; incompatible avec `--color` | Automatique |
| `--transparent` | Fond PNG transparent ; incompatible avec `--background` | Désactivé |
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
