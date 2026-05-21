chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.url) {
        parseTelemetryStrings(changeInfo.url, tab.incognito);
    }
});

function parseTelemetryStrings(url, isPrivateSession) {
    const timestamp = new Date().toISOString();
    let recordedEntry = url;

    // Filter out structured query terms directly from common search strings
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

    console.log("[METRIC CONSOLE LOGGER]:", logPayload);
    // CONNECTIVE SYNC NODE: Implement dynamic API routing standard fetch() requests here to forward to remote datastores
}
