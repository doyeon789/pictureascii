# Picture ASCII

[English](../README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | **Español** | [Français](README.fr.md)

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
`--color-scale` requiere `--color`. Las opciones específicas de PNG requieren `--save-image`.

## Proporción de caracteres del terminal

`--terminal-ratio` ajusta la proporción de los caracteres en la salida del terminal y TXT. El nombre corto existente `--ratio` sigue disponible y funciona de la misma forma.

```bash
pictureascii picture.png --terminal-ratio 0.6
```

Esta opción no controla la proporción del PNG guardado. La salida PNG utiliza el tamaño de celda configurado.

## Personalización

```bash
pictureascii picture.png --chars "@%#*+=-:. "
pictureascii picture.png --cell-width 8 --cell-height 12 --image-font-size 10 --save-image
pictureascii picture.png --background "#101820" --foreground "#F2AA4C" --save-image
pictureascii picture.png --color --transparent --save-image
pictureascii picture.png --image-width 1200 --image-height 800 --save-image
```

La izquierda de la paleta representa las zonas oscuras y la derecha las claras. Los colores aceptan `#RGB` o `#RRGGBB`. Si solo se indica una dimensión PNG, la otra se calcula con la proporción original.

`--image-font-size` establece el tamaño de fuente real dentro de cada celda. Utiliza un valor adecuado para la celda para evitar caracteres recortados o superpuestos. `--foreground` no se puede combinar con `--color`, y `--background` no se puede combinar con `--transparent`.

## Opciones

| Opción | Descripción | Predeterminado |
|---|---|---:|
| `image` | Ruta de la imagen de entrada | Obligatorio |
| `-w`, `--width` | Número de columnas de salida | `120` |
| `-o`, `--output` | Ruta del TXT | Nombre original + `.txt` |
| `--ratio`, `--terminal-ratio` | Corrección de proporción para terminal y TXT | `0.5` |
| `--invert`, `--no-invert` | Invierte el brillo de los caracteres | Activado |
| `--color` | Aplica los colores RGB originales | Desactivado |
| `--color-scale` | Multiplicador de brillo; requiere `--color` | `1.0` |
| `--save-image` | Guarda un PNG | Desactivado |
| `--image-font-size` | Tamaño de fuente utilizado en el PNG | `14` |
| `--cell-width`, `--cell-height` | Ancho y alto de la celda | `10`, `14` |
| `--chars` | Paleta de caracteres | Integrada |
| `--background` | Fondo PNG; incompatible con `--transparent` | Automático |
| `--foreground` | Texto del PNG normal; incompatible con `--color` | Automático |
| `--transparent` | Fondo PNG transparente; incompatible con `--background` | Desactivado |
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
