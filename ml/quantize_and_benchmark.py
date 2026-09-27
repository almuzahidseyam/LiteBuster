import os
import time
import numpy as np
import onnxruntime as ort
from onnxruntime.quantization import quantize_dynamic, QuantType
import warnings
warnings.filterwarnings('ignore')

FP32_MODEL = "extension/assets/model.onnx"
INT8_MODEL = "extension/assets/model_int8.onnx"

def benchmark_model(model_path, num_runs=50):
    session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
    input_name = session.get_inputs()[0].name
    
    # Dummy input matching [1, 1, 80, 187]
    dummy_input = np.random.randn(1, 1, 80, 187).astype(np.float32)
    
    # Warmup
    for _ in range(10):
        session.run(None, {input_name: dummy_input})
        
    start_time = time.time()
    for _ in range(num_runs):
        session.run(None, {input_name: dummy_input})
    end_time = time.time()
    
    avg_latency_ms = ((end_time - start_time) / num_runs) * 1000
    file_size_mb = os.path.getsize(model_path) / (1024 * 1024)
    return file_size_mb, avg_latency_ms

def main():
    print(f"Applying Dynamic INT8 Quantization to {FP32_MODEL}...")
    quantize_dynamic(
        model_input=FP32_MODEL,
        model_output=INT8_MODEL,
        weight_type=QuantType.QUInt8
    )
    print("Quantization complete!\n")
    
    print("Running Inference Benchmark (CPU)...")
    fp32_size, fp32_lat = benchmark_model(FP32_MODEL)
    int8_size, int8_lat = benchmark_model(INT8_MODEL)
    
    print("-" * 40)
    print(f"{'Metric':<20} | {'FP32 (Original)':<10} | {'INT8 (Quantized)':<10}")
    print("-" * 40)
    print(f"{'Model Size (MB)':<20} | {fp32_size:<10.2f} | {int8_size:<10.2f}")
    print(f"{'Avg Latency (ms)':<20} | {fp32_lat:<10.2f} | {int8_lat:<10.2f}")
    print("-" * 40)
    
    size_reduction = (1 - int8_size / fp32_size) * 100
    print(f"\nSize reduced by {size_reduction:.1f}%! Perfect for Chrome Extensions.")

if __name__ == "__main__":
    main()
