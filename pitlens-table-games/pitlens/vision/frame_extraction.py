import cv2
import os
from typing import Optional

def extract_frame_at_timestamp(video_path: str, timestamp_sec: float, output_path: str) -> Optional[str]:
    """
    Extracts a frame from a local video file at the given timestamp.
    Returns the path to the saved frame image, or None if extraction fails.
    """
    if not os.path.exists(video_path):
        return None
        
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
        
    # Get FPS and set the frame position
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_number = int(timestamp_sec * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        cv2.imwrite(output_path, frame)
        return output_path
        
    return None
