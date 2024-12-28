import os
import clr

# Funkcja do testowania OpenHardwareMonitor
def test_open_hardware_monitor():
    try:
        # Sprawdzenie, czy biblioteka DLL istnieje
        dll_path = os.path.join(os.getcwd(), "ohm", "OpenHardwareMonitorLib.dll")
        if not os.path.exists(dll_path):
            raise FileNotFoundError(f"Nie znaleziono pliku DLL: {dll_path}")

        # Dodanie referencji do biblioteki
        clr.AddReference(dll_path)
        from OpenHardwareMonitor.Hardware import Computer

        # Inicjalizacja OpenHardwareMonitor
        computer = Computer()
        computer.CPUEnabled = True
        computer.GPUEnabled = True
        computer.Open()

        # Testowe odczytywanie danych
        for hardware in computer.Hardware:
            hardware.Update()
            print(f"Urządzenie: {hardware.Name}")
            for sensor in hardware.Sensors:
                print(f"  Sensor: {sensor.Name}, Wartość: {sensor.Value}")
    except Exception as e:
        print(f"Błąd podczas inicjalizacji OpenHardwareMonitor: {e}")

# Wywołanie funkcji testowej
test_open_hardware_monitor()
