# Picture ASCII

[English](../README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | **Español** | [Français](README.fr.md)

Un programa en Python que convierte imágenes en caracteres ASCII.

- Salida de texto ASCII sin formato
- Salida de terminal con los colores RGB de la imagen original
- Exportación PNG normal o en color
- Paletas de caracteres, tamaño de celda, fondo y color de texto configurables
- Fondo transparente y dimensiones PNG personalizadas

## Ejemplos

- [Imagen original](https://github.com/doyeon789/pictureascii/tree/main/example/images/sample.png)
- [Texto ASCII (la proporción puede variar por la fuente de GitHub)](https://github.com/doyeon789/pictureascii/tree/main/example/outputs/sample.txt)
- [Imagen ASCII normal](https://github.com/doyeon789/pictureascii/tree/main/example/outputs/sample_plain.png)
- [Imagen ASCII en color](https://github.com/doyeon789/pictureascii/tree/main/example/outputs/sample_color.png)

## Instalación

Requiere Python 3.10 o posterior.

```bash
pip install pictureascii
```

Para desarrollo local, ejecuta desde la raíz del proyecto:

```bash
python -m pip install -e .
```

## Uso básico

```bash
pascii picture.png
pascii picture.png --width 200
```

`pascii` es el alias corto de `pictureascii`; ambos comandos funcionan igual. El resultado se guarda como `picture.txt` junto a la imagen original.

## Color y exportación PNG

```bash
pictureascii picture.png --color
pictureascii picture.png --save-image
pictureascii picture.png --color --save-image
```

Para la salida en color se recomienda un terminal compatible con color ANSI de 24 bits. El archivo TXT no contiene códigos de color ANSI.

## Personalización

```bash
pictureascii picture.png --chars "@%#*+=-:. "
pictureascii picture.png --cell-width 8 --cell-height 12 --save-image
pictureascii picture.png --background "#101820" --foreground "#F2AA4C" --save-image
pictureascii picture.png --color --transparent --save-image
pictureascii picture.png --image-width 1200 --image-height 800 --save-image
```

La izquierda de la paleta representa las zonas oscuras y la derecha las claras. Los colores aceptan `#RGB` o `#RRGGBB`. Si solo se indica una dimensión PNG, la otra se calcula con la proporción original.

## Opciones

| Opción | Descripción | Predeterminado |
|---|---|---:|
| `image` | Ruta de la imagen de entrada | Obligatorio |
| `-w`, `--width` | Número de columnas de salida | `120` |
| `-o`, `--output` | Ruta del TXT | Nombre original + `.txt` |
| `--ratio` | Corrección de proporción del carácter | `0.5` |
| `--invert`, `--no-invert` | Invierte el brillo de los caracteres | Activado |
| `--color` | Aplica los colores RGB originales | Desactivado |
| `--color-scale` | Multiplicador de brillo del color | `1.0` |
| `--save-image` | Guarda un PNG | Desactivado |
| `--cell-width`, `--cell-height` | Ancho y alto de la celda | `10`, `14` |
| `--chars` | Paleta de caracteres | Integrada |
| `--background`, `--foreground` | Fondo y texto del PNG | Automático |
| `--transparent` | Usa fondo PNG transparente | Desactivado |
| `--image-width`, `--image-height` | Ancho y alto del PNG | Automático |

```bash
pictureascii --help
python -m pictureascii picture.png --color
```

## Desarrollo

```bash
python -m unittest discover -s tests -v
python -m build
python -m twine check dist/*
```
