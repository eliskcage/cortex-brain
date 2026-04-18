<?php
// Relay to cortex on MAIN server — bypasses Cloudflare proxy issues
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(200); exit; }

$endpoint = isset($_GET['e']) ? $_GET['e'] : '';
if (!$endpoint || !preg_match('/^[a-z0-9\-]+$/', $endpoint)) {
    echo json_encode(['error' => 'bad endpoint']);
    exit;
}

$url = 'http://185.230.216.235/alive/studio/api/' . $endpoint;
$body = file_get_contents('php://input');

// Debug log
file_put_contents('/tmp/proxy-debug.log', date('H:i:s') . " ep=$endpoint body=$body\n", FILE_APPEND);

$ch = curl_init($url);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $body);
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 30);
$result = curl_exec($ch);
$code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$err = curl_error($ch);
curl_close($ch);

file_put_contents('/tmp/proxy-debug.log', date('H:i:s') . " code=$code err=$err result=" . substr($result,0,100) . "\n", FILE_APPEND);

http_response_code($code ?: 502);
echo $result;
