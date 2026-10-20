<?php
/**
 * WYMIS consent form: shared helpers for register.php and consent.php.
 * PHP-only include; prints nothing if requested over the web.
 *
 * Signing links are tamper-proof: the registration details travel in the link and are
 * signed with a secret key kept one level ABOVE public_html (wymis-consent-secret.txt).
 * The key is created automatically the first time it is needed.
 * Signed forms are saved as JSON files in wymis-consents/ next to that key (also outside public_html),
 * emailed to the signer, the student and info@, and logged to the "Consents" tab of the Google Sheet.
 */
if (!defined('WYMIS_PRIVATE_DIR')) define('WYMIS_PRIVATE_DIR', getenv('WYMIS_PRIVATE_DIR') ?: dirname(__DIR__));

const CONSENT_VERSION = '2026-10-20';
const CONSENT_TTL     = 15552000; // signing links work for 180 days

function consent_secret() {
    static $key = null;
    if ($key !== null) return $key;
    $file = WYMIS_PRIVATE_DIR . '/wymis-consent-secret.txt';
    $k = is_readable($file) ? trim((string)file_get_contents($file)) : '';
    if (strlen($k) < 32) {
        $k = bin2hex(random_bytes(32));
        if (@file_put_contents($file, $k . "\n", LOCK_EX) !== false) @chmod($file, 0600);
        else $k = hash('sha256', __FILE__ . php_uname() . (defined('SHEET_URL') ? SHEET_URL : '')); // fallback if the folder is not writable
    }
    return $key = $k;
}

function b64u_enc($s) { return rtrim(strtr(base64_encode($s), '+/', '-_'), '='); }
function b64u_dec($s) { return base64_decode(strtr($s, '-_', '+/'), true); }

/** Build the signing token for one registration. $d keys: e (event slug), f, l, m (student email), a (age), r ('guardian'|'self'), gn, ge, gp */
function consent_token(array $d) {
    $d['t'] = time();
    $p = b64u_enc(json_encode($d, JSON_UNESCAPED_UNICODE));
    return $p . '.' . b64u_enc(substr(hash_hmac('sha256', $p, consent_secret(), true), 0, 18));
}

/** Returns the payload array, or null if the link was altered or expired. */
function consent_verify($tok) {
    if (!is_string($tok) || strlen($tok) > 2000 || substr_count($tok, '.') !== 1) return null;
    [$p, $sig] = explode('.', $tok);
    $want = b64u_enc(substr(hash_hmac('sha256', $p, consent_secret(), true), 0, 18));
    if (!hash_equals($want, $sig)) return null;
    $d = json_decode((string)b64u_dec($p), true);
    if (!is_array($d) || empty($d['e']) || empty($d['m']) || time() - (int)($d['t'] ?? 0) > CONSENT_TTL) return null;
    return $d;
}

function consent_url(array $d) { return 'https://wymisworks.org/consent?t=' . consent_token($d); }

/** Where a signed form for this student and event is stored. */
function consent_record_path($eventSlug, $studentEmail) {
    $dir = WYMIS_PRIVATE_DIR . '/wymis-consents/' . preg_replace('/[^a-z0-9-]/', '', strtolower($eventSlug));
    return [$dir, $dir . '/' . hash('sha256', strtolower(trim($studentEmail))) . '.json'];
}

/**
 * The consent and release text. $minor: signed by a parent or guardian. Returns [heading, text] pairs.
 * Change the wording here and bump CONSENT_VERSION; each signed record stores the version and a hash of the exact text.
 */
function consent_sections($minor, $student, $city, $day, $where) {
    $org = 'Love Nation Inc., a 501(c)(3) nonprofit organization, its WYMIS (What You Missed In School) program, and their directors, officers, employees, facilitators, volunteers, and the host venue (together, "WYMIS")';
    $who = $minor ? "my child, $student" : 'myself';
    $s = [];
    $s[] = ['1. Permission to attend', $minor
        ? "I am the parent or legal guardian of $student. I give permission for $student to attend the free WYMIS One-Day Intensive in $city on $day, 9:00 AM to 6:00 PM local time, at $where, and to take part in its sessions, group activities, and meals."
        : "I am 18 or older. I am choosing to attend the free WYMIS One-Day Intensive in $city on $day, 9:00 AM to 6:00 PM local time, at $where, and to take part in its sessions, group activities, and meals."];
    $s[] = ['2. Voluntary participation and conduct', ($minor ? "Attendance is voluntary. " . ucfirst($student) . " is expected" : 'Attendance is voluntary. I am expected') .
        " to follow staff instructions and venue rules and to treat others with respect. WYMIS may end participation for conduct that is unsafe or disruptive" .
        ($minor ? ', and will contact me if that happens. If my child needs to leave early, I will tell WYMIS staff.' : '.')];
    $s[] = ['3. Travel and belongings', "WYMIS does not provide transportation to or from the event. " . ($minor ? 'I am responsible for how my child gets there and home.' : 'I am responsible for getting there and home.') .
        ' WYMIS is not responsible for lost, stolen, or damaged personal property.'];
    $s[] = ['4. Assumption of risk', "Attending an in-person event involves ordinary risks, including travel, slips and falls, food allergies or illness, and contagious illness. I understand these risks and accept them for $who."];
    $s[] = ['5. Release of liability', "To the fullest extent the law allows, I release and agree not to sue $org for any injury, illness, loss, or damage to " . ($minor ? 'my child or me' : 'me') .
        " that arises from taking part in the event, except for harm caused by gross negligence or willful misconduct. This release binds " . ($minor ? 'me, my child, and our' : 'me and my') . " heirs and legal representatives."];
    $s[] = ['6. Emergencies', ($minor ? 'If my child is hurt or becomes ill and I cannot be reached right away' : 'If I am hurt or become ill and cannot decide for myself') .
        ', I authorize WYMIS staff to call emergency services and to arrange emergency care. ' . ($minor ? 'I will be responsible for any resulting medical costs.' : 'I am responsible for any resulting medical costs.')];
    $s[] = ['7. Electronic signature', 'I have read this form and had the chance to ask questions by emailing info@wymisworks.org. Typing my full name below is my electronic signature and has the same effect as signing on paper. If any part of this form is found unenforceable, the rest still applies. This form is governed by the laws of the State of Arizona.'];
    return $s;
}

function consent_text($minor, $student, $city, $day, $where) {
    return implode("\n\n", array_map(function ($x) { return $x[0] . "\n" . $x[1]; }, consent_sections($minor, $student, $city, $day, $where)));
}
