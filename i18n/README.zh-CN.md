# Picture ASCII

[English](../README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | **简体中文** | [Español](README.es.md) | [Français](README.fr.md)

一个将图像转换为ASCII字符的Python程序。

- 输出纯ASCII文本
- 在终端中应用原图RGB颜色
- 保存普通或彩色PNG
- 自定义字符集、单元格尺寸、背景色和文字颜色
- 支持透明背景和自定义PNG尺寸

## 示例

- [原始图像](https://github.com/doyeon789/pictureascii/tree/main/example/images/sample.png)
- [ASCII文本（受GitHub字体渲染影响，宽高比可能不同）](https://github.com/doyeon789/pictureascii/tree/main/example/outputs/sample.txt)
- [普通ASCII图像](https://github.com/doyeon789/pictureascii/tree/main/example/outputs/sample_plain.png)
- [彩色ASCII图像](https://github.com/doyeon789/pictureascii/tree/main/example/outputs/sample_color.png)

## 安装

需要Python 3.10或更高版本。

```bash
pip install pictureascii
```

本地开发时，请在项目根目录运行：

```bash
python -m pip install -e .
```

## 基本用法

```bash
pictureascii picture.png
pictureascii picture.png --width 200
```

结果会以`picture.txt`保存到原图所在目录。

## 彩色输出与PNG导出

```bash
pictureascii picture.png --color
pictureascii picture.png --save-image
pictureascii picture.png --color --save-image
```

建议使用支持24位ANSI颜色的终端查看彩色输出。TXT文件不包含ANSI颜色代码。

## 自定义输出

```bash
pictureascii picture.png --chars "@%#*+=-:. "
pictureascii picture.png --cell-width 8 --cell-height 12 --save-image
pictureascii picture.png --background "#101820" --foreground "#F2AA4C" --save-image
pictureascii picture.png --color --transparent --save-image
pictureascii picture.png --image-width 1200 --image-height 800 --save-image
```

字符集左侧表示暗部，右侧表示亮部。颜色支持`#RGB`和`#RRGGBB`格式。仅指定一个PNG尺寸时，另一个尺寸会根据原图比例计算。

## 选项

| 选项 | 说明 | 默认值 |
|---|---|---:|
| `image` | 输入图像路径 | 必填 |
| `-w`, `--width` | 输出字符列数 | `120` |
| `-o`, `--output` | TXT输出路径 | 原文件名 + `.txt` |
| `--ratio` | 字符宽高比校正 | `0.5` |
| `--invert`, `--no-invert` | 反转字符明暗 | 启用 |
| `--color` | 应用原图RGB颜色 | 禁用 |
| `--color-scale` | 颜色亮度倍数 | `1.0` |
| `--save-image` | 保存PNG | 禁用 |
| `--cell-width`, `--cell-height` | 字符单元格宽度和高度 | `10`, `14` |
| `--chars` | 字符集 | 内置字符集 |
| `--background`, `--foreground` | PNG背景色和文字颜色 | 自动 |
| `--transparent` | 使用透明PNG背景 | 禁用 |
| `--image-width`, `--image-height` | PNG宽度和高度 | 自动 |

```bash
pictureascii --help
python -m pictureascii picture.png --color
```

## 开发

```bash
python -m unittest discover -s tests -v
python -m build
python -m twine check dist/*
```
