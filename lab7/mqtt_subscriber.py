"""
MQTT Подписчик для лабораторной работы 7
Подписывается на топик MQTT, получает значения и отображает их на графике
Повторяет форму сигнала из CSV файла
"""

import time
import random
from collections import deque
from paho.mqtt import client as mqtt_client
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib.animation as animation


# Параметры MQTT
BROKER = 'broker.emqx.io'
PORT = 1883
TOPIC = "lab7/signal_variant4"
CLIENT_ID = f'lab7-subscriber-{random.randint(0, 100)}'
USERNAME = ''  # можно указать при необходимости
PASSWORD = ''  # можно указать при необходимости


class SignalSubscriber:
    """Класс подписчика MQTT с визуализацией сигнала."""
    
    def __init__(self, max_points: int = 200):
        """
        Инициализация подписчика.
        
        Args:
            max_points: максимальное количество точек для отображения на графике
        """
        self.max_points = max_points
        self.received_data = deque(maxlen=max_points)
        self.time_data = deque(maxlen=max_points)
        self.start_time = None
        
        # Настройка графика
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.line, = self.ax.plot([], [], 'b-', linewidth=2, marker='o', markersize=3)
        self.ax.set_xlabel('Время (с)', fontsize=12)
        self.ax.set_ylabel('Значение сигнала', fontsize=12)
        self.ax.set_title('Сигнал апериодического звена (Вариант 4)\nТопик: ' + TOPIC, fontsize=14)
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlim(0, max_points * 0.5)  # Примерный диапазон по X
        self.ax.set_ylim(0, 12)  # Ожидаемый диапазон значений для k=10
        
        # Статистика
        self.message_count = 0
        self.first_message_time = None
    
    def connect_mqtt(self) -> mqtt_client:
        """Подключение к MQTT брокеру."""
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print(f"Подключено к MQTT брокеру!")
                print(f"Подписка на топик: {TOPIC}")
            else:
                print(f"Ошибка подключения, код возврата {rc}")

        # Проверка версии paho-mqtt и создание клиента с соответствующим API
        # Для paho-mqtt >= 2.0 необходимо указывать callback_api_version
        if hasattr(mqtt, 'CallbackAPIVersion'):
            client = mqtt_client.Client(callback_api_version=mqtt.CallbackAPIVersion.V2, client_id=CLIENT_ID)
        else:
            # Для paho-mqtt < 2.0 (старая версия)
            client = mqtt_client.Client(client_id=CLIENT_ID)
        
        client.on_connect = on_connect
        
        if USERNAME and PASSWORD:
            client.username_pw_set(USERNAME, PASSWORD)
        
        client.connect(BROKER, PORT)
        return client
    
    def subscribe(self, client: mqtt_client) -> None:
        """Подписка на топик MQTT."""
        def on_message(client, userdata, msg):
            try:
                value = float(msg.payload.decode())
                current_time = time.time()
                
                if self.first_message_time is None:
                    self.first_message_time = current_time
                
                relative_time = current_time - self.first_message_time
                
                self.received_data.append(value)
                self.time_data.append(relative_time)
                self.message_count += 1
                
                if self.message_count % 10 == 0 or self.message_count <= 5:
                    print(f"[{self.message_count}] Получено: {value:.6f} (время: {relative_time:.2f}s)")
                    
            except ValueError as e:
                print(f"Ошибка преобразования данных: {e}")
                print(f"Полученные данные: {msg.payload.decode()}")

        client.subscribe(TOPIC)
        client.on_message = on_message
        print(f"Ожидание сообщений в топике '{TOPIC}'...")
    
    def update_plot(self, frame) -> tuple:
        """Функция обновления графика для анимации."""
        if len(self.time_data) > 0:
            self.line.set_data(list(self.time_data), list(self.received_data))
            
            # Автоподстройка масштаба
            if len(self.time_data) > 1:
                x_max = max(self.time_data) * 1.1 if max(self.time_data) > 0 else 10
                self.ax.set_xlim(0, max(x_max, 1))
                
                y_values = list(self.received_data)
                y_min = min(y_values) * 0.9 if min(y_values) > 0 else 0
                y_max = max(y_values) * 1.1 if max(y_values) > 0 else 12
                self.ax.set_ylim(y_min, y_max)
            
            self.ax.set_title(
                f'Сигнал апериодического звена (Вариант 4)\n'
                f'Топик: {TOPIC} | Получено сообщений: {self.message_count}',
                fontsize=12
            )
        
        return self.line,
    
    def run(self):
        """Запуск подписчика с визуализацией."""
        print("=" * 50)
        print("MQTT Подписчик - Лабораторная работа 7 (Вариант 4)")
        print("=" * 50)
        
        # Подключение к MQTT
        client = self.connect_mqtt()
        self.subscribe(client)
        
        # Запуск сетевого цикла в фоне
        client.loop_start()
        
        # Запуск анимации графика
        print("\nЗапуск графика... Закройте окно графика для остановки.")
        print("Нажмите Ctrl+C в консоли для завершения.\n")
        
        try:
            ani = animation.FuncAnimation(
                self.fig, 
                self.update_plot, 
                interval=500,  # Обновление каждые 500 мс
                blit=True,
                cache_frame_data=False
            )
            plt.show()
        except KeyboardInterrupt:
            print("\nОстановка по команде пользователя...")
        finally:
            client.loop_stop()
            client.disconnect()
            print(f"\nВсего получено сообщений: {self.message_count}")
            print("Подписчик завершил работу.")
    
    def save_received_data(self, filename: str = "received_signal.csv"):
        """Сохранение полученных данных в CSV файл."""
        import csv
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['time', 'value'])
            for t, v in zip(self.time_data, self.received_data):
                writer.writerow([f"{t:.6f}", f"{v:.6f}"])
        print(f"Данные сохранены в файл {filename}")


def run():
    """Основная функция запуска подписчика."""
    subscriber = SignalSubscriber(max_points=150)
    subscriber.run()


if __name__ == '__main__':
    run()
