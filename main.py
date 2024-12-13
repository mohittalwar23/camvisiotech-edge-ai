# Import libraries
import sensor, image, lcd, time
import KPU as kpu
from machine import Timer
from Maix import GPIO
from fpioa_manager import fm
from board import board_info
from machine import Timer
import utime
import utime


# Face Recognition and Detection Setup
task_fd = kpu.load(0x300000)
task_ld = kpu.load(0x500000)
task_fe = kpu.load(0x600000)


# Anchors and key points for face alignment
anchor = (1.889, 2.5245, 2.9465, 3.94056, 3.99987, 5.3658, 5.155437, 6.92275, 6.718375, 9.01025)
dst_point = [(44, 59), (84, 59), (64, 82), (47, 105), (81, 105)]  # standard face key point positions
a = kpu.init_yolo2(task_fd, 0.5, 0.3, 5, anchor)

record_ftrs = []  # List to hold registered face features
names = ['Person 1', 'Person 2', 'Person 3']  # Sample names
ACCURACY = 80

## Key setup for starting processing
fm.register(board_info.BOOT_KEY, fm.fpioa.GPIOHS0)
key_gpio = GPIO(GPIO.GPIOHS0, GPIO.IN)
start_processing = False

def set_key_state(*_):
    global start_processing
    start_processing = True
    utime.sleep_ms(50)  # Bounce protection

key_gpio.irq(set_key_state, GPIO.IRQ_RISING, GPIO.WAKEUP_NOT_SUPPORT)

# Thingspeak integration and Face Processing Logic
def on_timer(timer):
    global timer_triggered
    timer_triggered = True
    led_r.value(0)  # Turn on LED to indicate unknown face detection
    field1_value = 90  # Example value for Thingspeak
    thingspeak_url = THINGSPEAK_URL.format(THINGSPEAK_API_KEY, field1_value)

    res = get(thingspeak_url)
    if res.status_code == 200:
        print("Data sent successfully to Thingspeak.")
    else:
        print("Failed to send data to Thingspeak. Status code:", res.status_code)

# Timer and Camera Setup
tim = Timer(Timer.TIMER0, Timer.CHANNEL0, mode=Timer.MODE_PERIODIC, period=5, unit=Timer.UNIT_S, callback=on_timer, start=False)
lcd.init()
lcd.rotation(2)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_hmirror(1)
sensor.set_vflip(1)
sensor.run(1)


# Start the main loop
while (True):
    img = sensor.snapshot()
    objects = kpu.run_yolo2(task_fd, img)  # Detect multiple faces

    if objects:  # If faces are detected
        for obj in objects:  # Loop over each detected face
            # Draw the face rectangle
            img.draw_rectangle(obj.rect())

            # Cut and resize the detected face
            face_cut = img.cut(obj.x(), obj.y(), obj.w(), obj.h()).resize(128, 128)
            face_cut.pix_to_ai()

            # Landmark detection for aligning face
            fmap = kpu.forward(task_ld, face_cut)
            plist = fmap[:]
            le = (obj.x() + int(plist[0] * obj.w() - 10), obj.y() + int(plist[1] * obj.h()))
            re = (obj.x() + int(plist[2] * obj.w()), obj.y() + int(plist[3] * obj.h()))
            nose = (obj.x() + int(plist[4] * obj.w()), obj.y() + int(plist[5] * obj.h()))
            lm = (obj.x() + int(plist[6] * obj.w()), obj.y() + int(plist[7] * obj.h()))
            rm = (obj.x() + int(plist[8] * obj.w()), obj.y() + int(plist[9] * obj.h()))

            # Align face to the standard position for recognition
            src_point = [le, re, nose, lm, rm]
            T = image.get_affine_transform(src_point, dst_point)
            image.warp_affine_ai(img, face_cut, T)
            face_cut.ai_to_pix()

            # Feature extraction and comparison
            fmap = kpu.forward(task_fe, face_cut)
            feature = kpu.face_encode(fmap[:])

            max_score = 0
            index = -1

            # Check if any faces are registered
            if len(record_ftrs) > 0:
                # Compare with registered features
                for j in range(len(record_ftrs)):
                    score = kpu.face_compare(record_ftrs[j], feature)
                    if score > max_score:
                        max_score = score
                        index = j

                # If recognized, reset timer and stop trigger
                if max_score > ACCURACY:
                    img.draw_string(obj.x(), obj.y(), "{}: {:.1f}".format(names[index], max_score), scale=2, color=(0, 255, 0))
                    tim.stop()  # Stop timer if recognized
                    timer_started = False  # Reset timer flag
                    timer_triggered = False  # Reset trigger flag
                    led_r.value(1)  # Turn off LED
                else:
                    # Unrecognized face, start the timer if not already running
                    img.draw_string(obj.x(), obj.y(), "Unknown: {:.1f}".format(max_score), scale=2, color=(255, 0, 0))
                    if not timer_started:
                        tim.start()
                        timer_started = True
            else:
                img.draw_string(obj.x(), obj.y(), "No faces registered", scale=2, color=(255, 0, 0))

            # If key is pressed, register the face
            if start_processing:
                record_ftrs.append(feature)
                start_processing = False

    else:
        tim.stop()  # No face detected, stop the timer
        timer_started = False  # Reset timer flag
        timer_triggered = False
        led_r.value(1)  # Turn off LED when no face is detected

    # Display the image on the LCD
    lcd.display(img)
    gc.collect()

    # Trigger the action if timer ran for 5+ seconds
    if timer_triggered:
        print("Taking action due to unknown face!")
        #led_r.value(1)  # Turn off LED after action
        timer_triggered = False  # Reset trigger flag after action

