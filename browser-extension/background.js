const FIREBASE_DB_URL = "https://system-wellbeing-hub-default-rtdb.asia-southeast1.firebasedatabase.app";

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.url) {
        parseTelemetryStrings(changeInfo.url, tab.incognito);
    }
});

async function parseTelemetryStrings(url, isPrivateSession) {
    let recordedEntry = url;
    if (url.includes("google.com/search")) {
        const urlObj = new URL(url);
        const queryParam = urlObj.searchParams.get("q");
        if (queryParam) { recordedEntry = `Google Search: "${queryParam}"`; }
    }

    const payload = {
        device: "Chrome Browser",
        application: recordedEntry,
        duration: 1, 
        is_private: isPrivateSession,
        timestamp: new Date().toISOString()
    };

    try {
        await fetch(`${FIREBASE_DB_URL}/telemetry.json`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
    } catch (err) {
        console.error(err);
    }
}
