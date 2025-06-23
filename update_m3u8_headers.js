const { chromium } = require('playwright');
const fs = require('fs');

// Πάρε το stream URL και το αρχείο m3u8 από τα arguments ή βάλε default
const STREAM_URL = process.argv[2] || 'https://miztv.top/stream/stream-622.php';
const M3U8_FILE = process.argv[3] || 'GreekSportsChannels.m3u8';

(async () => {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    let referer = null, origin = null, found = false;

    context.on('request', request => {
        if (!found && request.url().includes('.m3u8')) {
            const headers = request.headers();
            if (headers['referer'] && headers['origin']) {
                referer = headers['referer'];
                origin = headers['origin'];
                found = true;
                console.log(`ΝΕΟ Referer: ${referer}`);
                console.log(`ΝΕΟ Origin: ${origin}`);
            }
        }
    });

    const page = await context.newPage();
    await page.goto(STREAM_URL, { waitUntil: "domcontentloaded" });

    // Προσπάθησε να κάνεις click σε κουμπιά play/mute αν υπάρχουν
    try { await page.click('button'); } catch(e) {}
    try { await page.keyboard.press('Space'); } catch(e) {}

    await page.waitForTimeout(25000);

    await browser.close();

    if (!referer || !origin) {
        console.error('ERROR: Δεν βρέθηκε referer/origin!');
        process.exit(1);
    }

    // === Ενημέρωση m3u8 αρχείου ===
    const content = fs.readFileSync(M3U8_FILE, 'utf-8');
    // Βρες και αντικατέστησε όλα τα Referer/Origin με τα καινούρια
    const updated = content.replace(
        /\|?Referer=[^&\r\n]+&Origin=[^&\r\n]+/g,
        `|Referer=${referer}&Origin=${origin}`
    );
    fs.writeFileSync(M3U8_FILE, updated, 'utf-8');
    console.log(`Το αρχείο ${M3U8_FILE} ενημερώθηκε με τα νέα headers!`);
})();
