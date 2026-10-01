import os
import random
import string
import pandas as pd
import numpy as np
import librosa
import soundfile as sf
from gtts import gTTS
import warnings
from audiomentations import Compose, AddGaussianNoise, TimeStretch, PitchShift, RoomSimulator, BandPassFilter, Padding

# Suppress warnings
warnings.filterwarnings('ignore')

DATASET_DIR = "ml/dataset"
NUM_BASE_SAMPLES = 10  # Note: Set this to 1000 or 5000 for actual model training

# Advanced Augmentation Pipeline
augmenter = Compose([
    AddGaussianNoise(min_amplitude=0.001, max_amplitude=0.015, p=0.5),
    TimeStretch(min_rate=0.8, max_rate=1.2, p=0.5),
    PitchShift(min_semitones=-2, max_semitones=2, p=0.5),
    RoomSimulator(p=0.3),  # Reverb
    BandPassFilter(min_center_freq=200, max_center_freq=4000, p=0.4), # Band-pass
    Padding(mode="silence", min_fraction=0.05, max_fraction=0.1, pad_section="end", p=0.3) # Silence Insertion
])

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_sample(text, split_dir, file_idx):
    spoken_text = ' '.join(list(text))
    tts = gTTS(text=spoken_text, lang='en', slow=True)
    
    temp_file = f"temp_{file_idx}.mp3"
    tts.save(temp_file)
    
    y, sr = librosa.load(temp_file, sr=16000)
    os.remove(temp_file)
    
    # Generate variations using advanced audiomentations
    variations = {
        "clean": y,
        "aug_1": augmenter(samples=y, sample_rate=sr),
        "aug_2": augmenter(samples=y, sample_rate=sr),
        "aug_3": augmenter(samples=y, sample_rate=sr)
    }
    
    records = []
    for var_name, audio_data in variations.items():
        filename = f"audio_{file_idx:05d}_{var_name}.wav"
        filepath = os.path.join(DATASET_DIR, split_dir, filename)
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
