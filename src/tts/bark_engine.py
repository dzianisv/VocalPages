from .base import TTSEngine
from bark import generate_audio, SAMPLE_RATE, preload_models
import numpy as np

class BarkEngine(TTSEngine):
    def __init__(self, voice="v2/en_speaker_6"):
        self.voice = voice
        
    def initialize(self):
        preload_models()
        
    def generate_audio(self, text: str) -> np.ndarray:
        return generate_audio(text, history_prompt=self.voice)
