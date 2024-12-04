from machine import PWM, ADC, Pin
import math
import utime

# Joystick connections
adc_x_joystick = ADC(Pin(26))  # X-direction connected to GPIO 26 (ADC)
adc_y_joystick = ADC(Pin(27))  # Y-direction connected to GPIO 27 (ADC)
sw_joystick = Pin(16, Pin.IN, Pin.PULL_UP)  # Switch connected to GPIO 16

# Servos for X, Y directions and the hand
servo_x = PWM(Pin(0), freq=50)  # Servo for X-axis
servo_y = PWM(Pin(1), freq=50)  # Servo for Y-axis
servo_hand = PWM(Pin(2), freq=50)  # Servo for hand control

# Helper functions
def get_joystick_value(joystick_position, joystick_min, joystick_max, desired_min, desired_max):
    m = (desired_min - desired_max) / (joystick_min - joystick_max)
    return int((m * joystick_position) - (m * joystick_max) + desired_max)

def get_servo_duty_cycle(joystick_value, min_angle_ms, max_angle_ms, period_ms, desired_min, desired_max):
    point_1_x = desired_min
    point_1_y = (min_angle_ms / period_ms) * 65536
    point_2_x = desired_max
    point_2_y = (max_angle_ms / period_ms) * 65536
    m = (point_2_y - point_1_y) / (point_2_x - point_1_x)
    return int((m * joystick_value) - (m * desired_min) + point_1_y)

# Main loop
while True:
    # Read joystick positions
    x_position = adc_x_joystick.read_u16()
    y_position = adc_y_joystick.read_u16()
    sw_status = sw_joystick.value()

    # Map joystick positions to -100 to 100
    x_value = get_joystick_value(x_position, 416, 65535, -100, 100)
    y_value = get_joystick_value(y_position, 416, 65535, -100, 100)

    # Remove noise/jitter for near-zero values
    if abs(x_value) <= 8:
        x_value = 0
    if abs(y_value) <= 8:
        y_value = 0

    # Convert joystick values to servo duty cycles
    x_duty = get_servo_duty_cycle(x_value, 0.5, 2.5, 20, -100 , 100)
    y_duty = get_servo_duty_cycle(y_value, 0.5, 2.5, 20, -100, 100)

    # Hand control: Open (0 degrees) or close (180 degrees) based on switch press
    if sw_status == 0:  # Switch pressed
        hand_duty = int((2.5 * 65536) / 20)  # 180 degrees (closed hand)
    else:
        hand_duty = int((0.5 * 65536) / 20)  # 0 degrees (open hand)

    # Update servo positions
    servo_x.duty_u16(x_duty)
    servo_y.duty_u16(y_duty)
    servo_hand.duty_u16(hand_duty)

    # Debugging output
    print(f"x_value: {x_value}, x_duty: {x_duty}, y_value: {y_value}, y_duty: {y_duty}, hand_duty: {hand_duty}, sw_status: {sw_status}")

    # Small delay for stability
    utime.sleep(0.1)
