# LiteBuster 🤖⚡

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Chrome Extension](https://img.shields.io/badge/Chrome-Manifest_V3-green.svg)
![ONNX Runtime](https://img.shields.io/badge/ONNX-WebGPU-orange.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-Model-red.svg)

**LiteBuster** is a lightweight, on-device audio CAPTCHA solver built as a Google Chrome Extension (Manifest V3). It demonstrates end-to-end Machine Learning deployment by combining a custom PyTorch acoustic model, ONNX Runtime WebGPU, and modern browser extension APIs.

*Note: This project is explicitly designed for research, accessibility demonstrations, and portfolio showcase. It solves a synthetic local CAPTCHA and does not target real-world commercial anti-bot systems.*

## ✨ Features
* **On-Device Inference:** Runs completely locally in the browser. No cloud APIs, no external servers, ensuring 100% privacy.
* **Hardware Acceleration:** Utilizes **WebGPU** via ONNX Runtime Web for blazing-fast neural network execution directly on your graphics card.
* **Modern Extension UI:** Built with the Chrome **Side Panel API** for a persistent, modern AI assistant experience.
* **Live Audio Visualizer:** Uses the Web Audio API to render real-time frequency waveforms on an HTML5 canvas.
* **Automated DOM Injection:** Automatically injects an "Auto Solve" button into the target CAPTCHA page.

## 🧠 Machine Learning Architecture
* **Dataset:** Synthetically generated audio dataset using gTTS and librosa (pitch shifting, time stretching, background noise).
* **Model:** CNN-BiGRU hybrid architecture.
  * **Input:** Log-Mel Spectrogram (80 mels).
  * **Feature Extraction:** 3-layer 2D Convolutional Neural Network (CNN).
  * **Sequence Modeling:** Bidirectional Gated Recurrent Unit (BiGRU).
  * **Decoding:** Connectionist Temporal Classification (CTC).
* **Export:** Exported to model.onnx (FP32) for browser compatibility.

## 📂 Repository Structure
* /demo - Local Flask server that generates the synthetic Audio CAPTCHA challenge and visualizer.
* /ml - Python scripts for dataset generation, PyTorch model training, ONNX export, and quantization benchmarking.
* /extension - The Manifest V3 Chrome Extension containing the UI, Background Service Worker, Content Scripts, and ONNX Runtime libraries.

## 🚀 How to Run Locally

### 1. Start the Demo Server
`ash
cd demo
python app.py
`
*Open http://127.0.0.1:5000 in your browser to see the CAPTCHA target.*

### 2. Install the Chrome Extension
1. Open Google Chrome and go to chrome://extensions/.
2. Enable **Developer mode** in the top right corner.
3. Click **Load unpacked** and select the LiteBuster/extension/ folder.
4. Click the LiteBuster icon in your Chrome toolbar to open the Side Panel.

### 3. Test the Solver
Play the audio on the demo page, then click the injected **🤖 Auto Solve (LiteBuster)** button, or click **Initialize Hardware & Solve** in the Side Panel!

## 🏷️ GitHub Topics & Tags
machine-learning chrome-extension onnx-runtime webgpu pytorch udio-processing speech-recognition manifest-v3 ctc-loss

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
