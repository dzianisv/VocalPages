import numpy as np
from TTS.api import TTS

class CoquiEngine:
    def __init__(self, model_name="tts_models/en/ljspeech/fast_pitch"):
        self.model_name = model_name
        self.tts = None
        
    def initialize(self):
        self.tts = TTS(model_name=self.model_name)
        
    def generate_audio(self, text: str) -> np.ndarray:
        return self.tts.tts(text)
