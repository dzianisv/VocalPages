EchoBook

Convert your EPUB ebooks into engaging audiobooks using Bark TTS.
Description

EchoBook is a command-line tool that transforms your EPUB files into audio format. It extracts topics and paragraphs from an EPUB, uses Bark Text-to-Speech (TTS) to render each paragraph into speech, and compiles them into audio files named after their respective topics.
Features

    Topic Extraction: Processes each topic/chapter in your EPUB.
    Paragraph Splitting: Splits topics into individual paragraphs.
    Text-to-Speech Conversion: Uses Bark TTS for high-quality audio generation.
    Audio Compilation: Merges paragraph audios into one file per topic.
    Custom Filenames: Saves audio files using sanitized topic names.

Installation
Prerequisites

    Python: Version 3.7 or higher.
    FFmpeg: Required by pydub for audio processing.

Install FFmpeg

    Windows: Download from the FFmpeg website and follow the installation instructions. Add FFmpeg to your system's PATH.

    macOS: Install via Homebrew:
    bash

brew install ffmpeg

Linux (Ubuntu/Debian):
bash

    sudo apt-get install ffmpeg

Install Python Packages