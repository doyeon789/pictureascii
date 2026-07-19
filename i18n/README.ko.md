# Picture ASCII

[English](../README.md) | **한국어** | [日本語](README.ja.md) | [Español](README.es.md) | [Français](README.fr.md)

이미지를 ASCII 문자로 변환하는 Python 프로그램입니다.

- 일반 ASCII 텍스트 출력
- 원본 RGB 색상을 적용한 터미널 출력
- 일반 또는 컬러 PNG 저장
- 문자 팔레트, 셀 크기, 배경색 및 글자색 설정
- 투명 배경과 PNG 해상도 지정

## 샘플 바로가기

- [원본 이미지](https://github.com/doyeon789/pictureascii/tree/main/example/images/sample.png)
- [ASCII 텍스트 (github폰트 호환 문제로 이미지 비율이 다를 수 있음)](https://github.com/doyeon789/pictureascii/tree/main/example/outputs/sample.txt)
- [일반 ASCII 이미지](https://github.com/doyeon789/pictureascii/tree/main/example/outputs/sample_plain.png)
- [컬러 ASCII 이미지](https://github.com/doyeon789/pictureascii/tree/main/example/outputs/sample_color.png)

## 설치

Python 3.10 이상이 필요합니다.

```bash
pip install pictureascii
```

소스에서 개발용으로 설치하려면 프로젝트 루트에서 실행합니다.

```bash
python -m pip install -e .
```

## 기본 사용법

```bash
pascii picture.png
```

`pascii`는 `pictureascii`의 짧은 별칭이며 두 명령의 동작은 같습니다. 실행 결과는 원본 이미지와 같은 위치에 `picture.txt`로 저장됩니다.

출력할 ASCII 아트의 가로 문자 수를 변경할 수도 있습니다.

```bash
pascii picture.png --width 200
```

## 컬러 출력

원본 이미지의 RGB 색상을 터미널 문자에 적용합니다.

```bash
pictureascii picture.png --color
```

컬러 밝기는 `--color-scale`로 조절합니다.

```bash
pictureascii picture.png --color --color-scale 0.8
```

컬러 터미널 출력은 Windows Terminal이나 PowerShell처럼 24비트 ANSI 색상을 지원하는 터미널에서 확인하는 것이 좋습니다.

`--color-scale`은 `--color`와 함께 사용해야 합니다.

## PNG 이미지 저장

일반 ASCII 이미지를 저장합니다.

```bash
pictureascii picture.png --save-image
```

컬러 ASCII 이미지를 저장하려면 `--color`를 함께 사용합니다.

```bash
pictureascii picture.png --color --save-image
```

저장 파일 이름은 다음과 같습니다.

```text
picture.txt
picture_plain.png   # --save-image
picture_color.png   # --color --save-image
```

TXT 파일에는 ANSI 색상 코드가 포함되지 않은 일반 ASCII 문자열이 저장됩니다.
PNG 전용 옵션은 `--save-image`와 함께 사용해야 합니다.

## 터미널 문자 비율

`--terminal-ratio`는 터미널과 TXT 출력의 문자 비율을 보정합니다.
기존의 짧은 이름인 `--ratio`도 동일하게 사용할 수 있습니다.

```bash
pictureascii picture.png --terminal-ratio 0.6
```

이 설정은 저장되는 PNG 비율에는 적용되지 않습니다. PNG는 지정한 문자
셀 크기를 기준으로 비율을 계산합니다.

## 문자 셀 크기

PNG에서 ASCII 문자 하나가 차지하는 기본 셀 크기는 `10×14px`입니다.

```bash
pictureascii picture.png --cell-width 8 --cell-height 12 --image-font-size 10 --save-image
```

PNG 크기를 별도로 지정하지 않으면 다음 방식으로 전체 크기를 계산합니다.

```text
PNG 너비 = 가로 문자 수 × 셀 너비
PNG 높이 = 세로 문자 수 × 셀 높이
```

`--image-font-size`는 셀 안에서 실제로 사용하는 폰트 크기를 지정합니다.
문자가 잘리거나 겹치지 않도록 셀 크기에 맞는 값을 사용하세요.

## 문자 팔레트

`--chars`로 밝기 표현에 사용할 문자를 직접 지정할 수 있습니다. 문자열의 왼쪽 문자는 어두운 영역, 오른쪽 문자는 밝은 영역에 사용됩니다.

```bash
pictureascii picture.png --chars "@%#*+=-:. "
```

공백도 문자 팔레트에 포함되므로 따옴표로 감싸는 것이 좋습니다.

## 배경색과 글자색

`#RGB` 또는 `#RRGGBB` 형식을 사용할 수 있습니다.

```bash
pictureascii picture.png --background "#101820" --foreground "#F2AA4C" --save-image
```

`--foreground`는 일반 PNG의 글자색에 적용됩니다. 컬러 PNG는 원본 이미지의
RGB 색상을 사용하므로 `--foreground`와 `--color`를 함께 사용할 수 없습니다.

## 투명 배경

```bash
pictureascii picture.png --transparent --save-image
```

컬러 문자와 투명 배경을 함께 사용할 수도 있습니다.

```bash
pictureascii picture.png --color --transparent --save-image
```

`--transparent`와 `--background`는 함께 사용할 수 없습니다.

## 저장 이미지 크기 지정

PNG의 픽셀 크기를 직접 지정할 수 있습니다.

```bash
pictureascii picture.png --image-width 1200 --image-height 800 --save-image
```

- 너비와 높이를 모두 지정하면 입력한 크기로 저장합니다.
- 한쪽만 지정하면 원본 이미지 비율에 맞춰 나머지 크기를 계산합니다.
- 아무것도 지정하지 않으면 문자 수와 셀 크기로 PNG 크기를 계산합니다.

## 사용 예시

```bash
pictureascii picture.png --color --width 180 --chars "@%#*+=-:. " --cell-width 10 --cell-height 14 --image-width 1800 --transparent --save-image
```

## 전체 옵션

| 옵션 | 설명 | 기본값 |
|---|---|---:|
| `image` | 변환할 이미지 경로 | 필수 |
| `-w`, `--width` | 출력 가로 문자 수 | `120` |
| `-o`, `--output` | TXT 저장 경로 | 원본 이름 `.txt` |
| `--ratio`, `--terminal-ratio` | 터미널 및 TXT 문자 비율 보정값 | `0.5` |
| `--invert`, `--no-invert` | 문자 명암 반전 여부 | 켜짐 |
| `--color` | 원본 RGB 색상을 문자에 적용 | 꺼짐 |
| `--color-scale` | 컬러 밝기 배율, `--color` 필요 | `1.0` |
| `--save-image` | 현재 색상 모드의 PNG 저장 | 꺼짐 |
| `--image-font-size` | PNG에서 사용하는 폰트 크기 | `14` |
| `--cell-width` | 문자 셀 너비 | `10` |
| `--cell-height` | 문자 셀 높이 | `14` |
| `--chars` | 사용자 문자 팔레트 | 기본 팔레트 |
| `--background` | PNG 배경색, `--transparent`와 함께 사용 불가 | 자동 |
| `--foreground` | 일반 PNG 글자색, `--color`와 함께 사용 불가 | 자동 |
| `--transparent` | PNG 배경 투명 처리, `--background`와 함께 사용 불가 | 꺼짐 |
| `--image-width` | PNG 너비 | 자동 |
| `--image-height` | PNG 높이 | 자동 |

터미널에서 전체 도움말을 확인할 수 있습니다.

```bash
pictureascii --help
```

모듈 방식으로도 실행할 수 있습니다.

```bash
python -m pictureascii picture.png --color
```

## 개발 및 배포

테스트를 실행합니다.

```bash
python -m unittest discover -s tests -v
```

wheel과 source distribution을 생성합니다.

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
```

먼저 TestPyPI에 시험 배포하는 것을 권장합니다.

```bash
python -m twine upload --repository testpypi dist/*
```

검증 후 실제 PyPI에 배포합니다.

```bash
python -m twine upload dist/*
```

새 버전을 배포할 때는 `pyproject.toml`과 `src/pictureascii/__init__.py`의 버전을 함께 올리고 `dist`를 다시 생성해야 합니다.
