import os
import torch
import whisper
import time
from datetime import datetime
import psutil
import subprocess

# Configurable variables
USE_GPU = True  # Set True to force GPU usage, False to force CPU
LANGUAGE = "pl"  # Language for transcription
INPUT_AUDIO = "audio.mp3"  # Input audio file name
MODEL_NAME = "medium"  # Model name: 'tiny', 'medium', 'large', etc.
FORMATTING_MODE = "timestamps"  # Formatting mode: "default", "newlines_after_period", "timestamps"
SHOW_PROGRESS = True  # Display progress in the console
MONITOR_INTERVAL = 1  # Resource monitoring interval in seconds

# Function to create a unique output directory
def create_unique_output_dir(base_dir):
    counter = 0
    unique_dir = base_dir
    while os.path.exists(unique_dir):
        counter += 1
        unique_dir = f"{base_dir}_{counter}"
    os.makedirs(unique_dir)
    return unique_dir

# Function to format transcription text
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

# Create unique output directory for results
OUTPUT_DIR_BASE = os.path.join(os.getcwd(), MODEL_NAME)
OUTPUT_DIR = create_unique_output_dir(OUTPUT_DIR_BASE)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"{MODEL_NAME}.txt")  # Output text file
LOG_FILE = os.path.join(OUTPUT_DIR, "log.txt")  # Log file

# Detect device availability
device = "cuda" if USE_GPU and torch.cuda.is_available() else "cpu"

# Maximize CPU thread usage if running on CPU
if device == "cpu":
    os.environ["OMP_NUM_THREADS"] = str(psutil.cpu_count(logical=True))
    torch.set_num_threads(psutil.cpu_count(logical=True))

# Device info
print(f"[INFO] Using device: {device}")

# Load Whisper model
print(f"[INFO] Loading model '{MODEL_NAME}' on device '{device}'...")
model = whisper.load_model(MODEL_NAME, device=device)

# Function to monitor system resources
def monitor_resources(log_file, stop_flag):
    with open(log_file, "a", encoding="utf-8") as log:
        log.write("\n[MONITORING STARTED]\n")
        while not stop_flag["stop"]:
            cpu_usage = psutil.cpu_percent(interval=MONITOR_INTERVAL)
            memory_info = psutil.virtual_memory()
            gpu_stats = "GPU unavailable"
            if device == "cuda":
                try:
                    gpu_stats = subprocess.check_output([
                        "nvidia-smi", "--query-gpu=utilization.gpu,utilization.memory,temperature.gpu,power.draw",
                        "--format=csv,noheader,nounits"
                    ]).decode("utf-8").strip()
                except subprocess.CalledProcessError:
                    gpu_stats = "Error fetching GPU stats"
            log.write(f"CPU Usage: {cpu_usage}%\n")
            log.write(f"Memory Usage: {memory_info.percent}%\n")
            log.write(f"GPU Stats: {gpu_stats}\n")
            log.flush()

# Start resource monitoring in a separate thread
from threading import Thread
stop_flag = {"stop": False}
monitor_thread = Thread(target=monitor_resources, args=(LOG_FILE, stop_flag))
monitor_thread.start()

# Measure start time
start_time = time.time()
start_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"[INFO] Transcription started: {start_datetime}")

# Perform transcription with optional progress display
if SHOW_PROGRESS:
    print(f"[INFO] Starting transcription of '{INPUT_AUDIO}' with progress display...")
    result = model.transcribe(INPUT_AUDIO, language=LANGUAGE, verbose=True)
else:
    print(f"[INFO] Starting transcription of '{INPUT_AUDIO}'...")
    result = model.transcribe(INPUT_AUDIO, language=LANGUAGE)

# Format transcription text
formatted_text = format_transcription(result["text"], FORMATTING_MODE, result.get("segments"))

# Save the result to a text file
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("Transcription started: " + start_datetime + "\n\n")
    f.write(formatted_text + "\n\n")
    f.write("Transcription ended: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
    f.write(f"Duration: {time.time() - start_time:.2f} seconds\n")

# Stop resource monitoring
stop_flag["stop"] = True
monitor_thread.join()

# Measure end time
end_time = time.time()
end_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
duration = end_time - start_time
print(f"[INFO] Transcription ended: {end_datetime}")
print(f"[INFO] Duration: {duration:.2f} seconds")

print(f"[INFO] Transcription completed! Result saved to: {OUTPUT_FILE}")
print(f"[INFO] Logs saved to: {LOG_FILE}")
