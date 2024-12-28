## Wyjaśnienie parametrów:
  `--use_gpu:` Określa, czy używać GPU (True) lub CPU (False).

  `--language:` Język transkrypcji (np. "pl" dla polskiego, "en" dla angielskiego).

  `--input_audio:` Nazwa pliku wejściowego z audio do transkrypcji (np. "audio.mp3").

  `--model_name:` Nazwa modelu Whisper ("tiny", "medium", "large" itp.).

  `--formatting_mode:` Sposób formatowania wynikowej transkrypcji:

  `"default":` Tekst w jednym bloku.

  `"newlines_after_period":` Nowa linia po każdej kropce.

  `"timestamps":` Dodanie znaczników czasowych do każdej linii.

  `--show_progress:` Czy wyświetlać postęp transkrypcji w konsoli (True lub False).

  `--monitor_interval:` Interwał monitorowania zasobów w sekundach (np. 2).

## Wynik:
  Plik wynikowy (tiny.txt lub inny zależny od modelu) zostanie zapisany w automatycznie utworzonym podkatalogu (tiny, medium, itp.) z dodatkową numeracją w przypadku wielu uruchomień.
  Plik logów (log.txt) zawiera szczegóły użycia CPU, GPU, pamięci, temperatury oraz mocy.

Parametry w ścieżce poleceń mogą być przekazywane zarówno w cudzysłowie, jak i bez niego, pod warunkiem że nie zawierają spacji ani specjalnych znaków. Jeśli jednak wartości parametrów zawierają spacje, cudzysłowy są konieczne.

```
  python start.py --use_gpu=True --language="pl" --input_audio="audio.mp3" --model_name="tiny" --formatting_mode="timestamps" --show_progress=True --monitor_interval=2
```

lub:

```
python start.py --language=pl --input_audio=audio.mp3 --model_name=tiny
```
