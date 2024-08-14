from captcha_solver import CaptchaSolver
from xrocket_client import XRocketWeb

# GET https://captcha.ton-rocket.com/auth/twa?.. HTTP/2 with query from telegram web view
TOKEN = ""


def main():
    rocket = XRocketWeb(
        access_token=""
    )

    rocket.init_app()
    captcha = rocket.get_captcha()
    solver = CaptchaSolver(captcha)

    solution = solver.solve_captcha()
    token = rocket.verify_captcha(solution)
    if not token:
        print("Error, captcha not solved :(")
        return

    print(rocket.verify_solution(token))


if __name__ == "__main__":
    main()
