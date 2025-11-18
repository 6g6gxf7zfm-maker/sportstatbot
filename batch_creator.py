#!/usr/bin/env python3
"""
Batch creator - Generate multiple reels at once
"""
from simple_demo import create_simple_reel, create_text_image
from script_generator import ScriptGenerator
from hashtag_generator import HashtagGenerator
import json
import os
from datetime import datetime

def create_batch_reels():
    """Create a variety of reels for posting"""

    script_gen = ScriptGenerator()
    hashtag_gen = HashtagGenerator()

    # Define variety of content
    reel_configs = [
        {'category': 'NBA', 'template': 'stat_reveal'},
        {'category': 'NFL', 'template': 'prediction'},
        {'category': 'Soccer', 'template': 'fact_drop'},
        {'category': 'NBA', 'template': 'vs_comparison'},
        {'category': 'General Sports Facts', 'template': 'did_you_know'},
    ]

    results = []

    print("\n" + "="*70)
    print("🎬 CREATING BATCH OF INSTAGRAM REELS FOR YOUR PHONE")
    print("="*70 + "\n")

    for i, config in enumerate(reel_configs, 1):
        print(f"\n>>> Creating Reel {i}/{len(reel_configs)}")
        print(f"    Category: {config['category']}")
        print(f"    Template: {config['template']}")
        print("-" * 70)

        # Generate script
        script = script_gen.generate_script(
            category=config['category'],
            template=config['template']
        )

        # Generate hashtags
        hashtags = hashtag_gen.generate(
            category=script['category'],
            template=script['template']
        )
        script['hashtags'] = hashtags

        # Create video
        video_path = create_simple_reel(script, add_voiceover=False)

        # Save result info
        result = {
            'number': i,
            'video_path': video_path,
            'category': script['category'],
            'template': script['template'],
            'caption': f"{script['hook']}\n\n{script['content']}\n\n{script['cta']}",
            'hashtags': hashtag_gen.format_for_comment(hashtags)
        }
        results.append(result)

        print(f"✅ Reel {i} complete: {video_path}\n")

    # Save posting guide
    guide_path = 'output/POSTING_GUIDE.txt'
    with open(guide_path, 'w') as f:
        f.write("="*70 + "\n")
        f.write("📱 INSTAGRAM POSTING GUIDE\n")
        f.write("="*70 + "\n\n")
        f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Reels: {len(results)}\n\n")

        for result in results:
            f.write(f"\n{'='*70}\n")
            f.write(f"REEL #{result['number']} - {result['category']} ({result['template']})\n")
            f.write(f"{'='*70}\n\n")
            f.write(f"📹 FILE: {result['video_path']}\n\n")
            f.write(f"📝 CAPTION:\n{'-'*70}\n")
            f.write(f"{result['caption']}\n")
            f.write(f"{'-'*70}\n\n")
            f.write(f"🏷️  HASHTAGS (paste in first comment):\n{'-'*70}\n")
            f.write(f"{result['hashtags']}\n")
            f.write(f"{'-'*70}\n\n")

    # Summary
    print("\n" + "="*70)
    print("✅ BATCH COMPLETE!")
    print("="*70)
    print(f"\n✨ Created {len(results)} reels ready for posting!\n")

    for result in results:
        print(f"  {result['number']}. {os.path.basename(result['video_path'])}")
        print(f"     → {result['category']} - {result['template']}")

    print(f"\n📋 Posting guide saved: {guide_path}")
    print(f"📁 All videos in: output/\n")

    print("📱 TO GET VIDEOS ON YOUR PHONE:")
    print("   Option 1: Download files from the output/ folder")
    print("   Option 2: Use 'ls output/*.mp4' to see all video files")
    print("   Option 3: Transfer via USB/cloud storage to your phone\n")

    return results

if __name__ == "__main__":
    create_batch_reels()
