/**
 * WYMIS Website Inquiries: backup receiver.
 * Bound to the sheet "WYMIS Website Inquiries" (Extensions > Apps Script), deployed as a
 * Web app (Execute as: Me, Who has access: Anyone). The /exec URL lives only in contact.php
 * on the server and acts as the access key; requests that are not WYMIS inquiries are rejected.
 */
function doPost(e) {
  try {
    var d = JSON.parse(e.postData.contents);
    if (d.source !== 'wymisworks.org' || !d.name || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(d.email || '')) {
      return reply({ ok: false, error: 'rejected' });
    }
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
    var safe = function (v) {
      v = String(v === undefined || v === null ? '' : v).slice(0, 4000);
      return /^[=+\-@]/.test(v) ? "'" + v : v;
    };
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
