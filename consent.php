<?php
/**
 * WYMIS One-Day Intensive consent and release form (/consent).
 * GENERATED: tools/build.py wraps tools/consent.tpl.php with the site header and footer and writes /consent.php.
 * Edit tools/consent.tpl.php, then run python3 tools/build.py.
 *
 * Opened from the signing link emailed at registration (prefilled and locked), or plainly at /consent
 * for anyone who registered before the form existed.
 */
const TO_EMAIL   = 'info@wymisworks.org';
const FROM_EMAIL = 'info@wymisworks.org';

$sheetFile = dirname(__DIR__) . '/wymis-sheet-url.txt';
$sheetUrl  = is_readable($sheetFile) ? trim((string)file_get_contents($sheetFile)) : '';
define('SHEET_URL', preg_match('#^https://script\.google\.com/macros/s/[\w-]+/exec$#', $sheetUrl) ? $sheetUrl : '');

date_default_timezone_set('America/Phoenix');
require __DIR__ . '/consent.inc.php';
$EVENTS = include __DIR__ . '/events.inc.php';

function h($s) { return htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8'); }
function clean($v, $max) {
    $v = trim((string)($v ?? ''));
    $v = str_replace(["\r", "\n", "%0a", "%0d"], ' ', $v);
    return mb_substr(strip_tags($v), 0, $max);
}
function norm($s) { return preg_replace('/\s+/', ' ', mb_strtolower(trim((string)$s))); }
function utf8_subject($s) { return '=?UTF-8?B?' . base64_encode($s) . '?='; }
function send($to, $subject, $body, $replyTo) {
    $h  = 'From: WYMIS <' . FROM_EMAIL . ">\r\n";
    $h .= 'Reply-To: ' . $replyTo . "\r\n";
    $h .= "MIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\n";
    return @mail($to, utf8_subject($subject), $body, $h, '-f' . FROM_EMAIL);
}

$today = date('Y-m-d');
$open  = array_filter($EVENTS, function ($e) use ($today) { return $e[2] >= $today; });

$tok   = (string)($_POST['t'] ?? $_GET['t'] ?? '');
$pre   = $tok !== '' ? consent_verify($tok) : null;
if ($pre && !isset($EVENTS[$pre['e']])) $pre = null;
$badLink = ($tok !== '' && !$pre);

$state = 'form';
$errs  = [];
$v = [   // form values
    'event' => $pre['e'] ?? clean($_GET['event'] ?? '', 60),
    'sfirst' => $pre['f'] ?? '', 'slast' => $pre['l'] ?? '', 'semail' => $pre['m'] ?? '',
    'minor' => $pre ? (($pre['r'] ?? '') === 'guardian' ? 'yes' : 'no') : '',
    'gname' => $pre['gn'] ?? (($pre['r'] ?? '') === 'self' ? trim(($pre['f'] ?? '') . ' ' . ($pre['l'] ?? '')) : ''),
    'rel' => ($pre['r'] ?? '') === 'self' ? 'Self, 18 or older' : '',
    'gemail' => $pre['ge'] ?? (($pre['r'] ?? '') === 'self' ? ($pre['m'] ?? '') : ''),
    'gphone' => $pre['gp'] ?? '', 'sig' => '',
];
$record = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!empty($_POST['website'])) { $state = 'done'; }   // honeypot
    else {
        if (!$pre) {
            $v['event']  = clean($_POST['event'] ?? '', 60);
            $v['sfirst'] = clean($_POST['sfirst'] ?? '', 80);
            $v['slast']  = clean($_POST['slast'] ?? '', 80);
            $v['semail'] = clean($_POST['semail'] ?? '', 160);
            $v['minor']  = ($_POST['minor'] ?? '') === 'yes' ? 'yes' : (($_POST['minor'] ?? '') === 'no' ? 'no' : '');
        }
        $v['gname']  = clean($_POST['gname'] ?? '', 120);
        $v['rel']    = clean($_POST['rel'] ?? '', 40);
        $v['gemail'] = clean($_POST['gemail'] ?? '', 160);
        $v['gphone'] = clean($_POST['gphone'] ?? '', 40);
        $v['sig']    = clean($_POST['sig'] ?? '', 120);
        $read  = ($_POST['read'] ?? '') === 'yes';
        $esign = ($_POST['esign'] ?? '') === 'yes';
        $minor = $v['minor'] === 'yes';
        if (!$minor) $v['rel'] = 'Self, 18 or older';

        if (!isset($open[$v['event']])) $errs['event'] = 'Choose an upcoming intensive.';
        if ($v['sfirst'] === '' || $v['slast'] === '') $errs['student'] = "Add the student's first and last name.";
        if (!filter_var($v['semail'], FILTER_VALIDATE_EMAIL)) $errs['semail'] = "Add the email the student registered with.";
        if ($v['minor'] === '') $errs['minor'] = "Tell us whether the student is under 18.";
        if ($minor && !in_array($v['rel'], ['Parent', 'Legal guardian'], true)) $errs['rel'] = 'Choose parent or legal guardian.';
        if ($v['gname'] === '') $errs['gname'] = 'Add your full legal name.';
        if (!filter_var($v['gemail'], FILTER_VALIDATE_EMAIL)) $errs['gemail'] = 'Add a valid email for your signed copy.';
        if ($minor && strlen(preg_replace('/\D/', '', $v['gphone'])) < 10) $errs['gphone'] = 'Add a phone number where we can reach you on the event day.';
        if (!$read)  $errs['read']  = 'Confirm you have read the form.';
        if (!$esign) $errs['esign'] = 'Agree to sign electronically.';
        if ($v['sig'] === '' || norm($v['sig']) !== norm($v['gname'])) $errs['sig'] = 'Type your full name exactly as entered above to sign.';

        if (!$errs) {
            [$city, $day, $iso, $where] = $EVENTS[$v['event']];
            $student = $v['sfirst'] . ' ' . $v['slast'];
            $text = consent_text($minor, $student, $city, $day, $where);
            [$dir, $path] = consent_record_path($v['event'], $v['semail']);
            if (is_readable($path)) {
                $record = json_decode((string)file_get_contents($path), true);
                $state = 'already';
            } else {
                $ip = $_SERVER['REMOTE_ADDR'] ?? '';
                $signedAt = date('Y-m-d g:i A');
                $record = [
                    'version' => CONSENT_VERSION, 'text_sha256' => hash('sha256', $text), 'signed_at' => $signedAt, 'signed_iso' => date('c'),
                    'event' => $v['event'], 'city' => $city, 'date' => $day, 'location' => $where,
                    'student' => $student, 'student_email' => $v['semail'], 'under_18' => $minor,
                    'signer' => $v['gname'], 'relationship' => $v['rel'], 'signer_email' => $v['gemail'], 'signer_phone' => $v['gphone'],
                    'signature' => $v['sig'], 'via_link' => (bool)$pre, 'ip' => $ip, 'user_agent' => mb_substr((string)($_SERVER['HTTP_USER_AGENT'] ?? ''), 0, 300),
                ];
                if (!is_dir($dir)) @mkdir($dir, 0700, true);
                $fh = @fopen($path, 'x');
                $saved = false;
                if ($fh) { $saved = fwrite($fh, json_encode($record, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)) !== false; fclose($fh); }

                $sigLine = "Signed electronically by {$v['gname']} ({$v['rel']}) on $signedAt Phoenix time.\nTyped signature: {$v['sig']}\nEmail: {$v['gemail']}" . ($v['gphone'] !== '' ? "\nPhone: {$v['gphone']}" : '') . "\nForm version: " . CONSENT_VERSION;
                $copy  = "WYMIS One-Day Intensive: Consent, Permission, and Release of Liability\n\n";
                $copy .= "Participant: $student ($v[semail])\nEvent: $city, $day, 9:00 AM to 6:00 PM local time\nLocation: $where\n\n";
                $copy .= $text . "\n\n" . $sigLine . "\n\nKeep this email as your copy. Questions or changes: reply to this email.\n\nWYMIS (What You Missed In School)\nA program under the umbrella of Love Nation Inc., a registered 501(c)(3) nonprofit organization.\nhttps://wymisworks.org\n";
                $mSigner = send($v['gemail'], "Signed: WYMIS consent form for $student ($city)", $copy, 'WYMIS <' . FROM_EMAIL . '>');
                $mStudent = false;
                if (strtolower($v['semail']) !== strtolower($v['gemail'])) {
                    $sm  = "Hi {$v['sfirst']},\n\nYour consent form for the WYMIS One-Day Intensive in $city on $day is signed" . ($minor ? " by {$v['gname']}" : '') . ". You are all set.\n\n";
                    $sm .= "Location: $where\nCheck-in opens at 8:30 AM.\n\nWYMIS\nhttps://wymisworks.org\n";
                    $mStudent = send($v['semail'], "Your WYMIS consent form is signed ($city)", $sm, 'WYMIS <' . FROM_EMAIL . '>');
                }
                $mInbox = send(TO_EMAIL, "Consent signed: $student ($city, " . date('M j', strtotime($iso)) . ")", $copy . "\nIP: $ip\nSaved on server: " . ($saved ? 'Yes' : 'No') . "\n", "{$v['gname']} <{$v['gemail']}>");

                $logged = false;
                if (SHEET_URL !== '' && function_exists('curl_init')) {
                    $ch = curl_init(SHEET_URL);
                    curl_setopt_array($ch, [
                        CURLOPT_POST => true, CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
                        CURLOPT_POSTFIELDS => json_encode([
                            'source' => 'wymisworks.org', 'form' => 'consent', 'received' => $signedAt,
                            'event' => $city, 'date' => $day, 'student' => $student, 'email' => $v['semail'], 'minor' => $minor,
                            'signer' => $v['gname'], 'relationship' => $v['rel'], 'gemail' => $v['gemail'], 'gphone' => $v['gphone'],
                            'signature' => $v['sig'], 'version' => CONSENT_VERSION, 'vialink' => (bool)$pre,
                            'copy' => $mSigner, 'notice' => $mInbox, 'saved' => $saved, 'ip' => $ip,
                        ]),
                        CURLOPT_RETURNTRANSFER => true, CURLOPT_FOLLOWLOCATION => true, CURLOPT_CONNECTTIMEOUT => 5, CURLOPT_TIMEOUT => 10,
                    ]);
                    $resp = curl_exec($ch); curl_close($ch);
                    $logged = is_string($resp) && strpos($resp, '"ok":true') !== false;
                }
                if ($saved || $mInbox || $logged) { $state = 'done'; }
                else { @unlink($path); $errs['send'] = 'We could not save your signature just now. Please try again in a few minutes or email info@wymisworks.org.'; }
            }
        }
    }
}

// Already signed (seen on a fresh visit from the link)
if ($state === 'form' && $pre && $_SERVER['REQUEST_METHOD'] !== 'POST') {
    [, $path] = consent_record_path($pre['e'], $pre['m']);
    if (is_readable($path)) { $record = json_decode((string)file_get_contents($path), true); $state = 'already'; }
}

$ev = $EVENTS[$v['event']] ?? null;
$minorView = $v['minor'] === 'yes';
$studentName = trim($v['sfirst'] . ' ' . $v['slast']);
$err = function ($k) use ($errs) { return isset($errs[$k]) ? '<span class="field-err" role="alert">' . h($errs[$k]) . '</span>' : ''; };
?>
<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Consent Form | WYMIS One-Day Intensive</title>
<meta name="description" content="Parent, guardian, and participant consent, permission, and release of liability for the free WYMIS One-Day Intensive.">
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="https://wymisworks.org/consent">
<meta name="author" content="Dr. Barry K. Jackson, Ph.D.">
<meta name="theme-color" content="#0A1F4D">
<meta name="geo.region" content="US-AZ">
<meta name="geo.placename" content="Phoenix, Arizona">
<meta name="geo.position" content="33.4484;-112.0740">
<meta name="ICBM" content="33.4484, -112.0740">
<meta property="og:type" content="website">
<meta property="og:site_name" content="WYMIS: What You Missed In School">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="Consent Form | WYMIS One-Day Intensive">
<meta property="og:description" content="Parent, guardian, and participant consent, permission, and release of liability for the free WYMIS One-Day Intensive.">
<meta property="og:url" content="https://wymisworks.org/consent">
<meta property="og:image" content="https://wymisworks.org/assets/img/og/wymis-og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="WYMIS logo with the line: Welcome to the thirteenth grade.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Consent Form | WYMIS One-Day Intensive">
<meta name="twitter:description" content="Parent, guardian, and participant consent, permission, and release of liability for the free WYMIS One-Day Intensive.">
<meta name="twitter:image" content="https://wymisworks.org/assets/img/og/wymis-og.png">
<link rel="icon" href="favicon.ico" sizes="48x48">
<link rel="icon" href="assets/img/brand/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="assets/img/brand/apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<link rel="alternate" type="text/plain" title="LLM summary" href="llms.txt">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://images.unsplash.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@112..125,500..800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="assets/css/site.css?v=fc77be66">
<script type="application/ld+json">{"@context":"https://schema.org","@graph":[{"@type":"EducationalOrganization","@id":"https://wymisworks.org/#org","name":"WYMIS","alternateName":"What You Missed In School","url":"https://wymisworks.org/","logo":{"@type":"ImageObject","url":"https://wymisworks.org/assets/img/brand/icon-512.png","width":512,"height":512},"image":"https://wymisworks.org/assets/img/og/wymis-og.png","email":"info@wymisworks.org","description":"WYMIS (What You Missed In School) is a cohort-based “thirteenth grade” workforce readiness and life skills program for ages 16 to 26.","founder":{"@id":"https://wymisworks.org/about#barry-jackson"},"slogan":"Building the bridge between education and execution","parentOrganization":{"@type":"NGO","name":"Love Nation Inc.","nonprofitStatus":"Nonprofit501c3","url":"https://lovenationministries.org/","logo":"https://img1.wsimg.com/isteam/ip/a3d9029a-ee77-4795-b8c1-e567b129ffc1/Love%20Nation%20Without%20Slogan%20Transparent%20bg.svg","address":{"@type":"PostalAddress","streetAddress":"1141 East Glendale Avenue","addressLocality":"Phoenix","addressRegion":"AZ","postalCode":"85020","addressCountry":"US"}},"areaServed":[{"@type":"Country","name":"United States"},{"@type":"City","name":"Phoenix","containedInPlace":{"@type":"State","name":"Arizona"}},{"@type":"City","name":"Las Vegas","containedInPlace":{"@type":"State","name":"Nevada"}},{"@type":"City","name":"Memphis","containedInPlace":{"@type":"State","name":"Tennessee"}}],"knowsAbout":["Financial Literacy","Business Fundamentals","Soft Skills","Etiquette","Networking Principles","AI and Technology","Branding and Marketing","Workforce readiness","Life skills education"]},{"@type":"WebSite","@id":"https://wymisworks.org/#website","url":"https://wymisworks.org/","name":"WYMIS","alternateName":"What You Missed In School","publisher":{"@id":"https://wymisworks.org/#org"},"inLanguage":"en-US"},{"@type":"WebPage","@id":"https://wymisworks.org/consent#webpage","url":"https://wymisworks.org/consent","name":"Consent Form | WYMIS One-Day Intensive","description":"Parent, guardian, and participant consent, permission, and release of liability for the free WYMIS One-Day Intensive.","isPartOf":{"@id":"https://wymisworks.org/#website"},"about":{"@id":"https://wymisworks.org/#org"},"primaryImageOfPage":"https://wymisworks.org/assets/img/og/wymis-og.png","inLanguage":"en-US","dateModified":"2026-10-21"},{"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://wymisworks.org/"},{"@type":"ListItem","position":2,"name":"Consent form","item":"https://wymisworks.org/consent"}]}]}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="promo" id="promo" role="region" aria-label="Upcoming One-Day Intensive">
  <div class="wrap promo-in"><a class="promo-link" href="register?event=phoenix-2026-10-24#register" data-date="2026-10-24"><span class="promo-tag">Free</span><span class="promo-text"><b>WYMIS One-Day Intensive</b> in Phoenix, AZ: Sat, Oct 24<span class="promo-sub">, ages 16 to 26</span></span><span class="promo-cta">Register now <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4"/></svg></span></a><a class="promo-link" href="register?event=memphis-2026-11-07#register" data-date="2026-11-07" hidden><span class="promo-tag">Free</span><span class="promo-text"><b>WYMIS One-Day Intensive</b> in Memphis, TN: Sat, Nov 7<span class="promo-sub">, ages 16 to 26</span></span><span class="promo-cta">Register now <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4"/></svg></span></a><a class="promo-link" href="register?event=las-vegas-2026-12-05#register" data-date="2026-12-05" hidden><span class="promo-tag">Free</span><span class="promo-text"><b>WYMIS One-Day Intensive</b> in Las Vegas, NV: Sat, Dec 5<span class="promo-sub">, ages 16 to 26</span></span><span class="promo-cta">Register now <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4"/></svg></span></a></div>
</div>
<nav class="nav" aria-label="Main">
  <div class="wrap nav-in">
    <a class="brand" href="./" aria-label="WYMIS home"><picture><source srcset="assets/img/brand/wymis-logo.webp" type="image/webp"><img src="assets/img/brand/wymis-logo.png" alt="WYMIS: What You Missed In School" width="250" height="48" fetchpriority="high"></picture></a>
    <button class="menu-btn" id="menuBtn" aria-label="Open menu" aria-expanded="false" aria-controls="navLinks">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
    </button>
    <ul class="nav-links" id="navLinks" data-open="false">
      <li><a href="program">Program</a></li><li><a href="curriculum">Curriculum</a></li><li><a href="intensive">One-Day Intensive</a></li><li><a href="register" aria-current="page">Register</a></li><li><a href="pilots">Pilots</a></li><li><a href="about">About</a></li><li><a href="faq">FAQ</a></li>
      <li><a class="btn btn-primary" href="partner">Partner With Us</a></li>
    </ul>
  </div>
</nav>
<header class="page-hero grid-bg">
  
  <div class="wrap ph-in">
    <ol class="crumbs" aria-label="Breadcrumb"><li><a href="./">Home</a></li><li aria-current="page">Consent form</li></ol>
    <span class="eyebrow">One-Day Intensive</span>
    <h1>Consent <em>form</em>.</h1>
    <p class="ph-lede">Permission to attend and release of liability. Required for every participant before the event: signed by a parent or guardian if under 18, or by the participant if 18 or older.</p>
  </div>
</header>
<main id="main">
<?php if ($state === 'done' || $state === 'already'): ?>
<section class="section" aria-labelledby="c-done">
  <div class="wrap"><div class="legal consent-done">
    <span class="eyebrow"><?= $state === 'done' ? 'Signed' : 'Already on file' ?></span>
    <h2 id="c-done"><?= $state === 'done' ? 'Thank you. The consent form is signed.' : 'This consent form is already signed.' ?></h2>
    <?php if ($record): ?>
    <ul class="consent-facts">
      <li><b>Participant</b><span><?= h($record['student']) ?></span></li>
      <li><b>Event</b><span><?= h($record['city'] . ', ' . $record['date']) ?></span></li>
      <li><b>Signed by</b><span><?= h($record['signer'] . ' (' . $record['relationship'] . ')') ?></span></li>
      <li><b>Signed on</b><span><?= h($record['signed_at']) ?> Phoenix time</span></li>
    </ul>
    <?php endif; ?>
    <p><?= $state === 'done' ? 'A copy of the signed form is on its way to your email. Keep it for your records.' : 'Nothing else is needed. If something on the form needs to change, email <a href="mailto:info@wymisworks.org">info@wymisworks.org</a>.' ?></p>
    <p>See the day's schedule on the <a href="/intensive">One-Day Intensive</a> page. Check-in opens at 8:30 AM.</p>
  </div></div>
</section>
<?php else: ?>
<section class="section" aria-labelledby="c-terms">
  <div class="wrap"><div class="legal">
    <span class="eyebrow">Read before signing</span>
    <h2 id="c-terms">Consent, permission, and release of liability</h2>
    <?php if ($pre && !empty($_GET['new']) && $_SERVER['REQUEST_METHOD'] !== 'POST'): ?><p class="consent-alert consent-ok">You're registered for <?= h($ev[0] . ', ' . $ev[1]) ?>. One more step: read and sign the consent form below. We also emailed you this link.</p><?php endif; ?>
    <?php if ($badLink): ?><p class="consent-alert">This signing link is not valid or has expired. You can still sign below: just enter the student's details.</p><?php endif; ?>
    <p class="lead"><?= $minorView ? 'Every participant under 18 needs this form signed by a parent or legal guardian before the event.' : ($v['minor'] === 'no' ? 'Participants 18 and older sign this form for themselves before the event.' : 'Every participant needs this form signed before the event: by a parent or legal guardian if the participant is under 18, or by the participant if 18 or older.') ?></p>
    <?php
      $sec = consent_sections($v['minor'] !== 'no', $studentName !== '' ? $studentName : 'the participant',
          $ev[0] ?? 'the city selected below', $ev[1] ?? 'the date selected below', $ev[3] ?? 'the venue listed for that date');
      foreach ($sec as $s): ?>
    <h3><?= h($s[0]) ?></h3>
    <p><?= h($s[1]) ?></p>
    <?php endforeach; ?>
    <?php if ($v['minor'] === ''): ?><p class="consent-small">If the participant is 18 or older, the same terms apply in the first person and the participant signs.</p><?php endif; ?>
  </div></div>
</section>
<section class="section on-navy grid-bg" id="sign" aria-labelledby="c-sign">
  <div class="wrap contact-in">
    <div class="contact-copy">
      <span class="eyebrow">Sign</span>
      <h2 id="c-sign"><?= $minorView ? 'Parent or guardian signature.' : ($v['minor'] === 'no' ? 'Your signature.' : 'Sign the form.') ?></h2>
      <p>It takes about a minute. You will get a signed copy by email right away.</p>
      <ul class="contact-list"><li>One form per participant, per event</li><li>Typed name counts as your signature</li><li>Questions? Email before you sign</li></ul>
      <div class="direct"><span>Questions</span><a href="mailto:info@wymisworks.org">info@wymisworks.org</a></div>
    </div>
    <form class="inquiry consent" action="/consent#sign" method="post" novalidate>
      <?php if (isset($errs['send'])): ?><p class="form-msg err" role="alert"><?= h($errs['send']) ?></p><?php elseif ($errs): ?><p class="form-msg err" role="alert">Please fix the highlighted items below.</p><?php endif; ?>
      <div class="hp" aria-hidden="true"><label for="c-web">Website</label><input id="c-web" name="website" tabindex="-1" autocomplete="off"></div>
      <input type="hidden" name="t" value="<?= $pre ? h($tok) : '' ?>">
      <?php if ($pre): ?>
      <div class="field full consent-locked">
        <span class="lbl">Participant</span>
        <p><b><?= h($studentName) ?></b> &middot; <?= h($v['semail']) ?><br><?= h($ev[0] . ', ' . $ev[1]) ?></p>
      </div>
      <?php else: ?>
      <div class="field full"><label for="c-event">Intensive</label><select id="c-event" name="event" required><option value="">Choose a city and date</option><?php foreach ($open as $slug => $e): ?><option value="<?= h($slug) ?>"<?= $v['event'] === $slug ? ' selected' : '' ?>><?= h($e[0] . ': ' . $e[1]) ?></option><?php endforeach; ?></select><?= $err('event') ?></div>
      <div class="field"><label for="c-sfirst">Participant first name</label><input id="c-sfirst" name="sfirst" value="<?= h($v['sfirst']) ?>" required maxlength="80"></div>
      <div class="field"><label for="c-slast">Participant last name</label><input id="c-slast" name="slast" value="<?= h($v['slast']) ?>" required maxlength="80"><?= $err('student') ?></div>
      <div class="field full"><label for="c-semail">Email the participant registered with</label><input id="c-semail" name="semail" type="email" value="<?= h($v['semail']) ?>" required maxlength="160"><?= $err('semail') ?></div>
      <div class="field full"><label for="c-minor">Is the participant under 18?</label><select id="c-minor" name="minor" required><option value="">Select</option><option value="yes"<?= $v['minor'] === 'yes' ? ' selected' : '' ?>>Yes, under 18: a parent or guardian signs</option><option value="no"<?= $v['minor'] === 'no' ? ' selected' : '' ?>>No, 18 or older: the participant signs</option></select><?= $err('minor') ?></div>
      <?php endif; ?>
      <div class="field"><label for="c-gname"><?= $pre && !$minorView ? 'Your full legal name' : 'Signer full legal name' ?></label><input id="c-gname" name="gname" value="<?= h($v['gname']) ?>" autocomplete="name" required maxlength="120"><?= $err('gname') ?></div>
      <?php if ($minorView || !$pre): ?>
      <div class="field" data-minor-only><label for="c-rel">Relationship to participant</label><select id="c-rel" name="rel"><option value="">Select</option><option<?= $v['rel'] === 'Parent' ? ' selected' : '' ?>>Parent</option><option<?= $v['rel'] === 'Legal guardian' ? ' selected' : '' ?>>Legal guardian</option></select><?= $err('rel') ?></div>
      <?php endif; ?>
      <div class="field"><label for="c-gemail">Email for your signed copy</label><input id="c-gemail" name="gemail" type="email" value="<?= h($v['gemail']) ?>" autocomplete="email" required maxlength="160"><?= $err('gemail') ?></div>
      <div class="field"><label for="c-gphone"><?= $minorView ? 'Phone on the event day' : ($pre ? 'Phone (optional)' : 'Phone (required if under 18)') ?></label><input id="c-gphone" name="gphone" type="tel" value="<?= h($v['gphone']) ?>" autocomplete="tel" maxlength="40"><?= $err('gphone') ?></div>
      <label class="check full"><input type="checkbox" name="read" value="yes"<?= !empty($_POST['read']) ? ' checked' : '' ?>> <span>I have read the consent, permission, and release of liability above and agree to it<?= $minorView ? ' on behalf of my child and myself' : '' ?>.</span></label><?= $err('read') ?>
      <label class="check full"><input type="checkbox" name="esign" value="yes"<?= !empty($_POST['esign']) ? ' checked' : '' ?>> <span>I agree to sign electronically. My typed name below is my legal signature.</span></label><?= $err('esign') ?>
      <div class="field full"><label for="c-sig">Type your full name to sign</label><input id="c-sig" name="sig" class="sig" value="<?= h($v['sig']) ?>" autocomplete="off" required maxlength="120"><?= $err('sig') ?></div>
      <div class="form-foot">
        <span class="form-note">Date signed is recorded automatically. <a href="/privacy">Privacy policy</a></span>
        <button class="btn btn-primary" type="submit">Sign consent form</button>
      </div>
    </form>
  </div>
</section>
<?php endif; ?>
</main>
<footer class="site-foot">
  <div class="wrap foot-top">
    <div class="foot-brand">
      <a href="./" aria-label="WYMIS home"><picture><source srcset="assets/img/brand/wymis-logo-light.webp" type="image/webp"><img src="assets/img/brand/wymis-logo-light.png" alt="WYMIS: What You Missed In School" width="271" height="52" loading="lazy"></picture></a>
      <p>Building the bridge between education and execution. A practical thirteenth grade for ages 16 to 26, available nationwide.</p>
      <p class="foot-np">WYMIS is a program under the umbrella of <a href="https://lovenationministries.org/" target="_blank" rel="noopener">Love Nation Inc.<span class="sr-only"> (opens in a new tab)</span></a>, a registered 501(c)(3) nonprofit organization.</p>
      <a class="foot-np-logo" href="https://lovenationministries.org/" target="_blank" rel="noopener" aria-label="Love Nation Inc. (opens in a new tab)"><img src="https://img1.wsimg.com/isteam/ip/a3d9029a-ee77-4795-b8c1-e567b129ffc1/Love%20Nation%20Without%20Slogan%20Transparent%20bg.svg" alt="Love Nation Inc." width="150" height="24" loading="lazy"></a>
      <p class="foot-tag">Discover. Learn. Build. Belong.</p>
    </div>
    <div class="foot-col"><h2>Program</h2><a href="program">How it works</a><a href="curriculum">Curriculum</a><a href="intensive">One-Day Intensive</a><a href="pilots">Pilot cities</a><a href="faq">FAQ</a></div>
    <div class="foot-col"><h2>Modules</h2><a href="curriculum#financial-literacy">Financial Literacy</a><a href="curriculum#business-fundamentals">Business Fundamentals</a><a href="curriculum#soft-skills">Soft Skills</a><a href="curriculum#etiquette">Etiquette</a><a href="curriculum#networking-principles">Networking Principles</a><a href="curriculum">All seven modules</a></div>
    <div class="foot-col"><h2>Connect</h2><a href="about">About &amp; vision</a><a href="partner">Partner with us</a><a href="mailto:info@wymisworks.org">info@wymisworks.org</a></div>
  </div>
  <div class="wrap foot-bot">
    <span>&copy; <span id="year">2026</span> WYMIS. All rights reserved.</span>
    <span class="foot-links"><a href="privacy">Privacy policy</a><a href="offer-terms">Offer terms</a><span>Site by <a href="https://atgaz.com" target="_blank" rel="noopener">ATGAZ<span class="sr-only"> (opens in a new tab)</span></a></span></span>
  </div>
</footer>
<script src="assets/js/site.js?v=52893f14" defer></script>
</body>
</html>
