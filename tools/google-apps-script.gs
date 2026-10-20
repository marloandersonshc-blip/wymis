/**
 * WYMIS Website Inquiries: backup receiver.
 * Bound to the sheet "WYMIS Website Inquiries" (Extensions > Apps Script), deployed as a
 * Web app (Execute as: Me, Who has access: Anyone). The /exec URL lives only in a private file
 * on the server and acts as the access key; requests that are not WYMIS submissions are rejected.
 *
 * Partner inquiries (contact.php) go to the first tab.
 * One-Day Intensive registrations (register.php, form: "registration") go to the "Registrations" tab,
 * which is created with headers the first time a registration arrives.
 * Signed consent forms (consent.php, form: "consent") go to the "Consents" tab, created the same way.
 * After pasting an update: Deploy > Manage deployments > edit (pencil) > Version: New version > Deploy.
 * Editing the existing deployment keeps the same /exec URL, so nothing changes on the server.
 */
var REG_TAB = 'Registrations';
var REG_HEADERS = ['Received (Phoenix time)', 'Event', 'Event date', 'Location', 'First name', 'Last name', 'Email', 'Phone',
  'Age', 'School or organization', 'Heard about WYMIS', 'Parent or guardian', 'Parent email', 'Parent phone',
  'Parent permission', 'Accessibility needs or questions', 'Notice to info@ sent', 'Confirmation sent',
  'Parent copy sent', 'IP address', 'Status'];

var CON_TAB = 'Consents';
var CON_HEADERS = ['Signed (Phoenix time)', 'Event', 'Event date', 'Participant', 'Participant email', 'Under 18',
  'Signed by', 'Relationship', 'Signer email', 'Signer phone', 'Typed signature', 'Form version', 'From registration link',
  'Copy emailed to signer', 'Notice to info@ sent', 'Saved on server', 'IP address'];

function tab(ss, name, headers) {
  var sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name, ss.getSheets().length);
    sh.appendRow(headers);
    sh.getRange(1, 1, 1, headers.length).setFontWeight('bold');
    sh.setFrozenRows(1);
  }
  return sh;
}

function doPost(e) {
  try {
    var d = JSON.parse(e.postData.contents);
    var emailOk = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(d.email || '');
    if (d.source !== 'wymisworks.org' || !emailOk) return reply({ ok: false, error: 'rejected' });
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var yn = function (v) { return v ? 'Yes' : 'No'; };

    if (d.form === 'consent') {
      if (!d.student || !d.event || !d.signer || !d.signature) return reply({ ok: false, error: 'rejected' });
      tab(ss, CON_TAB, CON_HEADERS).appendRow([
        d.received, d.event, d.date, d.student, d.email, yn(d.minor), d.signer, d.relationship, d.gemail, d.gphone,
        d.signature, d.version, yn(d.vialink), yn(d.copy), yn(d.notice), yn(d.saved), d.ip
      ].map(safe));
      return reply({ ok: true });
    }

    if (d.form === 'registration') {
      if (!d.first || !d.last || !d.event) return reply({ ok: false, error: 'rejected' });
      var reg = ss.getSheetByName(REG_TAB);
      if (!reg) {
        reg = ss.insertSheet(REG_TAB, ss.getSheets().length);
        reg.appendRow(REG_HEADERS);
        reg.getRange(1, 1, 1, REG_HEADERS.length).setFontWeight('bold');
        reg.setFrozenRows(1);
      }
      reg.appendRow([
        d.received, d.event, d.date, d.location, d.first, d.last, d.email, d.phone, d.age, d.org, d.heard,
        d.gname, d.gemail, d.gphone, d.gname ? yn(d.gconsent) : '', d.notes,
        yn(d.notice), yn(d.confirmation), d.gname ? yn(d.gconfirmation) : '', d.ip, 'Registered'
      ].map(safe));
      return reply({ ok: true });
    }

    if (!d.name) return reply({ ok: false, error: 'rejected' });
    ss.getSheets()[0].appendRow([
      d.received, d.name, d.org, d.email, d.phone, d.type, d.interest, d.message,
      yn(d.notice), yn(d.confirmation), d.ip, 'New'
    ].map(safe));
    return reply({ ok: true });
  } catch (err) {
    return reply({ ok: false, error: String(err) });
  }
}

// Blocks spreadsheet formula injection and caps cell length
function safe(v) {
  v = String(v === undefined || v === null ? '' : v).slice(0, 4000);
  return /^[=+\-@]/.test(v) ? "'" + v : v;
}

function reply(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
