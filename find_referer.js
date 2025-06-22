const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    let found = false;

    // Πιάσε όλα τα requests στη σελίδα
    page.on('request', request => {
        const url = request.url();
        if (!found && url.endsWith('.m3u8')) {
            const headers = request.headers();
            if (headers['referer'] && headers['origin']) {
                // Εκτυπώνει και τα δύο για το GitHub Actions/Workflow σου
                console.log('REFERER=' + headers['referer']);
                console.log('ORIGIN=' + headers['origin']);
                found = true;
            }
        }
    });

    // Βήμα 1: Άνοιξε τη σελίδα
    await page.goto('https://miztv.top/stream/stream-622.php', { waitUntil: "domcontentloaded" });

    // Βήμα 2: Περίμενε να φορτώσει το iframe
    const iframeElement = await page.waitForSelector('iframe', {timeout: 15000});
    const frame = await iframeElement.contentFrame();

    // Βήμα 3: Προσπάθησε να κάνεις click στο play/unmute αν υπάρχει κουμπί (προσαρμόζεις το selector)
    try {
        await frame.click('button, .vjs-big-play-button, .clappr-play-pause-button', {timeout: 5000});
    } catch (e) {
        // Αν δεν υπάρχει κουμπί, συνέχισε
    }

    // Βήμα 4: Περίμενε να γίνουν τα requests
    await page.waitForTimeout(10000); // 10 δευτερόλεπτα

    await browser.close();

    if (!found) {
        console.error('ERROR: Did not detect referer/origin!');
        process.exit(1);
    }
})();
