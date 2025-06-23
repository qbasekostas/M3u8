const { chromium } = require('playwright');
const fs = require('fs');

const STREAM_URL = process.argv[2] || 'https://miztv.top/stream/stream-622.php';
const M3U8_FILE = process.argv[3] || 'GreekSportsChannels.m3u8';

(async () => {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();

    let referer = null, origin = null, m3u8url = null, found = false;

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

    // Περίμενε λίγο να φορτώσουν τα iframes
    await page.waitForTimeout(5000);

    // Πάρε όλα τα iframe elements
    const frames = page.frames();
    console.log(`[DEBUG] Βρέθηκαν ${frames.length} frames`);

    for (let i = 0; i < frames.length; i++) {
        const frame = frames[i];
        try {
            // Πάτα όλα τα buttons σε κάθε frame
            const buttons = await frame.$$('button');
            console.log(`[DEBUG][Frame ${i}] Βρέθηκαν ${buttons.length} κουμπιά`);
            for (let j = 0; j < buttons.length; j++) {
                try {
                    console.log(`[DEBUG][Frame ${i}] Κάνω click στο κουμπί #${j + 1}`);
                    await buttons[j].click();
                    await page.waitForTimeout(1000);
                } catch (e) {
                    console.log(`[DEBUG][Frame ${i}] Σφάλμα στο click κουμπιού #${j + 1}:`, e.message);
                }
            }
        } catch (e) {
            console.log(`[DEBUG][Frame ${i}] Σφάλμα στην επεξεργασία κουμπιών:`, e.message);
        }
    }

    // Πάτησε Space σε όλα τα frames (αν και συνήθως δεν χρειάζεται)
    for (let i = 0; i < frames.length; i++) {
        try {
            await frames[i].keyboard.press('Space');
            console.log(`[DEBUG][Frame ${i}] Πάτησα Space.`);
        } catch (e) {
            // Αγνόησε το error
        }
    }

    // Περίμενε αρκετά να γίνει το αίτημα (.m3u8)
    await page.waitForTimeout(40000);

    await browser.close();

    if (!referer || !origin) {
        console.error('ERROR: Δεν βρέθηκε referer/origin!');
        process.exit(1);
    }

    // === Ενημέρωση m3u8 αρχείου ===
    const content = fs.readFileSync(M3U8_FILE, 'utf-8');
    const updated = content.replace(
        /\|?Referer=[^&\r\n]+&Origin=[^&\r\n]+/g,
        `|Referer=${referer}&Origin=${origin}`
    );
    fs.writeFileSync(M3U8_FILE, updated, 'utf-8');
    console.log(`[SUCCESS] Το αρχείο ${M3U8_FILE} ενημερώθηκε με τα νέα headers!`);
})();
