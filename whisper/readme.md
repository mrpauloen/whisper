
>Ten kod to skrypt w Pythonie, który wykorzystuje model Whisper do transkrypcji dźwięku na tekst z możliwością monitorowania zasobów systemowych (CPU, GPU, pamięci) w trakcie działania. Oto jego kluczowe funkcjonalności.



## Opis głównych funkcji:

1. **Argumenty wiersza poleceń:**

    Skrypt pozwala na konfigurację za pomocą argumentów wiersza poleceń, takich jak:
    
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

2. **Tworzenie unikalnego katalogu wyników:**

Wyniki transkrypcji są zapisywane w osobnym podkatalogu nazwanym na podstawie wybranego modelu. Jeśli katalog już istnieje, skrypt automatycznie dodaje kolejne numery w nazwie.

3. **Wybór urządzenia (GPU/CPU):**

Skrypt automatycznie sprawdza, czy dostępne jest GPU, i wybiera odpowiednie urządzenie. Dodatkowo można wymusić użycie CPU lub GPU.

4. **Monitorowanie zasobów systemowych:**
* Dla GPU: wykorzystanie, temperatura, obciążenie pamięci, pobór mocy (za pomocą nvidia-smi).
* Dla CPU: procentowe obciążenie procesora i zużycie pamięci RAM.
* Dane są zapisywane do pliku log.txt w trakcie działania skryptu.

5. **Transkrypcja audio:**
Obsługuje różne modele Whisper do transkrypcji audio.
Możliwość podglądu postępu transkrypcji w konsoli.

6. **Formatowanie wyników:**
 * Standardowe formatowanie tekstu.
 * Dodawanie timestampów do wyników.
 * Tworzenie nowego wiersza po kropce.

7. **Zapisywanie wyników:**
Transkrypcja jest zapisywana do pliku tekstowego z datą rozpoczęcia i zakończenia, czasem trwania oraz sformatowanym tekstem.

8. **Logowanie wyników:**
Szczegóły dotyczące użycia CPU, GPU i pamięci są zapisywane do pliku logów, co pozwala na analizę wydajności procesu.

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


## Główne zastosowanie:

Kod jest idealny do przetwarzania dużych ilości plików audio w różnych językach, z jednoczesnym śledzeniem obciążenia systemu. Dzięki rozbudowanym funkcjom monitorowania i formatowania wyników, użytkownik ma pełną kontrolę nad procesem transkrypcji i jego wynikami.
