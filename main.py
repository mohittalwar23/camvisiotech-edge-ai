# Import libraries
import sensor, image, lcd, time
import KPU as kpu
from machine import Timer, UART
from Maix import GPIO
from fpioa_manager import fm
import utime

# MQTT Config
BROKER_ADDRESS = "mqtt3.thingspeak.com"
PORT = 1883
MQTT_CLIENT_ID = "your_client_id"
MQTT_USER = "same_as_client_id"
MQTT_PASSWORD = "your_password"
PUBLISH_TOPIC = "channels/channel_id/publish/fields/field_number"

# UART for GSM communication
fm.register(10, fm.fpioa.UART1_TX, force=True)
fm.register(11, fm.fpioa.UART1_RX, force=True)
uart_A = UART(UART.UART1, 115200, 8, 1, 0, timeout=1000, read_buf_len=4096)

# Send AT command to GSM module
def send_at_command(command):
    uart_A.write(command + '\r\n')
    time.sleep(0.1)
    uart_A.read()  # Clear buffer

# Read GSM response
def read_response(timeout=2000):
    start_time = time.ticks_ms()
    response = b""
    while time.ticks_diff(time.ticks_ms(), start_time) < timeout:
        if uart_A.any():
            response += uart_A.read()
    return response.decode()

# MQTT commands
def connect_mqtt():
    send_at_command('AT+QMTOPEN=0,"{}",{}'.format(BROKER_ADDRESS, PORT))
    time.sleep(1)
    read_response()
    send_at_command('AT+QMTCONN=0,"{}","{}","{}"'.format(MQTT_CLIENT_ID, MQTT_USER, MQTT_PASSWORD))
    time.sleep(1)
    read_response()

# Publish data to MQTT
def publish_data(field_value):
    payload = "{}".format(field_value)
    send_at_command('AT+QMTPUBEX=0,0,0,0,"{}",2'.format(PUBLISH_TOPIC))
    uart_A.write(payload + '\r\n')
    read_response()

# Initialize face recognition
task_fd = kpu.load(0x300000)
task_ld = kpu.load(0x500000)
task_fe = kpu.load(0x600000)

# Key setup for starting processing
fm.register(board_info.BOOT_KEY, fm.fpioa.GPIOHS0)
key_gpio = GPIO(GPIO.GPIOHS0, GPIO.IN)
start_processing = False

def set_key_state(*_):
    global start_processing
    start_processing = True
    utime.sleep_ms(50)  # Debounce

key_gpio.irq(set_key_state, GPIO.IRQ_RISING, GPIO.WAKEUP_NOT_SUPPORT)

# Timer and Camera Setup
tim = Timer(Timer.TIMER0, Timer.CHANNEL0, mode=Timer.MODE_PERIODIC, period=5, unit=Timer.UNIT_S, callback=None, start=False)
lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_hmirror(1)
sensor.set_vflip(1)
sensor.run(1)

# Main loop with face detection
while True:
    if start_processing:
        img = sensor.snapshot()
        objects = kpu.run_yolo2(task_fd, img)

        if objects:
            for obj in objects:
                # Draw detected object box
                img.draw_rectangle(obj.rect())
                fmap = kpu.forward(task_ld, img)
                kpu.set_output(task_fe, 0, fmap)
                feature = kpu.get_output(task_fe, 0)

                # Example field value from feature for Thingspeak
                field1_value = sum(feature[:3])
                print("Detected face feature (field1 value):", field1_value)

                # Send data via MQTT
                connect_mqtt()
                publish_data(field1_value)

                # LED indication for detected face
                led_r.value(0)  # Turn on LED
                time.sleep(0.1)
                led_r.value(1)  # Turn off LED
    else:
        time.sleep(0.1)
