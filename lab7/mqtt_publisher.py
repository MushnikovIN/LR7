"""
MQTT Издатель для лабораторной работы 7
Считывает значения из CSV файла и отправляет их в топик MQTT
Каждое сообщение содержит одно значение из CSV файла
"""

import csv
import time
import random
from paho.mqtt import client as mqtt_client
import paho.mqtt.client as mqtt


# Параметры MQTT
BROKER = 'broker.emqx.io'
PORT = 1883
TOPIC = "lab7/signal_variant4"
CLIENT_ID = f'lab7-publisher-{random.randint(0, 1000)}'
USERNAME = ''  # можно указать при необходимости
PASSWORD = ''  # можно указать при необходимости


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Подключено к MQTT брокеру!")
    else:
        print(f"Ошибка подключения, код возврата {rc}")

# Проверка версии paho-mqtt и создание клиента с соответствующим API
# Для paho-mqtt >= 2.0 необходимо указывать callback_api_version
if hasattr(mqtt, 'CallbackAPIVersion'):
    client = mqtt_client.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
else:
    # Для paho-mqtt < 2.0 (старая версия)
    client = mqtt_client.Client(client_id=CLIENT_ID)

client.on_connect = on_connect


def connect_mqtt() -> mqtt_client:
    """
    Подключение к MQTT брокеру.
    
    Returns:
        MQTT клиент
    """
    # Проверка версии paho-mqtt и создание клиента с соответствующим API
    # Для paho-mqtt >= 2.0 необходимо указывать callback_api_version
    if hasattr(mqtt, 'CallbackAPIVersion'):
        client = mqtt_client.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
    else:
        # Для paho-mqtt < 2.0 (старая версия)
        client = mqtt_client.Client(client_id=CLIENT_ID)
    
    client.on_connect = on_connect
    
    if USERNAME and PASSWORD:
        client.username_pw_set(USERNAME, PASSWORD)
    
    client.connect(BROKER, PORT)
    return client


def read_csv_file(filename: str) -> list[float]:
    """
    Чтение значений из CSV файла.
    
    Args:
        filename: имя CSV файла
        
    Returns:
        Список значений сигнала
    """
    values = []
    try:
        with open(filename, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                values.append(float(row['value']))
        print(f"Прочитано {len(values)} значений из файла {filename}")
    except FileNotFoundError:
        print(f"Ошибка: файл {filename} не найден!")
        print("Сначала запустите signal_generator.py для создания файла")
        raise
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")
        raise
    return values


def publish(client: mqtt_client, values: list[float], delay: float = 0.5) -> None:
    """
    Публикация значений в MQTT топик.
    
    Args:
        client: MQTT клиент
        values: список значений для публикации
        delay: задержка между публикациями (секунды)
    """
    msg_count = 0
    total_msgs = len(values)
    
    print(f"Начало публикации {total_msgs} сообщений в топик '{TOPIC}'")
    print("-" * 50)
    
    for value in values:
        msg = f"{value:.6f}"
        result = client.publish(TOPIC, msg)
        status = result[0]
        
        if status == 0:
            print(f"[{msg_count + 1}/{total_msgs}] Отправлено: {msg}")
        else:
            print(f"[{msg_count + 1}/{total_msgs}] Ошибка отправки сообщения")
        
        msg_count += 1
        time.sleep(delay)
    
    print("-" * 50)
    print(f"Публикация завершена. Отправлено {msg_count} сообщений.")


def run():
    """Основная функция запуска издателя."""
    print("=" * 50)
    print("MQTT Издатель - Лабораторная работа 7 (Вариант 4)")
    print("=" * 50)
    
    # Чтение данных из CSV
    csv_filename = "signal_data.csv"
    values = read_csv_file(csv_filename)
    
    # Подключение к MQTT
    client = connect_mqtt()
    client.loop_start()
    
    # Небольшая пауза для установления соединения
    time.sleep(1)
    
    # Публикация данных
    publish(client, values, delay=0.3)
    
    # Завершение работы
    client.loop_stop()
    client.disconnect()
    print("\nИздатель завершил работу.")


if __name__ == '__main__':
    run()
