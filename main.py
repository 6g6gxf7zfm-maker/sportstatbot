#!/usr/bin/env python3
"""
Instagram Reel Automation - Main CLI
Creates viral sports videos with AI
"""
import argparse
import os
import json
from datetime import datetime
from script_generator import ScriptGenerator
from video_generator import VideoGenerator
from hashtag_generator import HashtagGenerator
from config import SPORTS_CATEGORIES, VIDEO_TEMPLATES, OUTPUT_DIR


class ReelAutomation:
    def __init__(self):
        self.script_gen = ScriptGenerator()
        self.video_gen = VideoGenerator()
        self.hashtag_gen = HashtagGenerator()

    def create_single_reel(self, category=None, template=None, voiceover=True, save_metadata=True):
        """Create a single viral reel"""
        print("\n" + "="*60)
        print("🎬 INSTAGRAM REEL AUTOMATION")
        print("="*60 + "\n")

        # Step 1: Generate script
        print("📝 Step 1: Generating AI script...")
        script = self.script_gen.generate_script(category=category, template=template)

        print(f"\n✅ Script generated!")
        print(f"   Category: {script['category']}")
        print(f"   Template: {script['template']}")
        print(f"   Hook: {script['hook']}")
        print()

        # Step 2: Generate hashtags
        print("🏷️  Step 2: Generating hashtags...")
        hashtags = self.hashtag_gen.generate(
            category=script['category'],
            template=script['template'],
            count=30
        )
        script['hashtags'] = hashtags
        print(f"✅ Generated {len(hashtags)} hashtags")
        print()

        # Step 3: Create video
        print("🎥 Step 3: Creating video...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"{script['category'].lower()}_{script['template']}_{timestamp}.mp4"

        video_path = self.video_gen.create_reel(
            script,
            output_name=output_name,
            add_voiceover=voiceover
        )
        print()

        # Step 4: Save metadata
        if save_metadata:
            print("💾 Step 4: Saving metadata...")
            metadata_path = self._save_metadata(script, video_path, output_name)
            print(f"✅ Metadata saved: {metadata_path}")
            print()

        # Step 5: Display posting info
        print("="*60)
        print("✅ REEL READY FOR MANUAL POSTING!")
        print("="*60)
        print(f"\n📹 Video: {video_path}")
        print(f"\n📝 CAPTION:")
        print("-"*60)
        print(f"{script['hook']}\n")
        print(f"{script['content']}\n")
        print(f"{script['cta']}\n")
        print("\n💡 TIP: Post hashtags in FIRST COMMENT for better reach!")
        print("\n🏷️  HASHTAGS (copy to first comment):")
        print("-"*60)
        print(self.hashtag_gen.format_for_comment(hashtags))
        print("-"*60)
        print()

        return {
            'video_path': video_path,
            'script': script,
            'hashtags': hashtags
        }

    def create_batch(self, count=5, category=None, voiceover=True):
        """Create multiple reels at once"""
        print("\n" + "="*60)
        print(f"🎬 BATCH CREATION: {count} REELS")
        print("="*60 + "\n")

        results = []

        for i in range(count):
            print(f"\n>>> Creating Reel {i+1}/{count}...")
            result = self.create_single_reel(
                category=category,
                voiceover=voiceover,
                save_metadata=True
            )
            results.append(result)
            print(f"✅ Reel {i+1}/{count} complete!\n")

        # Create batch summary
        self._save_batch_summary(results)

        print("\n" + "="*60)
        print(f"✅ BATCH COMPLETE! Created {count} reels")
        print("="*60)
        print(f"\nAll videos saved to: {OUTPUT_DIR}/")
        print("Check batch_summary.json for details\n")

        return results

    def _save_metadata(self, script, video_path, output_name):
        """Save script and metadata to JSON"""
        metadata = {
            'video_file': output_name,
            'video_path': video_path,
            'created_at': datetime.now().isoformat(),
            'category': script['category'],
            'template': script['template'],
            'hook': script['hook'],
            'content': script['content'],
            'cta': script['cta'],
            'voiceover': script.get('voiceover', ''),
            'hashtags': script.get('hashtags', []),
            'caption': f"{script['hook']}\n\n{script['content']}\n\n{script['cta']}",
        }

        metadata_filename = output_name.replace('.mp4', '_metadata.json')
        metadata_path = os.path.join(OUTPUT_DIR, metadata_filename)

        with open(metadata_path, 'w') as f:
            json.dump(metadata, indent=2, fp=f)

        return metadata_path

    def _save_batch_summary(self, results):
        """Save summary of batch creation"""
        summary = {
            'created_at': datetime.now().isoformat(),
            'total_reels': len(results),
            'reels': []
        }

        for result in results:
            summary['reels'].append({
                'video_path': result['video_path'],
                'category': result['script']['category'],
                'template': result['script']['template'],
                'hook': result['script']['hook']
            })

        summary_path = os.path.join(OUTPUT_DIR, 'batch_summary.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, indent=2, fp=f)

    def list_options(self):
        """Display available categories and templates"""
        print("\n" + "="*60)
        print("📋 AVAILABLE OPTIONS")
        print("="*60)

        print("\n🏀 SPORTS CATEGORIES:")
        for i, cat in enumerate(SPORTS_CATEGORIES, 1):
            print(f"  {i}. {cat}")

        print("\n🎬 VIDEO TEMPLATES:")
        for i, template in enumerate(VIDEO_TEMPLATES, 1):
            print(f"  {i}. {template}")

        print("\n" + "="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Instagram Reel Automation - Create viral sports videos with AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a single NBA reel
  python main.py --category NBA

  # Create 5 random sports reels
  python main.py --batch 5

  # Create NFL prediction reel without voiceover
  python main.py --category NFL --template prediction --no-voiceover

  # List available options
  python main.py --list
        """
    )

    parser.add_argument(
        '--category',
        choices=SPORTS_CATEGORIES + ['random'],
        help='Sports category (random if not specified)'
    )

    parser.add_argument(
        '--template',
        choices=VIDEO_TEMPLATES + ['random'],
        help='Video template (random if not specified)'
    )

    parser.add_argument(
        '--batch',
        type=int,
        metavar='N',
        help='Create N reels in batch mode'
    )

    parser.add_argument(
        '--no-voiceover',
        action='store_true',
        help='Skip AI voiceover generation'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List available categories and templates'
    )

    args = parser.parse_args()

    automation = ReelAutomation()

    # List options
    if args.list:
        automation.list_options()
        return

    # Convert 'random' to None
    category = None if args.category == 'random' else args.category
    template = None if args.template == 'random' else args.template
    voiceover = not args.no_voiceover

    # Batch mode
    if args.batch:
        automation.create_batch(
            count=args.batch,
            category=category,
            voiceover=voiceover
        )
    else:
        # Single reel
        automation.create_single_reel(
            category=category,
            template=template,
            voiceover=voiceover
        )


if __name__ == "__main__":
    main()
