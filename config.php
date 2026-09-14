<?php
define('DB_HOST', 'your-db-host.awardspace.net');
define('DB_NAME', 'your_db_name');
define('DB_USER', 'your_db_user');
define('DB_PASS', 'your_db_password');
define('APP_MASTER_KEY', 'REPLACE_WITH_64_HEX_CHAR_RANDOM_KEY');
define('ELEVENLABS_API_KEY', getenv('ELEVENLABS_API_KEY') ?: 'REPLACE_ME');
define('ELEVENLABS_AGENT_ID', getenv('ELEVENLABS_AGENT_ID') ?: 'REPLACE_ME');
define('VOICE_WEBHOOK_SECRET', 'REPLACE_WITH_RANDOM_SECRET');
define('CLASSIFICATION_LEVELS', ['unclassified'=>1,'restricted'=>2,'secret'=>3,'top_secret'=>4]);
date_default_timezone_set('Asia/Dubai');
if (session_status() === PHP_SESSION_NONE) {
    session_set_cookie_params(['lifetime'=>0,'path'=>'/','secure'=>true,'httponly'=>true,'samesite'=>'Strict']);
    session_start();
}
function db(): mysqli {
    static $conn = null;
    if ($conn === null) {
        mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
        $conn = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);
        $conn->set_charset('utf8mb4');
    }
    return $conn;
}
