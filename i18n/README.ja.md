# Picture ASCII

[English](../README.md) | [한국어](README.ko.md) | **日本語** | [Español](README.es.md) | [Français](README.fr.md)

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
pascii picture.png
pascii picture.png --width 200
```

`pascii`は`pictureascii`の短いエイリアスで、どちらも同じように動作します。結果は元画像と同じ場所の`picture.txt`に保存されます。

## カラー出力とPNG保存

```bash
pictureascii picture.png --color
pictureascii picture.png --save-image
pictureascii picture.png --color --save-image
```

カラー表示には24ビットANSIカラー対応のターミナルを推奨します。TXTにはANSIカラーコードは含まれません。
`--color-scale`を使用する場合は`--color`が必要です。PNG専用オプションを使用する場合は`--save-image`が必要です。

## ターミナルの文字比率

`--terminal-ratio`はターミナルとTXT出力の文字比率を補正します。従来の短い名前`--ratio`も同じように使用できます。

```bash
pictureascii picture.png --terminal-ratio 0.6
```

この設定は保存するPNGの比率には適用されません。PNGは設定された文字セルサイズを使用します。

## 表示のカスタマイズ

```bash
pictureascii picture.png --chars "@%#*+=-:. "
pictureascii picture.png --cell-width 8 --cell-height 12 --image-font-size 10 --save-image
pictureascii picture.png --background "#101820" --foreground "#F2AA4C" --save-image
pictureascii picture.png --color --transparent --save-image
pictureascii picture.png --image-width 1200 --image-height 800 --save-image
```

文字パレットは左側が暗部、右側が明部を表します。色は`#RGB`または`#RRGGBB`形式です。PNGサイズを片方だけ指定した場合、もう片方は元画像の比率から計算されます。

`--image-font-size`はセル内で実際に使用するフォントサイズです。文字が切れたり重なったりしないよう、セルサイズに合う値を指定してください。`--foreground`と`--color`、および`--background`と`--transparent`は同時に使用できません。

## オプション

| オプション | 説明 | 初期値 |
|---|---|---:|
| `image` | 入力画像のパス | 必須 |
| `-w`, `--width` | 出力の横文字数 | `120` |
| `-o`, `--output` | TXTの保存先 | 元の名前 + `.txt` |
| `--ratio`, `--terminal-ratio` | ターミナルとTXTの文字比率補正 | `0.5` |
| `--invert`, `--no-invert` | 文字の明暗を反転 | 有効 |
| `--color` | 元画像のRGB色を適用 | 無効 |
| `--color-scale` | カラーの明るさ倍率（`--color`が必要） | `1.0` |
| `--save-image` | PNGとして保存 | 無効 |
| `--image-font-size` | PNGで使用するフォントサイズ | `14` |
| `--cell-width`, `--cell-height` | 文字セルの幅と高さ | `10`, `14` |
| `--chars` | 文字パレット | 内蔵値 |
| `--background` | PNGの背景色（`--transparent`と併用不可） | 自動 |
| `--foreground` | プレーンPNGの文字色（`--color`と併用不可） | 自動 |
| `--transparent` | PNG背景を透過（`--background`と併用不可） | 無効 |
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
