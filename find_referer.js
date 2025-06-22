const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    let referer = null, origin = null;

    // Ακούμε όλα τα requests σε ΟΛΑ τα frames
    context.on('request', request => {
        if (request.url().endsWith('.m3u8') && !referer) {
            const headers = request.headers();
            if (headers['referer'] && headers['origin']) {
                referer = headers['referer'];
                origin = headers['origin'];
                console.log('REFERER=' + referer);
                console.log('ORIGIN=' + origin);
            }
        }
    });

    const page = await context.newPage();
    await page.goto('https://miztv.top/stream/stream-622.php', { waitUntil: "domcontentloaded" });

    // Προαιρετικά, κάνε scroll ή click για να ενεργοποιηθεί το player:
    // await page.mouse.move(100, 200);
    // await page.mouse.click(100, 200);

    // Περίμενε αρκετά να φορτώσουν τα requests (όσο χρειάζεται για να παίξει το stream)
    await page.waitForTimeout(15000);

    await browser.close();

    if (!referer || !origin) {
        console.error('ERROR: Did not detect referer/origin!');
        process.exit(1);
    }
})();
