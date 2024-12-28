import os
import torch
import whisper
import time
from datetime import datetime
import psutil
import subprocess
import argparse
import wmi  # Dodanie obsługi WMI dla monitorowania temperatury CPU

# Argumenty wiersza poleceń
def parse_arguments():
    parser = argparse.ArgumentParser(description="Whisper transcription with GPU/CPU monitoring")
    parser.add_argument("--gpu", type=str, default="true", help="Czy używać GPU (true/false)")
    parser.add_argument("--language", type=str, default="pl", help="Język transkrypcji")
    parser.add_argument("--input", type=str, default="audio.mp3", help="Nazwa pliku wejściowego")
    parser.add_argument("--model", type=str, default="tiny", help="Model Whisper do użycia (np. tiny, medium, large)")
    parser.add_argument("--format", type=str, default="default", help="Sposób formatowania tekstu (default, newlines_after_period, timestamps)")
    parser.add_argument("--progress", type=str, default="true", help="Wyświetlanie postępu transkrypcji (true/false)")
    parser.add_argument("--interval", type=int, default=1, help="Interwał monitorowania zasobów w sekundach")
    return parser.parse_args()

args = parse_arguments()

# Konwersja argumentów string na odpowiednie typy logiczne
USE_GPU = args.gpu.lower() == "true"
SHOW_PROGRESS = args.progress.lower() == "true"
LANGUAGE = args.language
INPUT_AUDIO = args.input
MODEL_NAME = args.model
FORMATTING_MODE = args.format
MONITOR_INTERVAL = args.interval

# Funkcja do tworzenia unikalnego podkatalogu
def create_unique_output_dir(base_dir):
    counter = 0
    unique_dir = base_dir
    while os.path.exists(unique_dir):
        counter += 1
        unique_dir = f"{base_dir}_{counter}"
    os.makedirs(unique_dir)
    return unique_dir

# Funkcja do formatowania tekstu transkrypcji
def format_transcription(text, formatting_mode, segments=None):
    if formatting_mode == "newlines_after_period":
        return text.replace(". ", ".\n")
    elif formatting_mode == "timestamps" and segments:
        formatted_text = ""
        for segment in segments:
            start = segment["start"]
            end = segment["end"]
            segment_text = segment["text"].strip()
            formatted_text += f"[{start:.2f}s - {end:.2f}s] {segment_text}\n"
        return formatted_text
    return text

# Tworzenie unikalnego podkatalogu dla wyników
OUTPUT_DIR_BASE = os.path.join(os.getcwd(), MODEL_NAME)
OUTPUT_DIR = create_unique_output_dir(OUTPUT_DIR_BASE)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"{MODEL_NAME}.txt")  # Wyjściowy plik tekstowy
LOG_FILE = os.path.join(OUTPUT_DIR, "log.txt")  # Plik logów

# Wykrywanie dostępności GPU
device = "cuda" if USE_GPU and torch.cuda.is_available() else "cpu"

# Wymuś maksymalne wykorzystanie CPU w przypadku pracy na CPU
if device == "cpu":
    os.environ["OMP_NUM_THREADS"] = str(os.cpu_count())  # Ustawienie liczby wątków na maksymalną liczbę logicznych procesorów
    torch.set_num_threads(os.cpu_count())

# Informacje o urządzeniu
print(f"[INFO] Używane urządzenie: {device}")

# Wczytaj model Whisper
print(f"[INFO] Ładowanie modelu '{MODEL_NAME}' na urządzeniu '{device}'...")
model = whisper.load_model(MODEL_NAME, device=device)

# Funkcja do monitorowania zasobów
def monitor_resources(log_file, stop_flag):
    wmi_obj = wmi.WMI()  # Inicjalizacja WMI
    with open(log_file, "a", encoding="utf-8") as log:
        log.write("\n[MONITORING STARTED]\n")
        log.write("Legenda:\n")
        log.write("GPU Stats: [Utilization %, Memory Utilization %, Temperature (°C), Power Draw (W)]\n")
        log.write("CPU Temperature: [°C]\n")
        log.write("\n")
        
        while not stop_flag["stop"]:
            cpu_usage = psutil.cpu_percent(interval=MONITOR_INTERVAL)
            memory_info = psutil.virtual_memory()
            
            # Pobieranie temperatury CPU za pomocą WMI
            cpu_temps = []
            for sensor in wmi_obj.MSAcpi_ThermalZoneTemperature():
                temp_c = (sensor.CurrentTemperature / 10.0) - 273.15  # Konwersja Kelvin -> Celsius
                cpu_temps.append(temp_c)
            avg_cpu_temp = sum(cpu_temps) / len(cpu_temps) if cpu_temps else "N/A"

            if device == "cuda":
                try:
                    gpu_stats = subprocess.check_output([
                        "nvidia-smi", "--query-gpu=utilization.gpu,utilization.memory,temperature.gpu,power.draw", "--format=csv,noheader,nounits"
                    ]).decode("utf-8").strip()
                except subprocess.CalledProcessError:
                    gpu_stats = "Błąd odczytu GPU"
            else:
                gpu_stats = "GPU niedostępne"
            
            log.write(f"CPU Usage: {cpu_usage}%\n")
            log.write(f"Memory Usage: {memory_info.percent}%\n")
            log.write(f"CPU Temperature: {avg_cpu_temp}°C\n")
            log.write(f"GPU Stats: {gpu_stats}\n")
            log.flush()

# Start monitorowania w oddzielnym wątku
from threading import Thread
stop_flag = {"stop": False}
monitor_thread = Thread(target=monitor_resources, args=(LOG_FILE, stop_flag))
monitor_thread.start()

# Mierzenie czasu rozpoczęcia
start_time = time.time()
start_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"[INFO] Rozpoczęcie transkrypcji: {start_datetime}")

# Transkrypcja z opcjonalnym wyświetlaniem postępu
if SHOW_PROGRESS:
    print(f"[INFO] Rozpoczynanie transkrypcji pliku '{INPUT_AUDIO}' z podglądem postępu...")
    result = model.transcribe(INPUT_AUDIO, language=LANGUAGE, verbose=True)
else:
    print(f"[INFO] Rozpoczynanie transkrypcji pliku '{INPUT_AUDIO}'...")
    result = model.transcribe(INPUT_AUDIO, language=LANGUAGE)

# Formatowanie tekstu
formatted_text = format_transcription(result["text"], FORMATTING_MODE, result.get("segments"))

# Zapisz wynik do pliku tekstowego z odstępami dla czytelności
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("Rozpoczęcie transkrypcji: " + start_datetime + "\n\n")
    f.write(formatted_text + "\n\n")
    f.write("Zakończenie transkrypcji: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
    f.write(f"Czas trwania procesu: {time.time() - start_time:.2f} sekund\n")

# Zatrzymaj monitorowanie zasobów
stop_flag["stop"] = True
monitor_thread.join()
# Mierzenie czasu zakończenia
end_time = time.time()
end_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
duration = end_time - start_time
print(f"[INFO] Zakończenie transkrypcji: {end_datetime}")
print(f"[INFO] Czas trwania procesu: {duration:.2f} sekund")

print(f"[INFO] Transkrypcja zakończona! Wynik zapisany w pliku: {OUTPUT_FILE}")
print(f"[INFO] Logi zapisane w pliku: {LOG_FILE}")
