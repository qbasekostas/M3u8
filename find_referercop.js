const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    let referer = null, origin = null, m3u8url = null;

    context.on('request', request => {
        if (!referer && request.url().includes('.m3u8')) {
            const headers = request.headers();
            if (headers['referer'] && headers['origin']) {
                referer = headers['referer'];
                origin = headers['origin'];
                m3u8url = request.url();
                // Εκτύπωσε τα headers για χρήση στο Action
                console.log(`REF=${referer}`);
                console.log(`ORIGIN=${origin}`);
                console.log(`M3U8=${m3u8url}`);
            }
        }
    });

    const page = await context.newPage();
    await page.goto('https://miztv.top/stream/stream-622.php', { waitUntil: "domcontentloaded" });

    // Προαιρετικά, κάνε κλικ στο play αν χρειάζεται, π.χ.:
    // await page.click('button ή selector αν έχει κουμπί play/unmute');

    await page.waitForTimeout(15000); // 15 δευτερόλεπτα

    await browser.close();

    if (!referer || !origin) {
        console.error('ERROR: Did not detect referer/origin!');
        process.exit(1);
    }
})();
