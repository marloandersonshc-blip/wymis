<?php
/**
 * WYMIS inquiry form handler (Hostinger PHP mail).
 * Change TO_EMAIL to the inbox that should receive inquiries.
 * FROM_EMAIL should be a mailbox on the wymis.com domain (create it in Hostinger > Emails) so messages are not flagged as spam.
 */
const TO_EMAIL   = 'info@wymis.com';
const FROM_EMAIL = 'no-reply@wymis.com';
const BACK       = '/partner';

function back($q) { header('Location: ' . BACK . '?' . $q . '#inquiry', true, 303); exit; }
function clean($v, $max) {
    $v = trim((string)($v ?? ''));
    $v = str_replace(["\r", "\n", "%0a", "%0d"], ' ', $v); // block header injection
    return mb_substr(strip_tags($v), 0, $max);
}

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

if ($name === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) { back('error=1'); }

// Light rate limit: one submission per IP every 60 seconds
$ipKey = sys_get_temp_dir() . '/wymis_' . md5($_SERVER['REMOTE_ADDR'] ?? 'x');
if (file_exists($ipKey) && time() - filemtime($ipKey) < 60) { back('sent=1'); }
@touch($ipKey);

$subject = 'WYMIS inquiry: ' . $name . ($org ? ' (' . $org . ')' : '');
$body  = "New inquiry from wymis.com\n\n";
$body .= "Name: $name\nOrganization: $org\nEmail: $email\nPhone: $phone\n";
$body .= "Reaching out as: $type\nInterested in: $interest\n\nMessage:\n$message\n\n";
$body .= "Sent: " . date('Y-m-d H:i T') . "\nIP: " . ($_SERVER['REMOTE_ADDR'] ?? '') . "\n";

$headers  = 'From: WYMIS Website <' . FROM_EMAIL . ">\r\n";
$headers .= 'Reply-To: ' . $name . ' <' . $email . ">\r\n";
$headers .= "MIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\n";

$ok = @mail(TO_EMAIL, '=?UTF-8?B?' . base64_encode($subject) . '?=', $body, $headers, '-f' . FROM_EMAIL);
back($ok ? 'sent=1' : 'error=2');
