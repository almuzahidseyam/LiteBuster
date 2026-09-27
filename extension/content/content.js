function injectBusterButton() {
    const container = document.querySelector('.captcha-box');
    if (!container || document.getElementById('litebuster-injected-btn')) return;

    const btn = document.createElement('button');
    btn.id = 'litebuster-injected-btn';
    btn.innerHTML = '🤖 Auto Solve (LiteBuster)';
    btn.style.marginTop = '15px';
    btn.style.background = '#10b981'; // Green color to distinguish from the original button
    btn.style.border = 'none';
    btn.style.color = 'white';
    btn.style.padding = '12px';
    btn.style.borderRadius = '6px';
    btn.style.cursor = 'pointer';
    btn.style.fontWeight = 'bold';
    btn.style.width = '100%';
    btn.style.transition = 'background 0.2s';
    
    btn.onmouseover = () => btn.style.background = '#059669';
    btn.onmouseout = () => btn.style.background = '#10b981';

    btn.onclick = () => {
        btn.innerText = '⏳ Solving...';
        // Request the background service worker or popup logic to run inference
        // For this demo, we will simulate the connection response since the model is loaded in the popup.
        // In a real advanced MV3, we'd load ONNX in the background service worker or an offscreen document.
        alert('LiteBuster: To run the actual ONNX inference, please click the Extension Icon in the Chrome toolbar. The injected button is successfully attached to the DOM!');
        btn.innerText = '🤖 Auto Solve (LiteBuster)';
    };

    container.appendChild(btn);
}

// Run on page load
injectBusterButton();

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === "FILL_CAPTCHA") {
        console.log("LiteBuster Content Script received text: " + request.text);
        const inputField = document.getElementById("captcha-input");
        if (inputField) {
            inputField.value = request.text;
            const verifyBtn = document.querySelector("button:not(#litebuster-injected-btn)");
            if (verifyBtn) verifyBtn.click();
        }
    }
});
