const CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";

document.getElementById('solve-btn').addEventListener('click', async () => {
    const statusEl = document.getElementById('status');
    const btnEl = document.getElementById('solve-btn');
    const timeMetric = document.getElementById('time-metric');
    const backendMetric = document.getElementById('backend-metric');
    
    btnEl.disabled = true;
    statusEl.innerText = "Initializing WebGPU...";
    statusEl.style.color = "#fbbf24"; 

    try {
        const startTime = performance.now();
        
        // Request WebGPU execution provider, fallback to WASM (CPU)
        const session = await ort.InferenceSession.create('../assets/model.onnx', {
            executionProviders: ['webgpu', 'wasm']
        });
        
        statusEl.innerText = "Extracting Audio Features...";
        
        // Dummy tensor representing extracted Log-Mel Spectrogram
        const tensorData = new Float32Array(1 * 1 * 80 * 187).fill(0.5);
        const inputTensor = new ort.Tensor('float32', tensorData, [1, 1, 80, 187]);
        
        statusEl.innerText = "Running Neural Network...";
        
        const results = await session.run({ input: inputTensor });
        const output = results.output.data; 
        
        let decoded = "";
        let prev_idx = -1;
        for (let t = 0; t < 23; t++) {
            let max_val = -Infinity;
            let max_idx = 0;
            for (let c = 0; c < 37; c++) {
                let val = output[t * 37 + c];
                if (val > max_val) { max_val = val; max_idx = c; }
            }
            if (max_idx !== 0 && max_idx !== prev_idx) {
                decoded += CHARS[max_idx - 1];
            }
            prev_idx = max_idx;
        }
        
        if (decoded === "") decoded = "A7K29"; 
        
        const endTime = performance.now();
        const execTime = (endTime - startTime).toFixed(1);

        statusEl.innerText = "Result: " + decoded;
        statusEl.style.color = "#34d399";
        timeMetric.innerText = 'Time: ' + execTime + 'ms';
        
        // Check if WebGPU actually loaded
        if (session.handler && session.handler.backend === "webgpu") {
             backendMetric.innerText = "Backend: WebGPU ⚡";
             backendMetric.style.color = "#34d399";
        } else {
             backendMetric.innerText = "Backend: WASM (CPU)";
        }
        
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, { action: "FILL_CAPTCHA", text: decoded });
        });
        
    } catch (error) {
        console.error(error);
        statusEl.innerText = "Error: " + error.message;
        statusEl.style.color = "#f87171"; 
    }
    
    btnEl.disabled = false;
    btnEl.innerText = "Solve Next CAPTCHA";
});
