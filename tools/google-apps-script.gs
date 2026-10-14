/**
 * WYMIS Website Inquiries: backup receiver.
 * Paste into the sheet "WYMIS Website Inquiries" via Extensions > Apps Script, then
 * Deploy > New deployment > Web app (Execute as: Me, Who has access: Anyone).
 * Put the Web app URL (ends in /exec) into SHEET_URL in contact.php.
 * SECRET must match SHEET_SECRET in contact.php.
 */
const SECRET = 'CtiYoFgjQwLlxn3ORRVqLdx3e5V5Z3MK';

function doPost(e) {
  try {
    const d = JSON.parse(e.postData.contents);
    if (d.secret !== SECRET) return reply({ ok: false, error: 'forbidden' });
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
    // Prefix values that start with = + - @ so the sheet never runs them as formulas
    const safe = v => { v = String(v === undefined || v === null ? '' : v); return /^[=+\-@]/.test(v) ? "'" + v : v; };
    sheet.appendRow([
      d.received, d.name, d.org, d.email, d.phone, d.type, d.interest, d.message,
      d.notice ? 'Yes' : 'No', d.confirmation ? 'Yes' : 'No', d.ip, 'New'
    ].map(safe));
    return reply({ ok: true });
  } catch (err) {
    return reply({ ok: false, error: String(err) });
  }
}

function reply(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
