#!/usr/bin/env python3

import sys
import os
import argparse
import re
import subprocess

from ebooklib import epub
from ebooklib import ITEM_DOCUMENT
from bs4 import BeautifulSoup
import scipy.io.wavfile as wavfile
import numpy as np


SAMPLE_RATE = 24000

def sanitize_filename(name):
    """Sanitize the topic title to create a valid filename."""
    clean = re.sub(r'[\\/:"*?<>|]+', ' ', name)
    clean = ' '.join(clean.split())
    return clean

def generate_spectrogram_video(audio_file):
    """Generate a video with audio spectrogram visualization."""
    output_video = audio_file.replace('.wav', '.mp4')
    ffmpeg_command = [
        'ffmpeg', '-y',
        '-i', audio_file,
        '-filter_complex', '[0:a]showspectrum=s=1920x1080:mode=combined:color=rainbow:scale=log:slide=scroll:saturation=4,format=yuv420p[v]',
        '-map', '[v]',
        '-map', '0:a',
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-pix_fmt', 'yuv420p',
        output_video
    ]
    subprocess.run(ffmpeg_command)
    return output_video

def main():
    parser = argparse.ArgumentParser(description='Convert EPUB topics to audio using TTS.')
    parser.add_argument('epub_file', help='Path to the .epub file to process.')
    parser.add_argument('--tts', type=str, choices=['bark', 'coqui'], default='bark', help='TTS engine to use')
    parser.add_argument('--voice', type=str, default=None, help='The voice to use for speech synthesis.')
    parser.add_argument('--chapter', type=int, help='Process only the specified chapter number')
    parser.add_argument('--animation', action='store_true', help='Generate video with audio spectrogram')
    args = parser.parse_args()

    # Initialize TTS engine
    if args.tts == 'bark':
        from tts.bark_engine import BarkEngine
        tts_engine = BarkEngine(voice=args.voice)
    else:
        from tts.coqui_engine import CoquiEngine
        tts_engine = CoquiEngine()
    
    tts_engine.initialize()

    if not os.path.exists(args.epub_file):
        print(f'Error: File "{args.epub_file}" does not exist.')
        sys.exit(1)

    book = epub.read_epub(args.epub_file)
    topic_count = 1

    for item in book.get_items():
        if item.get_type() == ITEM_DOCUMENT:
            if args.chapter and topic_count < args.chapter:
                topic_count += 1
                continue
            if args.chapter and topic_count > args.chapter:
                break

            content = item.get_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')

            title_tag = soup.find(['h1', 'title', 'p'])
            if not title_tag:
                print('No title found in this topic.')
                continue
            title = sanitize_filename(title_tag.get_text())
            if not title:
                continue
            print(f'📕 Processing chapter: {title}')

            paragraphs = [p.get_text().strip() for p in soup.find_all('p') if p.get_text().strip()]
            if not paragraphs:
                print('No paragraphs found in this topic.')
                continue

            audio_segments = []
            for idx, paragraph in enumerate(paragraphs, start=1):
                print(f'  📄 Generating audio for paragraph {idx} of {len(paragraphs)}...')
                print('   📄 Paragraph:', paragraph)
                try:
                    audio_array = tts_engine.generate_audio(paragraph)
                    audio_segments.append(audio_array)
                    output_file = f'{topic_count}-{title}-{idx}.wav'
                    wavfile.write(output_file, SAMPLE_RATE, audio_array)
                except Exception as e:
                    print(f'    Error generating audio for paragraph {idx}: {e}')

            if not audio_segments:
                print('No audio generated for this topic.')
                continue

            combined_audio = np.concatenate([segment for segment in audio_segments])
            output_file = f'{topic_count}-{title}.wav'
            wavfile.write(output_file, SAMPLE_RATE, combined_audio)
            
            if args.animation:
                print(f'  Generating spectrogram video...')
                video_file = generate_spectrogram_video(output_file)
                print(f'  Video file created: {video_file}')
            
            topic_count += 1
            print(f'  Audio file created: {output_file}')

if __name__ == '__main__':
    main()
