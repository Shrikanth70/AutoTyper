/**
 * AutoTyper Background Service Worker
 */

chrome.runtime.onInstalled.addListener(() => {
    console.log("AutoTyper Pro Extension Installed.");
});

// Listener for messages from popup or content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "ping") {
        sendResponse({ status: "alive" });
    }
});
