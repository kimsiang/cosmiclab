<?php
/**
 * Cosmic Lab — AI Assistant endpoint
 * Upload to: public_html/api/chat.php
 *
 * Proxies chat messages from the landing-page widget to the Claude API.
 * The API key lives in claude_config.php OUTSIDE public_html (see setup guide).
 */

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');

// mbstring may be absent on some shared hosts — fall back to byte functions
if (!function_exists('mb_strlen')) {
  function mb_strlen($s) { return strlen($s); }
}
if (!function_exists('mb_substr')) {
  function mb_substr($s, $start, $len = null) {
    return $len === null ? substr($s, $start) : substr($s, $start, $len);
  }
}

// ── Same-origin only ─────────────────────────────────────────────
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
  http_response_code(405);
  echo json_encode(['error' => 'method_not_allowed']);
  exit;
}

// ── Load config (API key) from outside the web root ──────────────
$configCandidates = [
  dirname(__DIR__, 2) . '/claude_config.php',  // one level above public_html
  dirname(__DIR__)   . '/claude_config.php',   // fallback: inside public_html root
];
$CLAUDE_API_KEY = null;
foreach ($configCandidates as $c) {
  if (is_readable($c)) { require $c; break; }
}
if (empty($CLAUDE_API_KEY) || $CLAUDE_API_KEY === 'sk-ant-PASTE-YOUR-KEY-HERE') {
  http_response_code(500);
  echo json_encode(['error' => 'not_configured',
    'reply' => 'The assistant is not set up yet. Please email hello@cosmiclab.my.']);
  exit;
}

// ── Simple per-IP rate limit: 8 requests / 10 minutes ────────────
$ip     = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
$rlFile = sys_get_temp_dir() . '/cl_rl_' . md5($ip);
$now    = time();
$stamps = is_readable($rlFile) ? array_filter(
            explode(',', (string)file_get_contents($rlFile)),
            fn($t) => (int)$t > $now - 600
          ) : [];
if (count($stamps) >= 8) {
  http_response_code(429);
  echo json_encode(['error' => 'rate_limited',
    'reply' => 'You have asked quite a few questions — please wait a few minutes, or email hello@cosmiclab.my.']);
  exit;
}
$stamps[] = $now;
@file_put_contents($rlFile, implode(',', $stamps), LOCK_EX);

// ── Parse & validate input ────────────────────────────────────────
$in      = json_decode((string)file_get_contents('php://input'), true) ?: [];
$message = trim((string)($in['message'] ?? ''));
$lang    = in_array($in['lang'] ?? 'en', ['en', 'zh', 'ms'], true) ? $in['lang'] : 'en';

if ($message === '' || mb_strlen($message) > 500) {
  http_response_code(400);
  echo json_encode(['error' => 'bad_message']);
  exit;
}

// Sanitise history: alternating user/assistant strings, last 8 turns max
$history = [];
foreach (array_slice((array)($in['history'] ?? []), -8) as $turn) {
  $role = ($turn['role'] ?? '') === 'assistant' ? 'assistant' : 'user';
  $text = mb_substr(trim((string)($turn['content'] ?? '')), 0, 600);
  if ($text !== '') $history[] = ['role' => $role, 'content' => $text];
}
$history[] = ['role' => 'user', 'content' => $message];

// ── System prompt: course facts only ──────────────────────────────
$langName = ['en' => 'English', 'zh' => 'Simplified Chinese', 'ms' => 'Bahasa Malaysia'][$lang];
$system = <<<SYS
You are the friendly enrolment assistant on the Cosmic Lab website. Cosmic Lab is a
1-day online physics masterclass for Malaysian secondary students (Form 4-6, ages 15-18).

COURSE FACTS — only ever state these; never invent details:
- Format: live online, 9:00 AM to 2:30 PM Malaysia time (4.5 hours of sessions plus a lunch break).
- Content: students analyse 100,000+ real muon-detector events in Python using Google Colab
  (no installation; a laptop, stable internet, and a Google account are needed). No prior
  coding or advanced physics required — notebooks are pre-built with guidance.
- Sessions: intro physics lecture with live Q&A, two hands-on Python sessions (histograms,
  muon flux, track reconstruction, an underground-tunnel muography dataset), and short
  student presentations at the end.
- Instructor: a Malaysian particle physicist. Class is taught in English; the instructor
  can clarify in Bahasa Malaysia. Parents may observe.
- Price: RM 199 per student (early-bird; usual price RM 499), one-time, all materials
  included. Includes certificate of completion signed by the physicist, 30-day recording
  access, and a WhatsApp alumni/support group.
- Enrolment: fill in the "Register Your Interest" form on this page; a WhatsApp payment
  link follows within 24 hours. Questions: hello@cosmiclab.my.
- Relevance: the completed project is a strong talking point for JPA/MARA scholarship and
  university applications.

RULES:
- Reply in {$langName} unless the visitor clearly writes in another of: English, Bahasa
  Malaysia, Simplified Chinese — then match them.
- Keep replies under 120 words, warm and plain-spoken. Many visitors are teenagers or
  parents; keep every reply age-appropriate and never request personal information.
- You may also answer basic curiosity questions about muons, cosmic rays, relativity, and
  muography at a high-school level.
- Politely decline anything unrelated (homework answers, other products, personal advice)
  and steer back to the course.
- Never promise scholarship outcomes, discounts beyond RM 199, or specific class dates —
  for dates, point to the registration form.
SYS;

// ── Call the Claude API ────────────────────────────────────────────
$payload = json_encode([
  'model'      => 'claude-haiku-4-5-20251001',
  'max_tokens' => 400,
  'system'     => $system,
  'messages'   => $history,
]);

$ch = curl_init('https://api.anthropic.com/v1/messages');
curl_setopt_array($ch, [
  CURLOPT_POST           => true,
  CURLOPT_POSTFIELDS     => $payload,
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_TIMEOUT        => 25,
  CURLOPT_HTTPHEADER     => [
    'Content-Type: application/json',
    'x-api-key: ' . $CLAUDE_API_KEY,
    'anthropic-version: 2023-06-01',
  ],
]);
$resp   = curl_exec($ch);
$status = curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
$cerr   = curl_error($ch);
curl_close($ch);

$fallback = [
  'en' => 'Sorry — I could not reach the assistant just now. Please try again in a moment, or email hello@cosmiclab.my.',
  'zh' => '抱歉，助手暂时无法连接。请稍后再试，或发送邮件至 hello@cosmiclab.my。',
  'ms' => 'Maaf — pembantu tidak dapat dihubungi buat masa ini. Sila cuba sebentar lagi, atau e-mel hello@cosmiclab.my.',
][$lang];

if ($resp === false || $status !== 200) {
  error_log("CosmicLab chat error: HTTP $status $cerr " . substr((string)$resp, 0, 300));
  http_response_code(502);
  echo json_encode(['error' => 'upstream', 'reply' => $fallback]);
  exit;
}

$data  = json_decode($resp, true);
$reply = '';
foreach (($data['content'] ?? []) as $block) {
  if (($block['type'] ?? '') === 'text') $reply .= $block['text'];
}
$reply = trim($reply);
if ($reply === '') $reply = $fallback;

echo json_encode(['reply' => $reply]);
