# Video-2-Slide-Extractor

プレゼンテーションがキャプチャされた動画ファイルからOpenCVを使ってスライドを抽出します。

## 説明

このツールは動画ファイルを解析し、プレゼンテーションスライドを自動的に検出して抽出します。OpenCVライブラリを使用してフレーム間の重要な変化を検出し、安定したスライド検出を実現します。

## 機能

- 動画ファイルからの自動スライド検出
- 検出パラメータのカスタマイズ
- 高品質な画像出力
- 様々な動画フォーマットに対応
- 重複スライドを防ぐ安定性チェック
- 出力品質とフォーマットの設定可能

## 必要条件

- Python 3.7+
- OpenCV
- NumPy
- Pillow
- tomli

## インストール

### Dockerで実行する

```bash
docker compose up --build
```

### ネイティブのPython環境で実行

1. uvのインストール
[公式インストールガイド](https://github.com/astral-sh/uv#installation)を参照してください。

2. 依存関係のインストール
```bash
uv venv
uv pip install -r requirements.txt
```

3. 依存関係の更新
```bash
uv pip install --upgrade -r requirements.txt
```

## 使用方法

### Dockerで実行する

1. `input`ディレクトリにスライドを抽出したい動画ファイルを配置
2. `docker compose up`を実行
3. 抽出されたスライドは`output`ディレクトリに保存されます

### ネイティブのPython環境で実行

```bash
python video2slide_extractor.py <動画ファイル> <出力ディレクトリ> [設定ファイル]
```

### 使用例

```bash
# Dockerで実行する
docker compose up

# ネイティブのPython環境で実行
python video2slide_extractor.py presentation.mp4 ./slides config.toml
```

## 設定

このツールはTOMLファイルを使用して設定できます。各パラメータの詳細な説明は以下の通りです：

### スライド検出パラメータ

```toml
[slide_detection]
# フレーム差分検出の閾値（低い値ほど多くのスライドを検出）
frame_diff_threshold = 15

# 変化検出の最小コントゥア面積（低い値ほど多くのスライドを検出）
min_contour_area = 500

# 検出されたスライド間の最小フレーム数
min_frame_interval = 15

# 安定性チェックのフレーム数
stability_frames = 10

# ブラー処理のカーネルサイズ
blur_kernel_size = 5

# コントラスト強調パラメータ
contrast_clip_limit = 2.0
contrast_grid_size = 8

# 重複検出の類似度閾値（0.0-1.0）
similarity_threshold = 0.95

[output]
# 出力画像のJPEG品質（1-100）
jpeg_quality = 95

# 出力画像の拡張子
extension = "jpg"
```

---

# Video-2-Slide-Extractor

Extract slides from video files captured during presentations using OpenCV.

## Description

This tool analyzes video files and automatically detects and extracts presentation slides. It uses the OpenCV library to detect significant changes between frames and ensures stable slide detection.

## Features

- Automatic slide detection from video files
- Customizable detection parameters
- High-quality image output
- Support for various video formats
- Stability check to prevent duplicate slides
- Configurable output quality and format

## Requirements

- Python 3.7+
- OpenCV
- NumPy
- Pillow
- tomli

## Installation

### Using Docker

```bash
docker compose up --build
```

### Using Native Python Environment

1. Install uv
Please refer to the [official installation guide](https://github.com/astral-sh/uv#installation).

2. Install dependencies
```bash
uv venv
uv pip install -r requirements.txt
```

3. Update dependencies
```bash
uv pip install --upgrade -r requirements.txt
```

## Usage

### Using Docker

1. Place your video file in the `input` directory
2. Run `docker compose up`
3. Extracted slides will be saved in the `output` directory

### Using Native Python Environment

```bash
python video2slide_extractor.py <video_file> <output_directory> [config_file]
```

### Example Usage

```bash
# Using Docker
docker compose up

# Using Native Python Environment
python video2slide_extractor.py presentation.mp4 ./slides config.toml
```

## Configuration

This tool can be configured using a TOML file. Detailed descriptions of each parameter are as follows:

### Slide Detection Parameters

```toml
[slide_detection]
# Frame difference threshold (lower value means more slides are detected)
frame_diff_threshold = 15

# Minimum contour area for change detection (lower value means more slides are detected)
min_contour_area = 500

# Minimum frame interval between detected slides
min_frame_interval = 15

# Stability check frame count
stability_frames = 10

# Blur processing kernel size
blur_kernel_size = 5

# Contrast enhancement parameters
contrast_clip_limit = 2.0
contrast_grid_size = 8

# Similarity threshold for duplicate detection (0.0-1.0)
similarity_threshold = 0.95

[output]
# JPEG quality of output images (1-100)
jpeg_quality = 95

# Output image extension
extension = "jpg"
```
