#!/bin/sh

INPUT_DIR="/app/input"
OUTPUT_DIR="/app/output"

mkdir -p "$OUTPUT_DIR"

VIDEO_EXTENSIONS="mp4 mkv avi mov wmv"

find "$INPUT_DIR" -type f | while read -r video_file; do
    extension=$(echo "$video_file" | awk -F. '{print tolower($NF)}')
    
    is_video=false
    for ext in $VIDEO_EXTENSIONS; do
        if [ "$extension" = "$ext" ]; then
            is_video=true
            break
        fi
    done
    
    if [ "$is_video" = true ]; then
        video_name=$(basename "$video_file" | sed "s/\.[^.]*$//"
        output_path="$OUTPUT_DIR/$video_name"
        mkdir -p "$output_path"
        
        if [ ! -f "$output_path/001.jpg" ]; then
            echo "Processing: $video_file"
            echo "Output: $output_path"
            
            python video2slide_extractor.py "$video_file" "$output_path"
            
            echo "Done: $video_file"
            echo "------------------------"
        else
            echo "Skipped: $video_file (Already processed)"
            echo "------------------------"
        fi
    fi
done

echo "All processes are completed" 
