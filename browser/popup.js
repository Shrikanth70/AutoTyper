/**
 * AutoTyper Popup Script
 */

document.getElementById('force-stop').addEventListener('click', async () => {
    // Send message to active tab to trigger forceStop
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab) {
        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => {
                if (window.AutoTyper) {
                    window.AutoTyper.forceStop();
                }
            }
        });
    }
});
