const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    let found = false;

    page.on('request', request => {
        if (!found && request.url().includes('.m3u8')) {
            const headers = request.headers();
            if (headers['referer'] && headers['origin']) {
                // Εμφάνισε για να το πάρει το workflow σου
                console.log('REFERER=' + headers['referer']);
                console.log('ORIGIN=' + headers['origin']);
                found = true;
            }
        }
    });

    // Άλλαξε εδώ το URL αν αλλάξει σημείο το stream
    await page.goto('https://miztv.top/stream/stream-622.php', { waitUntil: "domcontentloaded" });

    // Αν απαιτείται click για να ξεκινήσει το stream, κάνε το:
    // await page.click('button ή selector που ξεκινά το player');

    await page.waitForTimeout(10000);

    await browser.close();

    if (!found) {
        console.error('ERROR: Did not detect referer/origin!');
        process.exit(1);
    }
})();
