#!/usr/bin/env python3
import argparse
import scipy.io.wavfile as wavfile

def main():
    parser = argparse.ArgumentParser(description='Convert EPUB topics to audio using TTS.')
    parser.add_argument('--tts', type=str, choices=['bark', 'coqui'], default='bark', help='TTS engine to use')
    parser.add_argument('--voice', type=str, default=None, help='The voice to use for speech synthesis. Full list https://suno-ai.notion.site/8b8e8749ed514b0cbf3f699013548683?v=bc67cff786b04b50b3ceb756fd05f68c')
    parser.add_argument('--text', type=str, required=True, help='Text to convert to speech.')
    parser.add_argument('--output', type=str, required=True, help='Output audio file.')
    parser.add_argument('--sample-rate', type=int, default=24000, help='Sample rate for the output audio.')
    args = parser.parse_args()

    # Initialize TTS engine
    if args.tts == 'bark':
        from tts.bark_engine import BarkEngine
        tts_engine = BarkEngine(voice=args.voice)
    else:
        from tts.coqui_engine import CoquiEngine
        tts_engine = CoquiEngine()

    tts_engine.initialize()
    audio_array = tts_engine.generate_audio(args.text)
    wavfile.write(args.output, args.sample_rate, audio_array)

if __name__ == '__main__':
    main()