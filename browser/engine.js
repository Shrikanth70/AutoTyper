/**
 * AutoTyper Browser Engine
 * 100% Reliable & State-Safe
 */

let currentOperationId = 0;
let textToType = "";
const TYPING_SPEED = 40; // ms

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// WebSocket Connection to Python Backend
let ws = null;
function connectWS() {
    ws = new WebSocket("ws://localhost:8765");
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.action === "type" && data.text) {
            console.log("Received text from Voice Engine:", data.text);
            startTyping(data.text);
        }
    };
    ws.onclose = () => {
        console.log("WS Connection closed. Retrying in 5s...");
        setTimeout(connectWS, 5000);
    };
    ws.onerror = (err) => console.error("WS Error:", err);
}
connectWS();

/**
 * Force Stop: Kills all active typing loops and clears buffer
 */
function forceStop() {
    currentOperationId++; // Invalidate old loops
    textToType = "";
    console.log("Typing Force Stopped. Current ID:", currentOperationId);
}

/**
 * Inserts text directly into the element value to avoid character loss
 */
function insertTextSafely(element, text) {
    const start = element.selectionStart;
    const end = element.selectionEnd;
    const value = element.value;

    // Apply modification
    element.value = value.slice(0, start) + text + value.slice(end);

    // Maintain cursor position
    const newPos = start + text.length;
    element.selectionStart = element.selectionEnd = newPos;

    // Trigger input event for frameworks like React/Vue
    element.dispatchEvent(new Event('input', { bubbles: true }));
}

/**
 * Main typing loop
 */
async function typeText(text, operationId) {
    const element = document.activeElement;

    if (!element || !(element.tagName === 'INPUT' || element.tagName === 'TEXTAREA')) {
        console.warn("No valid input/textarea found for typing.");
        return;
    }

    console.log("Typing started. Length:", text.length, "Op ID:", operationId);
    element.focus();

    for (let i = 0; i < text.length; i++) {
        // Hard-cancel check
        if (operationId !== currentOperationId) {
            console.log("Operation invalidated. Breaking loop.");
            return;
        }

        // Focus guard
        if (document.activeElement !== element) {
            element.focus();
        }

        // Insert character
        insertTextSafely(element, text[i]);

        // Awaited safe speed
        await delay(TYPING_SPEED);
    }

    // Finished
    if (operationId === currentOperationId) {
        console.log("Typing Finished Successfully.");
        forceStop(); // Reset state
    }
}

/**
 * Start a new typing operation
 */
function startTyping(newText) {
    forceStop(); // Cancel previous first

    currentOperationId++;
    const operationId = currentOperationId;
    textToType = String(newText);

    if (!textToType) return;

    // Run in background (async)
    typeText(textToType, operationId).catch(err => {
        console.error("Typing Engine Error:", err);
        forceStop();
    });
}

/**
 * Clipboard Handlers
 */
async function handlePaste() {
    try {
        const clipboardText = await navigator.clipboard.readText();
        startTyping(clipboardText);
    } catch (err) {
        console.error("Failed to read clipboard:", err);
    }
}

/**
 * Tab Visibility Stability
 */
document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
        console.log("Tab hidden. Stopping current typing task.");
        forceStop();
    }
});

// Export functions for content script
window.AutoTyper = {
    startTyping,
    forceStop,
    handlePaste
};
