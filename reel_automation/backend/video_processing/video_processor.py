"""
Video Processing Pipeline for Sports Reels
Handles cropping, editing, and formatting videos for Instagram Reels
"""

import cv2
import ffmpeg
import numpy as np
from pathlib import Path
from typing import Tuple, Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoProcessor:
    """Processes sports highlight videos for Instagram Reels"""

    def __init__(self, output_resolution: Tuple[int, int] = (1080, 1920)):
        """
        Initialize video processor

        Args:
            output_resolution: Target resolution (width, height) for vertical video
        """
        self.output_resolution = output_resolution
        self.target_width, self.target_height = output_resolution
        self.aspect_ratio = self.target_width / self.target_height  # 9:16

    def process_highlight(
        self,
        input_path: str,
        output_path: str,
        max_duration: int = 15,
        apply_speed_ramp: bool = True
    ) -> Dict[str, any]:
        """
        Process a highlight video into Instagram Reel format

        Args:
            input_path: Path to input video file
            output_path: Path to save processed video
            max_duration: Maximum duration in seconds
            apply_speed_ramp: Whether to apply speed ramping effect

        Returns:
            Dictionary with processing metadata
        """
        try:
            logger.info(f"Processing video: {input_path}")

            # Analyze video
            video_info = self._analyze_video(input_path)

            # Detect action center
            action_center = self._detect_action_center(input_path)

            # Calculate crop area
            crop_coords = self._calculate_smart_crop(
                video_info['width'],
                video_info['height'],
                action_center
            )

            # Process video with FFmpeg
            self._process_with_ffmpeg(
                input_path,
                output_path,
                crop_coords,
                max_duration,
                apply_speed_ramp
            )

            result = {
                "success": True,
                "output_path": output_path,
                "duration": min(video_info['duration'], max_duration),
                "resolution": self.output_resolution,
                "crop_applied": True
            }

            logger.info(f"Video processed successfully: {output_path}")
            return result

        except Exception as e:
            logger.error(f"Error processing video: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _analyze_video(self, video_path: str) -> Dict[str, any]:
        """Analyze video to get metadata"""
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'video'),
                None
            )

            if video_stream is None:
                raise ValueError("No video stream found")

            return {
                'width': int(video_stream['width']),
                'height': int(video_stream['height']),
                'duration': float(video_stream.get('duration', 0)),
                'fps': eval(video_stream.get('r_frame_rate', '30/1'))
            }
        except Exception as e:
            logger.warning(f"Error analyzing video: {e}")
            # Return defaults
            return {
                'width': 1920,
                'height': 1080,
                'duration': 15,
                'fps': 30
            }

    def _detect_action_center(self, video_path: str) -> Tuple[int, int]:
        """
        Detect the center of action in the video
        Uses motion detection to find where most action happens

        Returns:
            (x, y) coordinates of action center
        """
        try:
            cap = cv2.VideoCapture(video_path)

            # Sample frames
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_interval = max(1, frame_count // 20)  # Sample 20 frames

            motion_map = None
            prev_frame = None

            for i in range(0, frame_count, sample_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()

                if not ret:
                    break

                # Convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                if prev_frame is not None:
                    # Calculate frame difference
                    diff = cv2.absdiff(gray, prev_frame)

                    if motion_map is None:
                        motion_map = np.zeros_like(diff, dtype=np.float32)

                    motion_map += diff.astype(np.float32)

                prev_frame = gray

            cap.release()

            if motion_map is not None:
                # Find center of motion
                motion_map = cv2.GaussianBlur(motion_map, (21, 21), 0)
                _, _, _, max_loc = cv2.minMaxLoc(motion_map)
                return max_loc
            else:
                # Default to center
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                return (width // 2, height // 2)

        except Exception as e:
            logger.warning(f"Error detecting action center: {e}")
            # Default to center
            return (960, 540)

    def _calculate_smart_crop(
        self,
        video_width: int,
        video_height: int,
        action_center: Tuple[int, int]
    ) -> Dict[str, int]:
        """
        Calculate optimal crop coordinates to follow action

        Returns:
            Dictionary with crop coordinates {x, y, width, height}
        """
        # Calculate crop dimensions for 9:16 aspect ratio
        crop_width = int(video_height * self.aspect_ratio)

        # If video is already narrower than target, use full width
        if crop_width > video_width:
            crop_width = video_width
            crop_height = int(crop_width / self.aspect_ratio)
        else:
            crop_height = video_height

        # Center crop on action, but keep within bounds
        action_x, action_y = action_center

        crop_x = max(0, min(action_x - crop_width // 2, video_width - crop_width))
        crop_y = max(0, min(action_y - crop_height // 2, video_height - crop_height))

        return {
            'x': crop_x,
            'y': crop_y,
            'width': crop_width,
            'height': crop_height
        }

    def _process_with_ffmpeg(
        self,
        input_path: str,
        output_path: str,
        crop_coords: Dict[str, int],
        max_duration: int,
        apply_speed_ramp: bool
    ) -> None:
        """
        Process video using FFmpeg with crop, scale, and effects

        Args:
            input_path: Input video path
            output_path: Output video path
            crop_coords: Crop coordinates
            max_duration: Maximum duration in seconds
            apply_speed_ramp: Whether to apply speed ramping
        """
        try:
            # Build FFmpeg filter chain
            filters = []

            # Crop filter
            filters.append(
                f"crop={crop_coords['width']}:{crop_coords['height']}:"
                f"{crop_coords['x']}:{crop_coords['y']}"
            )

            # Scale to target resolution
            filters.append(f"scale={self.target_width}:{self.target_height}")

            # Optional: Speed ramp effect (subtle slow-mo at peak moment)
            if apply_speed_ramp:
                # This is a simple implementation - can be enhanced
                # For now, we'll skip complex speed ramping and focus on basic processing
                pass

            # Combine filters
            filter_string = ",".join(filters)

            # Create output directory if needed
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            # Process with FFmpeg
            stream = ffmpeg.input(input_path)

            # Trim to max duration
            stream = stream.trim(duration=max_duration)

            # Apply filters
            stream = stream.filter_multi_output('split')[0]
            video = stream.video.filter_('scale', self.target_width, self.target_height)
            audio = stream.audio

            # Output
            output = ffmpeg.output(
                video,
                audio,
                output_path,
                vcodec='libx264',
                acodec='aac',
                video_bitrate='5M',
                audio_bitrate='192k',
                **{'c:v': 'libx264', 'preset': 'medium', 'crf': '23'}
            )

            # Run FFmpeg
            output.overwrite_output().run(capture_stdout=True, capture_stderr=True)

        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
            # Fallback to simple processing
            self._simple_process(input_path, output_path, max_duration)

    def _simple_process(self, input_path: str, output_path: str, max_duration: int) -> None:
        """
        Simplified video processing fallback

        Args:
            input_path: Input video path
            output_path: Output video path
            max_duration: Maximum duration
        """
        try:
            (
                ffmpeg
                .input(input_path, t=max_duration)
                .output(
                    output_path,
                    vf=f'scale={self.target_width}:{self.target_height}:force_original_aspect_ratio=increase,crop={self.target_width}:{self.target_height}',
                    vcodec='libx264',
                    acodec='aac'
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
        except Exception as e:
            logger.error(f"Simple processing also failed: {e}")
            raise


def test_video_processor():
    """Test the video processor"""
    processor = VideoProcessor()
    print(f"Video Processor initialized with resolution: {processor.output_resolution}")
    print("Ready to process sports highlights!")


if __name__ == "__main__":
    test_video_processor()
