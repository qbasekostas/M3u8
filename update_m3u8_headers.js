const { chromium } = require('playwright');
const fs = require('fs');

// Ορισμός URLs και αρχείου m3u8 από arguments ή default
const STREAM_URL = process.argv[2] || 'https://miztv.top/stream/stream-622.php';
const M3U8_FILE = process.argv[3] || 'GreekSportsChannels.m3u8';

(async () => {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();

    let referer = null, origin = null, m3u8url = null, found = false;

    // DEBUG: Εκτύπωσε κάθε request προς .m3u8
    context.on('request', request => {
        if (request.url().includes('.m3u8')) {
            console.log('[DEBUG] Βρέθηκε αίτημα προς .m3u8: ' + request.url());
            console.log('[DEBUG] Headers:', request.headers());
        }
        if (!found && request.url().includes('.m3u8')) {
            const headers = request.headers();
            if (headers['referer'] && headers['origin']) {
                referer = headers['referer'];
                origin = headers['origin'];
                m3u8url = request.url();
                found = true;
                console.log(`[INFO] ΝΕΟ Referer: ${referer}`);
                console.log(`[INFO] ΝΕΟ Origin: ${origin}`);
                console.log(`[INFO] ΝΕΟ m3u8 URL: ${m3u8url}`);
            }
        }
    });

    const page = await context.newPage();
    console.log(`[DEBUG] Μετάβαση στη σελίδα: ${STREAM_URL}`);
    await page.goto(STREAM_URL, { waitUntil: "domcontentloaded" });

    // DEBUG: Περίμενε, μήπως φορτώνει κάποιο iframe/player
    await page.waitForTimeout(3000);

    // DEBUG: Δες αν υπάρχουν κουμπιά και κάνε click κατά σειρά
    const buttons = await page.$$('button');
    if (buttons.length > 0) {
        for (let i = 0; i < buttons.length; i++) {
            try {
                console.log(`[DEBUG] Κάνω click στο κουμπί #${i + 1}`);
                await buttons[i].click();
                await page.waitForTimeout(1000);
            } catch (e) {
                console.log(`[DEBUG] Σφάλμα στο click κουμπιού #${i + 1}:`, e.message);
            }
        }
    } else {
        console.log('[DEBUG] Δεν βρέθηκαν κουμπιά για click.');
    }

    // DEBUG: Δοκίμασε να πατήσεις Space
    try {
        await page.keyboard.press('Space');
        console.log('[DEBUG] Πάτησα Space.');
    } catch (e) {
        console.log('[DEBUG] Αποτυχία στο πάτημα Space:', e.message);
    }

    // Περίμενε αρκετά για να ξεκινήσει το stream (40 δευτερόλεπτα)
    await page.waitForTimeout(40000);

    await browser.close();

    if (!referer || !origin) {
        console.error('ERROR: Δεν βρέθηκε referer/origin!');
        process.exit(1);
    }

    // === Ενημέρωση m3u8 αρχείου ===
    const content = fs.readFileSync(M3U8_FILE, 'utf-8');
    // Αντικατάσταση headers σε όλες τις γραμμές που περιέχουν Referer/Origin
    const updated = content.replace(
        /\|?Referer=[^&\r\n]+&Origin=[^&\r\n]+/g,
        `|Referer=${referer}&Origin=${origin}`
    );
    fs.writeFileSync(M3U8_FILE, updated, 'utf-8');
    console.log(`[SUCCESS] Το αρχείο ${M3U8_FILE} ενημερώθηκε με τα νέα headers!`);
})();
