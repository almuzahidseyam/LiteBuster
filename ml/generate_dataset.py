import os
import random
import string
import pandas as pd
import numpy as np
import librosa
import soundfile as sf
from gtts import gTTS
import warnings

# Suppress librosa warnings
warnings.filterwarnings('ignore')

DATASET_DIR = "ml/dataset"
NUM_BASE_SAMPLES = 10  # Note: Set this to 1000 or 5000 for actual model training

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def add_noise(data, noise_factor=0.01):
    noise = np.random.randn(len(data))
    return data + noise_factor * noise

def generate_sample(text, split_dir, file_idx):
    # 1. Generate base TTS audio
    spoken_text = ' '.join(list(text))
    tts = gTTS(text=spoken_text, lang='en', slow=True)
    
    temp_file = f"temp_{file_idx}.mp3"
    tts.save(temp_file)
    
    # 2. Load the audio file using Librosa
    y, sr = librosa.load(temp_file, sr=16000)
    os.remove(temp_file)
    
    # 3. Create Audio Augmentations
    variations = {
        "clean": y,
        "noisy": add_noise(y, 0.015),
        "fast": librosa.effects.time_stretch(y, rate=1.2),
        "slow": librosa.effects.time_stretch(y, rate=0.85)
    }
    
    records = []
    for var_name, audio_data in variations.items():
        filename = f"audio_{file_idx:05d}_{var_name}.wav"
        filepath = os.path.join(DATASET_DIR, split_dir, filename)
        
        # Save as standard WAV file for training
        sf.write(filepath, audio_data, sr)
        records.append({"file": filename, "text": text})
        
    return records

def main():
    print(f"Starting Dataset Generation ({NUM_BASE_SAMPLES} base samples * 4 augmentations)...")
    splits = ['train', 'validation', 'test']
    for s in splits:
        ensure_dir(os.path.join(DATASET_DIR, s))
        
    metadata = {s: [] for s in splits}
    
    for i in range(NUM_BASE_SAMPLES):
        # Generate random 5-character string
        text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        
        # Split distribution: 80% train, 10% validation, 10% test
        r = random.random()
        if r < 0.8:
            split = 'train'
        elif r < 0.9:
            split = 'validation'
        else:
            split = 'test'
            
        print(f"[{i+1}/{NUM_BASE_SAMPLES}] Generating '{text}' for {split} set...")
        records = generate_sample(text, split, i)
        metadata[split].extend(records)
        
    # Save CSV metadata mapping files
    for s in splits:
        if metadata[s]:
            df = pd.DataFrame(metadata[s])
            df.to_csv(os.path.join(DATASET_DIR, f"{s}_metadata.csv"), index=False)
            
    print("Dataset generation complete!")
    print(f"Audio files saved in: {os.path.abspath(DATASET_DIR)}")

if __name__ == "__main__":
    main()
