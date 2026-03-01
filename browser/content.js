/**
 * AutoTyper Content Script
 * Hooking shortcuts to the engine
 */

const HOTKEYS = {
    CLIPBOARD: { ctrl: true, alt: true, key: 'v' },
    VOICE: { ctrl: true, alt: true, key: 's' },
    STOP: { ctrl: true, alt: true, key: 'x' }
};

document.addEventListener('keydown', (e) => {
    // Emergency Stop
    if (e.ctrlKey && e.altKey && e.key.toLowerCase() === HOTKEYS.STOP.key) {
        e.preventDefault();
        window.AutoTyper.forceStop();
        return;
    }

    // Clipboard Trigger
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
