# Picture ASCII

[English](../README.md) | [한국어](README.ko.md) | **日本語** | [简体中文](README.zh-CN.md) | [Español](README.es.md) | [Français](README.fr.md)

画像をASCII文字に変換するPythonプログラムです。

- プレーンASCIIテキスト出力
- 元画像のRGBカラーを使用したターミナル出力
- プレーンまたはカラーPNGの保存
- 文字パレット、セルサイズ、背景色、文字色の設定
- 透過背景とPNGサイズの指定

## サンプル

- [元画像](https://github.com/doyeon789/pictureascii/tree/main/example/images/sample.png)
- [ASCIIテキスト（GitHubのフォント表示により縦横比が異なる場合があります）](https://github.com/doyeon789/pictureascii/tree/main/example/outputs/sample.txt)
- [プレーンASCII画像](https://github.com/doyeon789/pictureascii/tree/main/example/outputs/sample_plain.png)
- [カラーASCII画像](https://github.com/doyeon789/pictureascii/tree/main/example/outputs/sample_color.png)

## インストール

Python 3.10以降が必要です。

```bash
pip install pictureascii
```

ローカル開発では、プロジェクトのルートで実行します。

```bash
python -m pip install -e .
```

## 基本的な使い方

```bash
pictureascii picture.png
pictureascii picture.png --width 200
```

結果は元画像と同じ場所の`picture.txt`に保存されます。

## カラー出力とPNG保存

```bash
pictureascii picture.png --color
pictureascii picture.png --save-image
pictureascii picture.png --color --save-image
```

カラー表示には24ビットANSIカラー対応のターミナルを推奨します。TXTにはANSIカラーコードは含まれません。

## 表示のカスタマイズ

```bash
pictureascii picture.png --chars "@%#*+=-:. "
pictureascii picture.png --cell-width 8 --cell-height 12 --save-image
pictureascii picture.png --background "#101820" --foreground "#F2AA4C" --save-image
pictureascii picture.png --color --transparent --save-image
pictureascii picture.png --image-width 1200 --image-height 800 --save-image
```

文字パレットは左側が暗部、右側が明部を表します。色は`#RGB`または`#RRGGBB`形式です。PNGサイズを片方だけ指定した場合、もう片方は元画像の比率から計算されます。

## オプション

| オプション | 説明 | 初期値 |
|---|---|---:|
| `image` | 入力画像のパス | 必須 |
| `-w`, `--width` | 出力の横文字数 | `120` |
| `-o`, `--output` | TXTの保存先 | 元の名前 + `.txt` |
| `--ratio` | 文字の縦横比補正 | `0.5` |
| `--invert`, `--no-invert` | 文字の明暗を反転 | 有効 |
| `--color` | 元画像のRGB色を適用 | 無効 |
| `--color-scale` | カラーの明るさ倍率 | `1.0` |
| `--save-image` | PNGとして保存 | 無効 |
| `--cell-width`, `--cell-height` | 文字セルの幅と高さ | `10`, `14` |
| `--chars` | 文字パレット | 内蔵値 |
| `--background`, `--foreground` | PNGの背景色と文字色 | 自動 |
| `--transparent` | PNG背景を透過 | 無効 |
| `--image-width`, `--image-height` | PNGの幅と高さ | 自動 |

```bash
pictureascii --help
python -m pictureascii picture.png --color
```

## 開発

```bash
python -m unittest discover -s tests -v
python -m build
python -m twine check dist/*
```
