import cv2
import numpy as np
import os
import sys
from datetime import datetime
from PIL import Image
import tomli
from pathlib import Path

# デフォルト設定
DEFAULT_CONFIG = {
    "slide_detection": {
        # フレーム差分の閾値（低いほど多くのスライドを検出）
        "frame_diff_threshold": 15,
        # 最小コントゥア面積（小さいほど多くのスライドを検出）
        "min_contour_area": 500,
        # 最小フレーム間隔（フレーム数）
        "min_frame_interval": 15,
        # 安定性チェックのフレーム数
        "stability_frames": 10,
        # ブラー処理のカーネルサイズ
        "blur_kernel_size": 5,
        # コントラストクリップの制限
        "contrast_clip_limit": 2.0,
        # コントラストグリッドのサイズ
        "contrast_grid_size": 8,
        # 類似度の閾値
        "similarity_threshold": 0.95
    },
    "output": {
        # 出力画像の品質（1-100）
        "jpeg_quality": 95,
        # 出力画像の拡張子
        "extension": "jpg"
    }
}

def load_config(config_path):
    """Load configuration from TOML file"""
    try:
        if os.path.exists(config_path):
            with open(config_path, "rb") as f:
                config = tomli.load(f)
                print(f"Configuration loaded: {config_path}")
                return config
        else:
            print(f"Configuration file not found: {config_path}")
            print("Using default configuration")
            return DEFAULT_CONFIG
    except Exception as e:
        print(f"Failed to load configuration: {e}")
        print("Using default configuration")
        return DEFAULT_CONFIG

def preprocess_frame(frame, config=None):
    """Preprocess frame for slide detection"""
    slide_detection = DEFAULT_CONFIG["slide_detection"].copy()
    if config and "slide_detection" in config:
        slide_detection.update(config["slide_detection"])
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur_kernel_size = slide_detection["blur_kernel_size"]
    blurred = cv2.GaussianBlur(gray, (blur_kernel_size, blur_kernel_size), 0)
    
    clip_limit = slide_detection["contrast_clip_limit"]
    grid_size = slide_detection["contrast_grid_size"]
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(grid_size, grid_size))
    enhanced = clahe.apply(blurred)
    
    return enhanced

def calculate_similarity(frame1, frame2):
    """Calculate similarity between two frames"""
    hist1 = cv2.calcHist([frame1], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([frame2], [0], None, [256], [0, 256])
    
    cv2.normalize(hist1, hist1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    cv2.normalize(hist2, hist2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    
    similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    return max(0.0, similarity)

def extract_slides(video_path, output_dir, config):
    """Extract slides from video file"""
    video_path = str(Path(video_path).resolve())
    output_dir = str(Path(output_dir).resolve())
    
    slide_detection = DEFAULT_CONFIG["slide_detection"].copy()
    slide_detection.update(config.get("slide_detection", {}))
    
    output_config = DEFAULT_CONFIG["output"].copy()
    output_config.update(config.get("output", {}))
    
    frame_diff_threshold = slide_detection["frame_diff_threshold"]
    min_contour_area = slide_detection["min_contour_area"]
    min_frame_interval = slide_detection["min_frame_interval"]
    stability_frames = slide_detection["stability_frames"]
    similarity_threshold = slide_detection["similarity_threshold"]
    jpeg_quality = output_config["jpeg_quality"]
    output_ext = output_config["extension"]

    os.makedirs(output_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video file: {video_path}")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video information:")
    print(f"- FPS: {fps}")
    print(f"- Total frames: {total_frames}")
    print(f"- Configuration:")
    print(f"  - Frame difference threshold: {frame_diff_threshold}")
    print(f"  - Minimum contour area: {min_contour_area}")
    print(f"  - Minimum frame interval: {min_frame_interval}")
    print(f"  - Stability check frames: {stability_frames}")
    print(f"  - Similarity threshold: {similarity_threshold}")
    print(f"  - JPEG quality: {jpeg_quality}")
    print(f"  - Output extension: {output_ext}")
    
    prev_frame = None
    prev_processed = None
    frame_count = 0
    slide_count = 1
    last_save_frame = 0
    transition_buffer = []
    in_transition = False
    last_saved_slide = None
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        processed_frame = preprocess_frame(frame, {"slide_detection": slide_detection})
        
        if prev_processed is not None:
            diff = cv2.absdiff(processed_frame, prev_processed)
            _, thresh = cv2.threshold(diff, frame_diff_threshold, 255, cv2.THRESH_BINARY)
            
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            total_area = sum(cv2.contourArea(cnt) for cnt in contours)
            
            if total_area > min_contour_area:
                if not in_transition:
                    in_transition = True
                    transition_buffer = []
                transition_buffer.append(frame)
            elif in_transition and len(transition_buffer) >= stability_frames:
                if frame_count - last_save_frame >= min_frame_interval:
                    stable_frame = transition_buffer[-1]
                    if last_saved_slide is None or calculate_similarity(
                        preprocess_frame(stable_frame, {"slide_detection": slide_detection}),
                        preprocess_frame(last_saved_slide, {"slide_detection": slide_detection})
                    ) < similarity_threshold:
                        output_path = os.path.join(output_dir, f"{slide_count:03d}.{output_ext}")
                        pil_image = Image.fromarray(cv2.cvtColor(stable_frame, cv2.COLOR_BGR2RGB))
                        pil_image.save(output_path, quality=jpeg_quality)
                        
                        print(f"Saved slide {slide_count}: {output_path}")
                        last_saved_slide = stable_frame.copy()
                        slide_count += 1
                        last_save_frame = frame_count
                    else:
                        print(f"Skipped: High similarity (frame {frame_count})")
                
                in_transition = False
                transition_buffer = []
        
        prev_frame = frame
        prev_processed = processed_frame
        
        if frame_count % 30 == 0:
            progress = (frame_count / total_frames) * 100
            print(f"\rProcessing: {progress:.1f}% ({frame_count}/{total_frames})", end="")
    
    cap.release()
    print(f"\nProcessing complete: Extracted {slide_count - 1} slides")

def main():
    if len(sys.argv) < 3:
        print("Usage: python extract_slides.py <video_file> <output_directory> [config_file]")
        sys.exit(1)
    
    video_path = sys.argv[1]
    output_dir = sys.argv[2]
    config_path = sys.argv[3] if len(sys.argv) > 3 else "config.toml"
    
    config = load_config(config_path)
    extract_slides(video_path, output_dir, config)

if __name__ == "__main__":
    main() 
