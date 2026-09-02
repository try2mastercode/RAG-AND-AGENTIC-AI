import torch
import soundfile as sf
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

def transcribe_audio(audio_path):
    processor=Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
    model=Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

    speech,sample_rate=sf.read(audio_path)
    inputs=processor(speech,sampling_rate=sample_rate,return_tensors="pt")

    with torch.no_grad():
        logits=model(inputs.input_values).logits

    predicted_ids=torch.argmax(logits,dim=-1)
    transcription=processor.batch_decode(predicted_ids)
    return transcription[0]
text=transcribe_audio("output.wav")
print(f"transcription: {text}")
