<?php
// Funkcja parsowania argumentów wiersza poleceń
function parseArguments($argv) {
    $args = [];
    foreach ($argv as $arg) {
        if (preg_match('/--([^=]+)=(.*)/', $arg, $match)) {
            $args[$match[1]] = $match[2];
        }
    }
    return $args;
}

// Parsowanie argumentów
$args = parseArguments($argv);
$use_gpu = $args['gpu'] ?? 'true';
$language = $args['language'] ?? 'pl';
$input_audio = $args['input'] ?? 'audio.mp3';
$model_name = $args['model'] ?? 'tiny';
$formatting_mode = $args['format'] ?? 'default';
$progress = $args['progress'] ?? 'true';
$monitor_interval = $args['interval'] ?? 1;

// Funkcja do tworzenia unikalnego podkatalogu
function createUniqueOutputDir($baseDir) {
    $counter = 0;
    $uniqueDir = $baseDir;
    while (is_dir($uniqueDir)) {
        $counter++;
        $uniqueDir = $baseDir . "_" . $counter;
    }
    mkdir($uniqueDir, 0777, true);
    return $uniqueDir;
}

// Tworzenie podkatalogu dla wyników
$outputDirBase = getcwd() . "/" . $model_name;
$outputDir = createUniqueOutputDir($outputDirBase);
$outputFile = $outputDir . "/" . $model_name . ".txt";
$logFile = $outputDir . "/log.txt";

// Urządzenie do transkrypcji
$device = ($use_gpu === 'true' && file_exists('/usr/bin/nvidia-smi')) ? 'cuda' : 'cpu';

// Informacje o urządzeniu
echo "[INFO] Używane urządzenie: $device\n";

// Funkcja formatowania tekstu transkrypcji
function formatTranscription($text, $formattingMode, $segments = []) {
    if ($formattingMode === 'newlines_after_period') {
        return str_replace('. ', ".\n", $text);
    } elseif ($formattingMode === 'timestamps' && !empty($segments)) {
        $formattedText = "";
        foreach ($segments as $segment) {
            $start = $segment['start'];
            $end = $segment['end'];
            $segmentText = trim($segment['text']);
            $formattedText .= "[{$start}s - {$end}s] $segmentText\n";
        }
        return $formattedText;
    }
    return $text;
}

// Funkcja do monitorowania zasobów
function monitorResources($logFile, $interval) {
    $log = fopen($logFile, 'a');
    fwrite($log, "[MONITORING STARTED]\n");
    for ($i = 0; $i < 10; $i++) { // Monitoruj przez określoną liczbę cykli
        $cpuUsage = sys_getloadavg();
        fwrite($log, "CPU Usage: {$cpuUsage[0]}%\n");
        sleep($interval);
    }
    fclose($log);
}

// Uruchomienie monitorowania w tle
if (strtolower(PHP_OS) === 'winnt') {
    $command = "php monitor.php --logFile=\"$logFile\" --interval=$monitor_interval";
    pclose(popen("start /B $command", "r"));
} else {
    $pid = exec("php monitor.php --logFile=\"$logFile\" --interval=$monitor_interval > /dev/null & echo $!");
}

// Rozpoczęcie transkrypcji
$startTime = microtime(true);
echo "[INFO] Rozpoczęcie transkrypcji pliku '$input_audio'...\n";

// Tutaj można zintegrować z biblioteką transkrypcji w PHP
$result = [
    'text' => "Przykładowy wynik transkrypcji.",
    'segments' => [
        ['start' => 0.00, 'end' => 5.00, 'text' => "To jest pierwszy segment."],
        ['start' => 5.00, 'end' => 10.00, 'text' => "To jest drugi segment."]
    ]
];

// Formatowanie i zapis wyników
$formattedText = formatTranscription($result['text'], $formatting_mode, $result['segments']);
file_put_contents($outputFile, $formattedText);

// Czas zakończenia
$endTime = microtime(true);
$duration = $endTime - $startTime;
echo "[INFO] Czas trwania procesu: {$duration} sekund\n";
echo "[INFO] Transkrypcja zakończona! Wynik zapisany w: $outputFile\n";
