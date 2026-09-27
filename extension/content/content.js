chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === "FILL_CAPTCHA") {
        console.log("LiteBuster Content Script received text: " + request.text);
        
        // Find the input field in our Demo CAPTCHA page
        const inputField = document.getElementById("captcha-input");
        if (inputField) {
            inputField.value = request.text;
            
            // Optionally auto-click the verify button
            const verifyBtn = document.querySelector("button");
            if (verifyBtn && verifyBtn.innerText.includes("Verify")) {
                verifyBtn.click();
            }
        } else {
            console.error("LiteBuster: Could not find the captcha input field on this page.");
        }
    }
});
