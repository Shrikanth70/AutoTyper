/**
 * AutoTyper Content Script
 * Hooking shortcuts to the engine
 */

const HOTKEYS = {
    COPY: { key: 'f8' },
    CLIPBOARD: { ctrl: true, alt: true, key: 'v' },
    VOICE: { ctrl: true, alt: true, key: 's' },
    STOP: { key: 'f9' }
};

document.addEventListener('keydown', (e) => {
    // Emergency Stop
    if (e.key.toLowerCase() === HOTKEYS.STOP.key) {
        e.preventDefault();
        window.AutoTyper.forceStop();
        return;
    }

    // Copy selected text
    if (e.key.toLowerCase() === HOTKEYS.COPY.key) {
        e.preventDefault();
        window.AutoTyper.handleCopy();
        return;
    }

    // Clipboard typing trigger
    if (e.ctrlKey && e.altKey && e.key.toLowerCase() === HOTKEYS.CLIPBOARD.key) {
        e.preventDefault();
        window.AutoTyper.handlePaste();
        return;
    }

    // Voice Trigger (Placeholder for future voice handling logic)
    if (e.ctrlKey && e.altKey && e.key.toLowerCase() === HOTKEYS.VOICE.key) {
        e.preventDefault();
        console.log("Voice trigger detected. (Browser voice implementation pending integration)");
        // window.AutoTyper.startVoice(); // Would be implemented similarly
    }
});
