"""
Генератор сигнала апериодического звена (Вариант 4)
Формула: y(t) = k * (1 - e^(-t/T))
Сохраняет последовательность значений в файл формата CSV
"""

import csv
import math
from datetime import datetime


def generate_aperiodic_signal(k: float, T: float, duration: float, dt: float) -> list[tuple[float, float]]:
    """
    Генерирует сигнал апериодического звена.
    
    Args:
        k: коэффициент усиления
        T: постоянная времени
        duration: длительность сигнала в секундах
        dt: шаг дискретизации в секундах
    
    Returns:
        Список кортежей (время, значение сигнала)
    """
    signal_data = []
    t = 0.0
    while t <= duration:
        y = k * (1 - math.exp(-t / T))
        signal_data.append((t, y))
        t += dt
    return signal_data


def save_to_csv(data: list[tuple[float, float]], filename: str) -> None:
    """
    Сохраняет данные сигнала в CSV файл.
    
    Args:
        data: список кортежей (время, значение)
        filename: имя файла для сохранения
    """
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['time', 'value'])
        for time_val, value in data:
            writer.writerow([f"{time_val:.6f}", f"{value:.6f}"])
    print(f"Данные сохранены в файл {filename}")


def main():
    # Параметры сигнала для варианта 4
    k = 10.0       # коэффициент усиления
    T = 2.0        # постоянная времени (секунды)
    duration = 10.0  # длительность сигнала (секунды)
    dt = 0.1       # шаг дискретизации (секунды)
    
    print("Генерация сигнала апериодического звена (Вариант 4)")
    print(f"Параметры: k={k}, T={T}s, duration={duration}s, dt={dt}s")
    print(f"Формула: y(t) = {k} * (1 - e^(-t/{T}))")
    print("-" * 50)
    
    # Генерация сигнала
    signal_data = generate_aperiodic_signal(k, T, duration, dt)
    
    print(f"Сгенерировано {len(signal_data)} точек данных")
    
    # Сохранение в CSV
    output_filename = "signal_data.csv"
    save_to_csv(signal_data, output_filename)
    
    # Вывод первых нескольких значений для проверки
    print("\nПервые 10 значений сигнала:")
    print(f"{'Время (с)':<15} {'Значение':<15}")
    print("-" * 30)
    for i in range(min(10, len(signal_data))):
        t, y = signal_data[i]
        print(f"{t:<15.2f} {y:<15.4f}")
    
    print(f"\nГенерация завершена. Файл: {output_filename}")


if __name__ == '__main__':
    main()
