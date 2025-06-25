import time
import pyautogui
import cv2
import numpy as np
from PIL import ImageGrab

# Coordinates and dimensions of the fishing bar
x, y, width, height = 1664, 375, 79, 318
find_bar = False
pole_img = "Fishing Pole.png"

def fishin(goto_x, goto_y):
    Casting = True
    pole_position = pyautogui.center(pyautogui.locateOnScreen("Fishing Pole.png"))

    pixel_position_x = int(pole_position.x - 23)
    pixel_position_y = int(pole_position.y - 22)

    # print(pyautogui.pixel(pixel_position_x, pixel_position_y))  # Gets color of pixel

    if pyautogui.pixel(pixel_position_x, pixel_position_y) != (216, 175, 9):
        keyboard.press("2")
        time.sleep(.1)
        keyboard.release("2")

        mouse.move(goto_x, goto_y)
        mouse.press()
        time.sleep(.1)
        mouse.release()


def capture_bar():
    """Capture the part of the screen where the bar is located."""
    screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

def find_white_line_and_green_zone(bar_img):
    """Identify the position of the white line and the green zone."""
    # Convert the position to HSV
    hsv = cv2.cvtColor(bar_img, cv2.COLOR_BGR2HSV)

    # Define color ranges
    white_lower = np.array([0, 0, 200], np.uint8)
    white_upper = np.array([180, 30, 255], np.uint8)

    green_lower = np.array([40, 100, 100], np.uint8)
    green_upper = np.array([80, 255, 255], np.uint8)

    # Create masks
    white_mask = cv2.inRange(hsv, white_lower, white_upper)
    green_mask = cv2.inRange(hsv, green_lower, green_upper)

    # Find contours
    white_contours, _ = cv2.findContours(white_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    green_contours, _ = cv2.findContours(green_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    white_line_y = None
    green_zone_top = None
    green_zone_bottom = None

    if white_contours:
        # Assuming the largest contour is the white line
        white_line = max(white_contours, key=cv2.contourArea)
        x, white_line_y, w, h = cv2.boundingRect(white_line)

    if green_contours:
        # Assuming the largest contour is the green zone
        green_zone = max(green_contours, key=cv2.contourArea)
        x, green_zone_top, w, h = cv2.boundingRect(green_zone)
        green_zone_bottom = green_zone_top + h

    return white_line_y, green_zone_top, green_zone_bottom

def click_behavior(white_line_y, green_zone_top, green_zone_bottom):
    """Determine the clicking behavior based on the white line's position."""
    if white_line_y is None or green_zone_top is None or green_zone_bottom is None:
        return

    if white_line_y < green_zone_top:
        # White line above the green zone, stop clicking
        pyautogui.mouseUp()
    elif green_zone_top <= white_line_y <= green_zone_bottom:
        # White line within the green zone, click at a medium speed
        pyautogui.click()
        time.sleep(0.05)
    else:
        # White line below the green zone, click rapidly
        pyautogui.click()
        time.sleep(0.01)


def main():
    while True:
        # Check if the fishing bar is visible
        bar_img = capture_bar()
        white_line_y, green_zone_top, green_zone_bottom = find_white_line_and_green_zone(bar_img)

        if white_line_y is None or green_zone_top is None or green_zone_bottom is None:
            # If the bar is not visible, perform fishing pole logic
            # fishin(400, 600)
            fishin(1600, 750)
        else:
            # Handle the fishing bar
            click_behavior(white_line_y, green_zone_top, green_zone_bottom)

        time.sleep(0.01)


if __name__ == "__main__":
    main()
