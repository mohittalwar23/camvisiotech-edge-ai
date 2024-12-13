# Import essential libraries
import gc
import sys
from Maix import FPIOA, GPIO
from fpioa_manager import fm
from board import board_info
from machine import Timer, UART
import time
import lcd

# BLUE LED setup for intruder detection
io_led_red = 14
fm.register(io_led_red, fm.fpioa.GPIO0)
led_r = GPIO(GPIO.GPIO0, GPIO.OUT)
led_r.value(1)  # Turn off LED initially (assuming 1 is off, 0 is on)

# GSM setup for K210 (Using UART)
fm.register(10, fm.fpioa.UART1_TX, force=True)
fm.register(11, fm.fpioa.UART1_RX, force=True)
uart_A = UART(UART.UART1, 115200, 8, 1, 0, timeout=1000, read_buf_len=4096)

# Function to send AT command to GSM module
def send_at_command(command):
    print("Sending command: ", command)
    uart_A.write(command + '\r\n')
    time.sleep(0.1)
    uart_A.read()  # Clear buffer

# Function to read GSM response
def read_response(timeout=2000):
    start_time = time.ticks_ms()
    response = b""
    while time.ticks_diff(time.ticks_ms(), start_time) < timeout:
        if uart_A.any():
            response += uart_A.read()
    print("Received response: ", response.decode())
    return response.decode()

# GSM Initialization commands
def initialize_gsm():
    send_at_command('AT')  # Test AT command
    time.sleep(1)
    send_at_command('AT+CREG?')  # Network registration status
    time.sleep(1)
    send_at_command('AT+QMTCFG="recv/mode",0,0,1')  # MQTT receive mode configuration

initialize_gsm()
