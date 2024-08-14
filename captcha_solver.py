import base64
import random

import cv2
import numpy as np


class CaptchaSolver:
    def __init__(self, captcha: dict):
        """
        Initializates class
        :param captcha: dictionary containing the background and slider images encoded in base64
        """

        background_bytes = base64.b64decode(captcha["background"].encode())
        slider_bytes = base64.b64decode(captcha["slider"].encode())

        self.__background_img = cv2.imdecode(np.frombuffer(background_bytes, np.uint8), cv2.IMREAD_UNCHANGED)
        self.__slider_img = cv2.imdecode(np.frombuffer(slider_bytes, np.uint8), cv2.IMREAD_UNCHANGED)

        self.__processed_slider: np.ndarray = ...
        self.__processed_background: np.ndarray = ...

    @staticmethod
    def __process_image(image: np.ndarray) -> np.ndarray:  # some magic
        """
        Process the input image by applying Gaussian blur and Sobel edge detection
        :param image: image to be processed
        :return: processed image - np.ndarray
        """

        blurred = cv2.GaussianBlur(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), (3, 3), 0)

        processed = cv2.addWeighted(
            cv2.convertScaleAbs(cv2.Sobel(blurred, cv2.CV_16S, 1, 0, ksize=3)),
            0.5,
            cv2.convertScaleAbs(cv2.Sobel(blurred, cv2.CV_16S, 0, 1, ksize=3)),
            0.5,
            0,
        )
        return processed

    def __recognize_slider(self) -> None:
        """
        Recognize the slider on image and preprocess images
        :return: None
        """

        slider_height, slider_width = self.__slider_img.shape[:2]
        # print(f"Slider image size: {slider_width}x{slider_height}")

        if self.__slider_img.shape[2] == 3:  # If the image has no alpha channel
            self.__slider_img = cv2.cvtColor(self.__slider_img, cv2.COLOR_BGR2BGRA)  # Convert the slider image to RGBA

        lines_with_white = []
        for index, line in enumerate(self.__slider_img):
            has_white_color = any(np.any(color != [0, 0, 0, 0]) for color in line)
            if has_white_color:
                lines_with_white.append(index)

        # Find the upper and lower bounds of the rocket
        rocket_upper_y, rocket_lower_y = max(lines_with_white), min(lines_with_white)
        # print(f"Rocket upper y: {rocket_upper_y}")
        # print(f"Rocket lower y: {rocket_lower_y}")
        # print(f"Rocket size: {slider_width}x{rocket_upper_y - rocket_lower_y}")

        cropped___slider_img = self.__slider_img[rocket_lower_y:rocket_upper_y, 0:slider_height]  # extract rocket
        cropped___background_img = self.__background_img[rocket_lower_y:rocket_upper_y, 0:self.__background_img.shape[1]]

        self.__processed_slider = self.__process_image(cropped___slider_img)
        self.__processed_background = self.__process_image(cropped___background_img)

    def solve_captcha(self) -> dict:
        """
        Solves the captcha
        :return: solution - dict
        """

        self.__recognize_slider()

        x_cord = cv2.minMaxLoc(cv2.matchTemplate(self.__processed_background, self.__processed_slider, cv2.TM_CCOEFF_NORMED))[3][0]
        # print(f"Solution (X): {x_cord}")

        randlength = round(random.uniform(20, 50))  # random length of trial
        randomized_x = random.uniform(x_cord - 1, x_cord + 1)

        # first X and Y coordinate is always 0
        x_movements = [0]
        y_movements = [0]

        # simulate slider movement
        for step in range(1, randlength):
            x_movements.append(round(x_cord / (randlength / step)))
            y_movements.append(round(15 / (randlength / step)))  # 15 is Y maximum coordinate

        solution = {
            "response": round(randomized_x, 2),
            "trail": {
                "x": x_movements,
                "y": y_movements
            }
        }

        return solution
