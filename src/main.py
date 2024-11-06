#!/usr/bin/env python3

import sys
import os
import argparse
import re

from ebooklib import epub
from ebooklib import ITEM_DOCUMENT
from bs4 import BeautifulSoup
import scipy.io.wavfile as wavfile
import numpy as np

from tts.bark_engine import BarkEngine
from tts.coqui_engine import CoquiEngine

SAMPLE_RATE = 24000  # Move this to a config file in a real project

def sanitize_filename(name):
    """Sanitize the topic title to create a valid filename."""
    clean = re.sub(r'[\\/:"*?<>|]+', ' ', name)
    clean = ' '.join(clean.split())
    return clean

def main():
    parser = argparse.ArgumentParser(description='Convert EPUB topics to audio using TTS.')
    parser.add_argument('epub_file', help='Path to the .epub file to process.')
    parser.add_argument('--engine', type=str, choices=['bark', 'coqui'], default='bark', help='TTS engine to use')
    parser.add_argument('--voice', type=str, default='v2/en_speaker_6', help='The voice to use for speech synthesis.')
    args = parser.parse_args()

    # Initialize TTS engine
    if args.engine == 'bark':
        tts_engine = BarkEngine(voice=args.voice)
    else:
        tts_engine = CoquiEngine()
    
    tts_engine.initialize()

    if not os.path.exists(args.epub_file):
        print(f'Error: File "{args.epub_file}" does not exist.')
        sys.exit(1)

    book = epub.read_epub(args.epub_file)
    topic_count = 1

    for item in book.get_items():
        if item.get_type() == ITEM_DOCUMENT:
            content = item.get_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')

            title_tag = soup.find(['h1', 'title', 'p'])
            if not title_tag:
                print('No title found in this topic.')
                continue
            title = sanitize_filename(title_tag.get_text())
            if not title:
                continue
            print(f'\nProcessing topic: {title}')

            paragraphs = [p.get_text().strip() for p in soup.find_all('p') if p.get_text().strip()]
            if not paragraphs:
                print('No paragraphs found in this topic.')
                continue

            audio_segments = []
            for idx, paragraph in enumerate(paragraphs, start=1):
                print(f'  Generating audio for paragraph {idx} of {len(paragraphs)}...')
                try:
                    audio_array = tts_engine.generate_audio(paragraph)
                    audio_segments.append(audio_array)
                except Exception as e:
                    print(f'    Error generating audio for paragraph {idx}: {e}')

            if not audio_segments:
                print('No audio generated for this topic.')
                continue

            combined_audio = np.concatenate([segment for segment in audio_segments])
            output_file = f'{topic_count}-{title}.wav'
            wavfile.write(output_file, SAMPLE_RATE, combined_audio)
            topic_count += 1
            
            print(f'  Audio file created: {output_file}')

if __name__ == '__main__':
    main()