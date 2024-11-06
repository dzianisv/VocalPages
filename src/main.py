#!/usr/bin/env python3

import sys
import os
import argparse
import re

from ebooklib import epub
from ebooklib import ITEM_DOCUMENT

from bs4 import BeautifulSoup
from bark import generate_audio, SAMPLE_RATE, preload_models
import scipy.io.wavfile as wavfile
import numpy as np

def sanitize_filename(name):
    """Sanitize the topic title to create a valid filename."""
    return re.sub(r'[\\/:"*?<>|]+', '', name).strip()

def main():
    parser = argparse.ArgumentParser(description='Convert EPUB topics to audio using Bark TTS.')
    parser.add_argument('epub_file', help='Path to the .epub file to process.')
    args = parser.parse_args()
    epub_file = args.epub_file

    if not os.path.exists(epub_file):
        print(f'Error: File "{epub_file}" does not exist.')
        sys.exit(1)

    book = epub.read_epub(epub_file)
    # Process each document item (chapter/topic) in the EPUB
    for item in book.get_items():
        if item.get_type() == ITEM_DOCUMENT:
            # Extract content and parse with BeautifulSoup
            content = item.get_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')

            # Get the topic title
            title_tag = soup.find(['h1', 'title', 'p'])
            if not title_tag:
                print('No title found in this topic.')
                continue  # Skip if no title is found
            title = sanitize_filename(title_tag.get_text())
            if not title:
                continue  # Skip if title is empty after sanitization
            print(f'\nProcessing topic: {title}')

            # Extract paragraphs
            paragraphs = [p.get_text().strip() for p in soup.find_all('p') if p.get_text().strip()]
            if not paragraphs:
                print('No paragraphs found in this topic.')
                continue

            audio_segments = []
            # Generate audio for each paragraph
            for idx, paragraph in enumerate(paragraphs, start=1):
                print(f'  Generating audio for paragraph {idx} of {len(paragraphs)}...')
                try:
                    preload_models()

                    audio_array = generate_audio(paragraph, history_prompt="v2/en_speaker_1")
                    audio_segments.append(audio_array)
                except Exception as e:
                    print(f'    Error generating audio for paragraph {idx}: {e}')

            if not audio_segments:
                print('No audio generated for this topic.')
                continue

            # Combine all audio segments into one file
            combined_audio = np.concatenate([segment for segment in audio_segments])
            output_file = f'{title}.wav'
            wavfile.write(output_file, SAMPLE_RATE, combined_audio)
            
            print(f'  Audio file created: {output_file}')

if __name__ == '__main__':
    main()