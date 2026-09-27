import os
import torch
import torch.nn as nn
import torch.optim as optim
import torchaudio
import pandas as pd
import soundfile as sf

CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CHAR_MAP = {c: i+1 for i, c in enumerate(CHARS)}

class LiteBusterModel(nn.Module):
    def __init__(self, num_classes=37):
        super().__init__()
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)
        )
        self.gru = nn.GRU(1280, 128, bidirectional=True, batch_first=True)
        self.fc = nn.Linear(256, num_classes)
        
    def forward(self, x):
        x = self.cnn(x)
        B, C, H, W = x.size()
        x = x.view(B, C * H, W)
        x = x.permute(0, 2, 1)
        
        x, _ = self.gru(x)
        x = self.fc(x)
        return x

class AudioDataset(torch.utils.data.Dataset):
    def __init__(self, csv_path, audio_dir):
        self.df = pd.read_csv(csv_path) if os.path.exists(csv_path) else pd.DataFrame(columns=["file", "text"])
        self.audio_dir = audio_dir
        self.mel_spec = torchaudio.transforms.MelSpectrogram(sample_rate=16000, n_fft=1024, hop_length=256, n_mels=80)
        self.target_length = 48000

    def __len__(self): return len(self.df)
        
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        file_path = os.path.join(self.audio_dir, row['file'])
        
        # Load audio bypassing torchaudio.load to avoid backend issues on Windows
        waveform, sr = sf.read(file_path)
        waveform = torch.tensor(waveform, dtype=torch.float32).unsqueeze(0)
        
        if waveform.shape[1] > self.target_length:
            waveform = waveform[:, :self.target_length]
        else:
            padding = self.target_length - waveform.shape[1]
            waveform = torch.nn.functional.pad(waveform, (0, padding))
            
        mel = self.mel_spec(waveform)
        mel = torch.log(mel + 1e-9)
        
        text = str(row['text'])
        target = torch.tensor([CHAR_MAP[c] for c in text], dtype=torch.long)
        return mel, target

def train_and_export():
    print("Loading synthetic dataset...")
    dataset = AudioDataset("ml/dataset/train_metadata.csv", "ml/dataset/train")
    if len(dataset) == 0:
        return

    dataloader = torch.utils.data.DataLoader(dataset, batch_size=4, shuffle=True)
    model = LiteBusterModel()
    
    criterion = nn.CTCLoss(blank=0, zero_infinity=True)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    print("Starting Training (1 Epoch for demonstration)...")
    model.train()
    for inputs, targets in dataloader:
        optimizer.zero_grad()
        outputs = model(inputs)
        outputs = outputs.permute(1, 0, 2)
        
        batch_size = inputs.size(0)
        input_lengths = torch.full((batch_size,), 23, dtype=torch.long)
        target_lengths = torch.full((batch_size,), 5, dtype=torch.long)
        
        loss = criterion(outputs, targets, input_lengths, target_lengths)
        loss.backward()
        optimizer.step()
        
    print(f"Training completed. Final Loss: {loss.item():.4f}")
    
    print("Exporting model to ONNX Runtime format...")
    model.eval()
    dummy_input = torch.randn(1, 1, 80, 187)
    os.makedirs("extension/assets", exist_ok=True)
    
    torch.onnx.export(
        model, dummy_input, "extension/assets/model.onnx",
        export_params=True, opset_version=14,
        input_names=['input'], output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    print("Successfully saved to extension/assets/model.onnx!")

if __name__ == "__main__":
    train_and_export()
