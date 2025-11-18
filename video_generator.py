"""
Video Generator for Instagram Reels
Creates viral sports videos with text overlays and animations
"""
import os
import random
from moviepy.editor import (
    VideoClip, TextClip, CompositeVideoClip,
    AudioFileClip, concatenate_videoclips, ColorClip
)
from moviepy.video.fx import fadein, fadeout
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from config import (
    VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS,
    VIDEO_DURATION_MIN, VIDEO_DURATION_MAX,
    TITLE_FONT_SIZE, SUBTITLE_FONT_SIZE, CAPTION_FONT_SIZE,
    PRIMARY_COLOR, ACCENT_COLOR, BACKGROUND_COLOR,
    OUTPUT_DIR, MUSIC_DIR, IMAGES_DIR
)


class VideoGenerator:
    def __init__(self):
        # Ensure output directories exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(MUSIC_DIR, exist_ok=True)
        os.makedirs(IMAGES_DIR, exist_ok=True)
        os.makedirs(f"{OUTPUT_DIR}/temp", exist_ok=True)

    def create_reel(self, script, output_name=None, add_voiceover=True, add_music=False):
        """
        Create a complete Instagram Reel from script

        Args:
            script: Dict with 'hook', 'content', 'cta', 'voiceover'
            output_name: Custom output filename
            add_voiceover: Add AI voiceover
            add_music: Add background music

        Returns:
            Path to generated video file
        """
        print("🎬 Creating Instagram Reel...")

        # Determine video duration
        duration = random.randint(VIDEO_DURATION_MIN, VIDEO_DURATION_MAX)

        # Generate voiceover audio if requested
        audio_path = None
        if add_voiceover and script.get('voiceover'):
            audio_path = self._generate_voiceover(script['voiceover'])
            if audio_path and os.path.exists(audio_path):
                # Adjust duration to match voiceover
                from moviepy.editor import AudioFileClip as AFC
                audio_clip = AFC(audio_path)
                duration = min(max(audio_clip.duration, VIDEO_DURATION_MIN), VIDEO_DURATION_MAX)
                audio_clip.close()

        # Create video clips
        clips = []

        # Background
        background = self._create_gradient_background(duration)
        clips.append(background)

        # Hook (first 3-5 seconds)
        hook_duration = min(4, duration * 0.3)
        hook_clip = self._create_text_clip(
            script['hook'],
            duration=hook_duration,
            fontsize=TITLE_FONT_SIZE,
            color=ACCENT_COLOR,
            position='center',
            animation='zoom'
        )
        clips.append(hook_clip)

        # Content (middle section)
        content_start = hook_duration
        content_duration = duration - hook_duration - 3
        content_clip = self._create_scrolling_text(
            script['content'],
            start_time=content_start,
            duration=content_duration,
            fontsize=SUBTITLE_FONT_SIZE
        )
        clips.append(content_clip)

        # CTA (last 2-3 seconds)
        cta_start = content_start + content_duration
        cta_duration = duration - cta_start
        cta_clip = self._create_text_clip(
            script['cta'],
            duration=cta_duration,
            fontsize=CAPTION_FONT_SIZE,
            color=PRIMARY_COLOR,
            position='center',
            animation='fade',
            start_time=cta_start
        )
        clips.append(cta_clip)

        # Compose video
        video = CompositeVideoClip(clips, size=(VIDEO_WIDTH, VIDEO_HEIGHT))
        video = video.set_duration(duration)

        # Add audio
        if audio_path and os.path.exists(audio_path):
            audio = AudioFileClip(audio_path)
            video = video.set_audio(audio)

        # Generate output filename
        if not output_name:
            output_name = f"reel_{script.get('category', 'sports')}_{random.randint(1000, 9999)}.mp4"

        output_path = os.path.join(OUTPUT_DIR, output_name)

        # Render video
        print(f"📹 Rendering video: {output_name}")
        video.write_videofile(
            output_path,
            fps=VIDEO_FPS,
            codec='libx264',
            audio_codec='aac',
            preset='medium',
            threads=4
        )

        # Cleanup
        video.close()
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except:
                pass

        print(f"✅ Video created: {output_path}")
        return output_path

    def _create_gradient_background(self, duration):
        """Create animated gradient background"""
        def make_frame(t):
            # Animated gradient
            img = np.zeros((VIDEO_HEIGHT, VIDEO_WIDTH, 3), dtype=np.uint8)

            # Create vertical gradient with time-based color shift
            for y in range(VIDEO_HEIGHT):
                progress = y / VIDEO_HEIGHT
                # Animate colors over time
                r = int(BACKGROUND_COLOR[0] + progress * 30 * np.sin(t * 0.5))
                g = int(BACKGROUND_COLOR[1] + progress * 30 * np.cos(t * 0.3))
                b = int(BACKGROUND_COLOR[2] + progress * 50)

                # Clamp values
                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))

                img[y, :] = [r, g, b]

            return img

        return VideoClip(make_frame, duration=duration)

    def _create_text_clip(self, text, duration, fontsize, color, position='center',
                          animation=None, start_time=0):
        """Create animated text clip"""
        try:
            # Create text clip
            txt_clip = TextClip(
                text,
                fontsize=fontsize,
                color=color,
                font='Arial-Bold',
                size=(VIDEO_WIDTH - 100, None),
                method='caption',
                align='center'
            )

            # Apply animation
            if animation == 'zoom':
                txt_clip = txt_clip.resize(lambda t: 1 + 0.3 * np.sin(t * 3))
            elif animation == 'fade':
                txt_clip = fadein(txt_clip, 0.5)
                txt_clip = fadeout(txt_clip, 0.5)

            # Position
            if position == 'center':
                txt_clip = txt_clip.set_position('center')
            elif position == 'top':
                txt_clip = txt_clip.set_position(('center', 100))
            elif position == 'bottom':
                txt_clip = txt_clip.set_position(('center', VIDEO_HEIGHT - 200))

            txt_clip = txt_clip.set_start(start_time).set_duration(duration)

            return txt_clip

        except Exception as e:
            print(f"Error creating text clip: {e}")
            # Return empty clip as fallback
            return ColorClip(size=(1, 1), color=(0, 0, 0), duration=duration).set_opacity(0)

    def _create_scrolling_text(self, text, start_time, duration, fontsize):
        """Create scrolling text effect"""
        try:
            # Split into lines for better readability
            words = text.split()
            lines = []
            current_line = []

            for word in words:
                current_line.append(word)
                if len(' '.join(current_line)) > 30:  # Wrap at ~30 chars
                    lines.append(' '.join(current_line[:-1]))
                    current_line = [word]

            if current_line:
                lines.append(' '.join(current_line))

            formatted_text = '\n'.join(lines)

            txt_clip = TextClip(
                formatted_text,
                fontsize=fontsize,
                color=PRIMARY_COLOR,
                font='Arial-Bold',
                size=(VIDEO_WIDTH - 150, None),
                method='caption',
                align='center'
            )

            # Fade in/out
            txt_clip = fadein(txt_clip, 0.8)
            txt_clip = fadeout(txt_clip, 0.8)

            txt_clip = txt_clip.set_position('center')
            txt_clip = txt_clip.set_start(start_time).set_duration(duration)

            return txt_clip

        except Exception as e:
            print(f"Error creating scrolling text: {e}")
            return ColorClip(size=(1, 1), color=(0, 0, 0), duration=duration).set_opacity(0)

    def _generate_voiceover(self, text):
        """Generate AI voiceover using gTTS"""
        try:
            print("🎙️  Generating voiceover...")
            audio_path = f"{OUTPUT_DIR}/temp/voiceover_{random.randint(1000, 9999)}.mp3"

            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(audio_path)

            print(f"✅ Voiceover generated: {audio_path}")
            return audio_path

        except Exception as e:
            print(f"Error generating voiceover: {e}")
            return None

    def create_thumbnail(self, script, output_name=None):
        """Create thumbnail image for the reel"""
        img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), color=BACKGROUND_COLOR)
        draw = ImageDraw.Draw(img)

        try:
            # Try to load custom font
            font_title = ImageFont.truetype("Arial.ttf", TITLE_FONT_SIZE)
        except:
            font_title = ImageFont.load_default()

        # Draw hook text
        text = script['hook']
        # Simple text positioning (centered)
        bbox = draw.textbbox((0, 0), text, font=font_title)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((VIDEO_WIDTH - text_width) // 2, (VIDEO_HEIGHT - text_height) // 2)

        # Add shadow
        shadow_offset = 3
        draw.text(
            (position[0] + shadow_offset, position[1] + shadow_offset),
            text,
            font=font_title,
            fill=(0, 0, 0)
        )

        # Main text
        draw.text(position, text, font=font_title, fill=ACCENT_COLOR)

        # Save thumbnail
        if not output_name:
            output_name = f"thumbnail_{random.randint(1000, 9999)}.jpg"

        output_path = os.path.join(OUTPUT_DIR, output_name)
        img.save(output_path, quality=95)

        print(f"✅ Thumbnail created: {output_path}")
        return output_path


if __name__ == "__main__":
    # Test video generation
    generator = VideoGenerator()

    test_script = {
        'hook': '🚨 INSANE NBA STAT! 🚨',
        'content': 'LeBron James has played against 35% of all players in NBA history. That\'s over 1,200 different players in 21 seasons!',
        'cta': 'Follow for more crazy stats! 👆',
        'voiceover': 'Did you know LeBron James has played against 35% of all players in NBA history? That\'s over 1,200 different players across 21 seasons. Absolutely insane!',
        'category': 'NBA'
    }

    generator.create_reel(test_script, add_voiceover=True)
