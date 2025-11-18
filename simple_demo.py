#!/usr/bin/env python3
"""
Simple Demo - Creates a basic Instagram Reel using fallback methods
This bypasses moviepy text rendering issues by using PIL directly
"""
import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoClip, AudioFileClip, CompositeVideoClip
from gtts import gTTS
from script_generator import ScriptGenerator
from hashtag_generator import HashtagGenerator
from config import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, OUTPUT_DIR
from datetime import datetime


def create_text_image(text, width, height, fontsize=60, color=(255, 255, 255)):
    """Create an image with text using PIL"""
    img = Image.new('RGB', (width, height), color=(20, 20, 30))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", fontsize)
    except:
        font = ImageFont.load_default()

    # Simple text wrapping
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] < width - 100:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    # Draw text centered
    y_offset = (height - len(lines) * (fontsize + 10)) // 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2

        # Shadow
        draw.text((x + 2, y_offset + 2), line, font=font, fill=(0, 0, 0))
        # Main text
        draw.text((x, y_offset), line, font=font, fill=color)
        y_offset += fontsize + 10

    return np.array(img)


def create_simple_reel(script, add_voiceover=False):
    """Create a simple reel using PIL for text rendering"""
    print("🎬 Creating simple Instagram Reel...")

    duration = 20  # 20 second video

    # Generate voiceover if requested
    audio_clip = None
    if add_voiceover and script.get('voiceover'):
        try:
            print("🎙️  Generating voiceover...")
            audio_path = f"{OUTPUT_DIR}/temp/voiceover_{random.randint(1000, 9999)}.mp3"
            os.makedirs(f"{OUTPUT_DIR}/temp", exist_ok=True)

            tts = gTTS(text=script['voiceover'], lang='en', slow=False)
            tts.save(audio_path)

            audio_clip = AudioFileClip(audio_path)
            duration = min(max(audio_clip.duration, 15), 30)
            print(f"✅ Voiceover generated")
        except Exception as e:
            print(f"⚠️  Could not generate voiceover: {e}")

    # Create frames for different sections
    hook_img = create_text_image(script['hook'], VIDEO_WIDTH, VIDEO_HEIGHT,
                                  fontsize=70, color=(255, 215, 0))  # Gold
    content_img = create_text_image(script['content'], VIDEO_WIDTH, VIDEO_HEIGHT,
                                      fontsize=50, color=(255, 255, 255))  # White
    cta_img = create_text_image(script['cta'], VIDEO_WIDTH, VIDEO_HEIGHT,
                                 fontsize=55, color=(255, 255, 255))  # White

    def make_frame(t):
        """Generate frame based on time"""
        if t < 5:
            # Show hook
            return hook_img
        elif t < duration - 4:
            # Show content
            return content_img
        else:
            # Show CTA
            return cta_img

    # Create video clip
    video = VideoClip(make_frame, duration=duration)
    video = video.with_fps(VIDEO_FPS)

    # Add audio if available
    if audio_clip:
        video = video.with_audio(audio_clip)

    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_name = f"{script.get('category', 'sports').lower()}_{script.get('template', 'reel')}_{timestamp}.mp4"
    output_path = os.path.join(OUTPUT_DIR, output_name)

    # Render video
    print(f"📹 Rendering video: {output_name}")
    video.write_videofile(
        output_path,
        fps=VIDEO_FPS,
        codec='libx264',
        audio_codec='aac' if audio_clip else None,
        preset='medium',
        logger=None  # Suppress verbose output
    )

    # Cleanup
    video.close()
    if audio_clip:
        audio_clip.close()
        try:
            os.remove(audio_path)
        except:
            pass

    print(f"✅ Video created: {output_path}")
    return output_path


def main():
    print("\n" + "="*60)
    print("🎬 SIMPLE INSTAGRAM REEL DEMO")
    print("="*60 + "\n")

    # Generate script
    print("📝 Generating script...")
    script_gen = ScriptGenerator()
    script = script_gen.generate_script(category='NBA', template='stat_reveal')

    print(f"✅ Script generated!")
    print(f"   Hook: {script['hook']}\n")

    # Generate hashtags
    print("🏷️  Generating hashtags...")
    hashtag_gen = HashtagGenerator()
    hashtags = hashtag_gen.generate(category=script['category'], template=script['template'])
    script['hashtags'] = hashtags
    print(f"✅ Generated {len(hashtags)} hashtags\n")

    # Create video
    print("🎥 Creating video...")
    video_path = create_simple_reel(script, add_voiceover=True)

    # Display results
    print("\n" + "="*60)
    print("✅ REEL READY FOR MANUAL POSTING!")
    print("="*60)
    print(f"\n📹 Video: {video_path}")
    print(f"\n📝 CAPTION:")
    print("-"*60)
    print(f"{script['hook']}\n")
    print(f"{script['content']}\n")
    print(f"{script['cta']}\n")
    print("\n🏷️  HASHTAGS (copy to first comment):")
    print("-"*60)
    print(hashtag_gen.format_for_comment(hashtags))
    print("-"*60)
    print()


if __name__ == "__main__":
    main()
