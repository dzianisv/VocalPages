#!/usr/bin/env python3

import sys
import os
import argparse
import re

from ebooklib import epub
from bs4 import BeautifulSoup
from bark import generate_audio, SAMPLE_RATE, preload_models
import soundfile as sf
from pydub import AudioSegment

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

    # Preload Bark models
    print('Loading Bark TTS models...')
    preload_models()

    # Load the EPUB file
    book = epub.read_epub(epub_file)

    # Process each document item (chapter/topic) in the EPUB
    for item in book.get_items():
        if item.get_type() == epub.ITEM_DOCUMENT:
            # Extract content and parse with BeautifulSoup
            content = item.get_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')

            # Get the topic title
            title_tag = soup.find(['h1', 'title'])
            if not title_tag:
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
                    audio_array = generate_audio(paragraph)
                    audio_segment = AudioSegment(
                        audio_array.tobytes(),
                        frame_rate=SAMPLE_RATE,
                        sample_width=audio_array.dtype.itemsize,
                        channels=1
                    )
                    audio_segments.append(audio_segment)
                except Exception as e:
                    print(f'    Error generating audio for paragraph {idx}: {e}')

            if not audio_segments:
                print('No audio generated for this topic.')
                continue

            # Combine all audio segments into one file
            combined_audio = sum(audio_segments)
            output_file = f'{title}.wav'
            combined_audio.export(output_file, format='wav')
            print(f'  Audio file created: {output_file}')

if __name__ == '__main__':
    main()