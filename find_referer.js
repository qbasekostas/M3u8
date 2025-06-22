const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    let referer = null;

    // ΠΑΡΑΤΗΡΗΣΗ:
    // Άλλαξε το inspectionURL αν χρειάζεται (όποια σελίδα φορτώνει το player)
    const inspectionURL = 'https://miztv.top/stream/stream-622.php';

    // Πιάσε το πρώτο .m3u8 request και πάρε το referer header που στέλνεται
    page.on('request', request => {
        if (request.url().includes('.m3u8') && !referer) {
            referer = request.headers()['referer'] || page.url();
            // Εμφάνισε μόνο το origin (χωρίς path) αν θες:
            try {
                const url = new URL(referer);
                referer = url.origin + '/';
            } catch (e) {}
            console.log(referer);
        }
    });

    // Φόρτωσε τη σελίδα και περίμενε λίγο να ξεκινήσουν τα requests
    await page.goto(inspectionURL, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(10000);

    await browser.close();

    if (!referer) {
        console.error('ERROR: Did not detect referer!');
        process.exit(1);
    }
})();
