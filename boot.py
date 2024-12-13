# Import essential libraries
import gc
import sys
from Maix import FPIOA, GPIO
from fpioa_manager import fm
from board import board_info
from machine import Timer
import utime
import lcd


# BLUE LED setup When intruder is detected, same logic can be replicated with buzzer essentially
io_led_red = 14
fm.register(io_led_red, fm.fpioa.GPIO0)
led_r = GPIO(GPIO.GPIO0, GPIO.OUT)
led_r.value(1)  # Turn off LED initially (assuming 1 is off, 0 is on)

# WiFi credentials
# AP must support 2.5GHz 
SSID = "Your_SSID"
PASW = "Your_Password"
THINGSPEAK_API_KEY = "API"  # Replace with your Thingspeak API key
THINGSPEAK_URL = "http://api.thingspeak.com/update?api_key={}&field1={}"

# Function and Class Definitions for HTTP Requests
try:
    import usocket as socket
except ImportError:
    import socket

class Response:
    def __init__(self, f):
        self.raw = f
        self.encoding = "utf-8"
        self._cached = None

    def close(self):
        if self.raw:
            self.raw.close()
            self.raw = None
        self._cached = None

    @property
    def content(self):
        if self._cached is None:
            try:
                self._cached = self.raw.read()
            finally:
                self.raw.close()
                self.raw = None
        return self._cached

    @property
    def text(self):
        return str(self.content, self.encoding)

    def json(self):
        import ujson
        return ujson.loads(self.content)

# Define HTTP request methods
def request(method, url, data=None, json=None, headers={}, stream=None, parse_headers=True):
    try:
        _, _, host, path = url.split('/', 3)
        addr = socket.getaddrinfo(host, 80)[0][-1]
        s = socket.socket()
        s.connect(addr)
        s.send(b"%s /%s HTTP/1.0\r\nHost: %s\r\n\r\n" % (method, path, host))
        resp = Response(s)
        return resp
    except Exception as e:
        print("Request failed:", e)
        if s:
            s.close()
        raise

def get(url, **kw):
    return request("GET", url, **kw)


# Network setup functions
def enable_esp32():
    from network_esp32 import wifi
    lcd.init()
    lcd.rotation(2)
    lcd.draw_string(100, 100, "Connecting to WIFI", lcd.RED, lcd.BLACK)

    if not wifi.isconnected():
        for i in range(5):
            try:
                wifi.reset(is_hard=True)
                lcd.clear()
                print('Trying to connect to WiFi via ESP32...')
                lcd.draw_string(100, 100, "Trying to connect", lcd.RED, lcd.BLACK)
                wifi.connect(SSID, PASW)
                if wifi.isconnected():
                    break
            except Exception as e:
                print(e)

    lcd.clear()
    print('Network state (ESP32):', wifi.isconnected(), wifi.ifconfig())
    lcd.draw_string(100, 100, "WIFI Connected", lcd.RED, lcd.BLACK)



# Enable the required network interface
enable_esp32()
