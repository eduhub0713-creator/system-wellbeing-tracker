chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.url) {
        parseTelemetry(changeInfo.url, tab.incognito);
    }
});

function parseTelemetry(url, isPrivateSession) {
    const timestamp = new Date().toISOString();
    let recordedEntry = url;

    // Isolate Search Queries out of common engines
    if (url.includes("google.com/search")) {
        const urlObj = new URL(url);
        const queryParam = urlObj.searchParams.get("q");
        if (queryParam) {
            recordedEntry = `Google Search Phrase: "${queryParam}"`;
        }
    }

    const logPayload = {
        time: timestamp,
        data: recordedEntry,
        incognitoAlert: isPrivateSession
    };

    console.log("[TELEMETRY CAPTURED]:", logPayload);
    // CONNECTIVE NODE: Use standard fetch() calls to forward this JSON array straight to your API
}