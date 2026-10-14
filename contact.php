<?php
/**
 * WYMIS inquiry form handler (Hostinger PHP mail).
 *
 * Each inquiry is:
 *   1. emailed to TO_EMAIL,
 *   2. confirmed to the sender with a short "we received it" email,
 *   3. saved as a row in the Google Sheet "WYMIS Website Inquiries" (backup), via the Apps Script web app at SHEET_URL.
 *
 * FROM_EMAIL must be a real mailbox on wymisworks.org (Hostinger > Emails) so messages are not flagged as spam.
 * SHEET_URL is the Apps Script "Web app" URL (ends in /exec). Leave it empty to skip the sheet backup.
 * The Web app URL acts as the access key, so keep it only here (server side). Receiver script: tools/google-apps-script.gs.
 */
const TO_EMAIL     = 'info@wymisworks.org';
const FROM_EMAIL   = 'info@wymisworks.org';
const SHEET_URL    = '';
const BACK         = '/partner';

date_default_timezone_set('America/Phoenix');

function back($q) { header('Location: ' . BACK . '?' . $q . '#inquiry', true, 303); exit; }
function clean($v, $max) {
    $v = trim((string)($v ?? ''));
    $v = str_replace(["\r", "\n", "%0a", "%0d"], ' ', $v); // block header injection
    return mb_substr(strip_tags($v), 0, $max);
}
function utf8_subject($s) { return '=?UTF-8?B?' . base64_encode($s) . '?='; }

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { back('error=1'); }

// Honeypot: real visitors never fill this hidden field
if (!empty($_POST['website'])) { back('sent=1'); }

$name     = clean($_POST['name'] ?? '', 120);
$org      = clean($_POST['org'] ?? '', 160);
$email    = clean($_POST['email'] ?? '', 160);
$phone    = clean($_POST['phone'] ?? '', 40);
$type     = clean($_POST['type'] ?? '', 80);
$interest = clean($_POST['interest'] ?? '', 120);
$message  = mb_substr(strip_tags(trim((string)($_POST['message'] ?? ''))), 0, 4000);
$ip       = $_SERVER['REMOTE_ADDR'] ?? '';

if ($name === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) { back('error=1'); }

// Light rate limit: one submission per IP every 60 seconds
$ipKey = sys_get_temp_dir() . '/wymis_' . md5($ip ?: 'x');
if (file_exists($ipKey) && time() - filemtime($ipKey) < 60) { back('sent=1'); }
@touch($ipKey);

$received = date('Y-m-d g:i A');

// 1. Notice to the WYMIS inbox
$subject = 'WYMIS inquiry: ' . $name . ($org ? ' (' . $org . ')' : '');
$body  = "New inquiry from wymisworks.org\n\n";
$body .= "Name: $name\nOrganization: $org\nEmail: $email\nPhone: $phone\n";
$body .= "Reaching out as: $type\nInterested in: $interest\n\nMessage:\n$message\n\n";
$body .= "Received: $received (Phoenix time)\nIP: $ip\n";
$headers  = 'From: WYMIS Website <' . FROM_EMAIL . ">\r\n";
$headers .= 'Reply-To: ' . $name . ' <' . $email . ">\r\n";
$headers .= "MIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\n";
$notice = @mail(TO_EMAIL, utf8_subject($subject), $body, $headers, '-f' . FROM_EMAIL);

// 2. Confirmation to the sender (does not repeat their free-text message, so the form can't be used to relay spam)
$first = trim(explode(' ', $name)[0]);
$cbody  = "Hi $first,\n\n";
$cbody .= "Thank you for reaching out to WYMIS (What You Missed In School). We received your inquiry and will follow up within two business days.\n\n";
$cbody .= "What you sent us:\n";
if ($org !== '')      { $cbody .= "Organization: $org\n"; }
if ($interest !== '') { $cbody .= "Interested in: $interest\n"; }
$cbody .= "Received: $received (Phoenix time)\n\n";
$cbody .= "If you need to add anything, just reply to this email.\n\n";
$cbody .= "WYMIS\nhttps://wymisworks.org\n";
$cbody .= "A program under the umbrella of Love Nation Ministries, a registered 501(c)(3) nonprofit organization.\n";
$cheaders  = 'From: WYMIS <' . FROM_EMAIL . ">\r\n";
$cheaders .= 'Reply-To: WYMIS <' . FROM_EMAIL . ">\r\n";
$cheaders .= "MIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\n";
$confirm = @mail($email, utf8_subject('We received your WYMIS inquiry'), $cbody, $cheaders, '-f' . FROM_EMAIL);

// 3. Backup row in the Google Sheet
$logged = false;
if (SHEET_URL !== '' && function_exists('curl_init')) {
    $payload = json_encode([
        'source' => 'wymisworks.org', 'received' => $received, 'name' => $name, 'org' => $org,
        'email' => $email, 'phone' => $phone, 'type' => $type, 'interest' => $interest,
        'message' => $message, 'notice' => $notice, 'confirmation' => $confirm, 'ip' => $ip,
    ]);
    $ch = curl_init(SHEET_URL);
    curl_setopt_array($ch, [
        CURLOPT_POST => true, CURLOPT_POSTFIELDS => $payload,
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_RETURNTRANSFER => true, CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_CONNECTTIMEOUT => 5, CURLOPT_TIMEOUT => 10,
    ]);
    $resp = curl_exec($ch);
    curl_close($ch);
    $logged = is_string($resp) && strpos($resp, '"ok":true') !== false;
}

// The inquiry counts as received if it reached the inbox or the backup sheet
back(($notice || $logged) ? 'sent=1' : 'error=2');
