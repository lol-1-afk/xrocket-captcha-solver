import hashlib
import uuid

import requests


class XRocketWeb:
    __DEFAULT_UA__ = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0"
    __CAPTCHA_PREFIX__ = "RocketCaptcha"  # DON'T CHAGE IT! Vitally necessary!!

    def __init__(self, access_token: str, fingerprint: str = "", user_agent: str = ""):
        """
        Initializates class
        :param access_token: jwt from GET https://captcha.ton-rocket.com/auth/twa
        :param fingerprint: browser fingerprint (fingerprintjs). random if not passed
        :param user_agent: browser user-agent. default if not passed
        """

        self.session = requests.session()
        self.__token = access_token
        self.__ua = user_agent or XRocketWeb.__DEFAULT_UA__
        self.__fp = fingerprint or self.__random_fp()
        self.__wv_hash = ""

        self.session.headers.update({
            "User-Agent": user_agent or XRocketWeb.__DEFAULT_UA__,
            "Origin": "https://webcaptcha2.ton-rocket.com",
            "Referer": "https://webcaptcha2.ton-rocket.com/",
            "Authorization": f"Bearer {access_token}",
            "x-rocket-captcha-cf": self.__fp,
        })

    @staticmethod
    def __random_fp() -> str:
        """
        Private static method to generate a random fingerprint. md5(uuid4)
        :return: fingerprint - str
        """

        random_token = str(uuid.uuid4())
        return hashlib.md5(random_token.encode()).hexdigest()

    def __gen_headers(self) -> dict:
        """
        Generate headers for the request with captcha token and data.
        :return: headers - dict
        """

        captcha_token = str(uuid.uuid4())

        captcha_data = hashlib.sha256(f"{XRocketWeb.__CAPTCHA_PREFIX__}:{self.__ua}:{captcha_token}".encode()).hexdigest()
        captcha_hash = hashlib.sha256(f"{XRocketWeb.__CAPTCHA_PREFIX__}:{self.__fp}:{captcha_token}".encode()).hexdigest()

        headers = {
            "x-rocket-captcha-token": captcha_token,
            "x-rocket-webview-hash": self.__wv_hash or "NotSet",
            "x-rocket-captcha-data": captcha_data,
            "x-rocket-captcha-cf-hash": captcha_hash
        }

        return headers

    def init_app(self) -> None:
        """
        Initialize the app. (step 1)
        :return: None
        """

        response = self.session.get(
            url="https://captcha.ton-rocket.com/app/init",
            headers=self.__gen_headers()
        ).json()

        if not response.get("success"):
            print(response)
            raise Exception("[1] Something bad happened")

        self.__wv_hash = response["data"]["hash"]
        # captcha_status = response["data"]["status"]
        #
        # print(f"Status: {captcha_status}")

    def get_captcha(self) -> dict:
        """
        Retrieve a captcha data (step 2)
        :return: captcha - dict
        """

        response = self.session.get(
            url="https://captcha.ton-rocket.com/captcha/fetchCaptcha"
        ).json()

        if not response.get("success"):
            print(response)
            raise Exception("[2] Something bad happened")

        return response["data"]

    def verify_captcha(self, captcha_solution: dict) -> False or str:
        """
        Verifies captcha solution. (step 3)
        :param captcha_solution: dict with coordinates and trails
        :return: solution token - str if success, else False
        """

        response = self.session.post(
            url="https://captcha.ton-rocket.com/captcha/fetchVerify",
            json=captcha_solution
        ).json()

        if not response.get("success"):
            print(response)
            raise Exception("[3] Something bad happened")

        status = response["data"]["result"]
        if not status:
            return False

        solution_token = response["data"]["token"]
        return solution_token

    def verify_solution(self, solution_token: str) -> str:
        """
        Verifies solution token. (step 4)
        :param solution_token: token from captcha verification
        :return: bot url with passed captcha - str
        """

        post_data = {
            "token": solution_token
        }

        response = self.session.post(
            url="https://captcha.ton-rocket.com/app/verify",
            headers=self.__gen_headers(),
            json=post_data
        ).json()

        if not response.get("success"):
            print(response)
            raise Exception("[4] Something bad happened")

        url = response["data"]["link"]
        return url


