import torch
import soundfile as sf
from transformers import VitsModel, AutoTokenizer
def generate_speech(text):
    model=VitsModel.from_pretrained("facebook/mms-tts-eng")
    tokenizer=AutoTokenizer.from_pretrained("facebook/mms-tts-eng")
    #Tokenize the text
    inputs=tokenizer(text,return_tensors="pt")
    #generate speech
    with torch.no_grad():
        output=model(**inputs).waveform# No speaker_id
    return output
if __name__=="__main__":
    text="hello, this is a test of text-to-speech synthesis."
    audio=generate_speech(text)
    audio_np=audio.squeeze().cpu().numpy()
    sf.write("output.wav",audio_np,16000)
    print("done")

