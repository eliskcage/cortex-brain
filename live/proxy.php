<?php
/**
 * CORTEX LIVE — PHP proxy to Python Cortex server (port 8643)
 * Routes: proxy.php?ep=ramble-log, proxy.php?ep=brain-live, etc.
 */
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$ep = isset($_GET['ep']) ? preg_replace('/[^a-z0-9\-]/', '', $_GET['ep']) : '';
if (!$ep) {
    echo json_encode(['ok' => false, 'error' => 'No endpoint. Use ?ep=ramble-log']);
    exit;
}

$url = 'http://localhost:8643/api/' . $ep;

$ch = curl_init($url);
curl_setopt_array($ch, [
    CURLOPT_POST => true,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT => 10,
    CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
    CURLOPT_POSTFIELDS => '{}',
]);
$resp = curl_exec($ch);
$code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($code === 200 && $resp) {
    echo $resp;
} else {
    echo json_encode(['ok' => false, 'error' => 'Cortex offline or unreachable', 'http' => $code]);
}
