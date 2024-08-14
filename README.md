# XRocket Captcha Solver

This repository contains a Python-based captcha solver designed for the XRocket captcha system. The solution is divided into two main components:

1. **XRocketWeb Client**: Handles communication with the XRocket captcha API.
2. **CaptchaSolver**: Processes the captcha images to automatically determine the solution.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)

## Installation

To use this captcha solver, you'll need Python 3.7 or later. 

1. **Clone the repository**:

    ```bash
    git clone https://github.com/lol-1-afk/xrocket-captcha-solver.git
    cd xrocket-captcha-solver
    ```

2. **Install the required dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

   The dependencies include:
   - `requests` for handling HTTP requests.
   - `opencv-python` and `numpy` for image processing.

## Usage

### Example Script

Here's a basic example of how to use the XRocket captcha solver:

```python
from captcha_solver import CaptchaSolver
from xrocket_client import XRocketWeb

# GET https://captcha.ton-rocket.com/auth/twa?.. HTTP/2 with query from telegram web view
TOKEN = ""


def main():
    rocket = XRocketWeb(
        access_token=TOKEN
    )

    rocket.init_app()
    captcha = rocket.get_captcha()
    solver = CaptchaSolver(captcha)

    solution = solver.solve_captcha()
    token = rocket.verify_captcha(solution)
    if not token:
        print("Error, captcha not solved :(")
        return

    result_url = rocket.verify_solution(token)
    print(f"Captcha passed! Access the bot at: {result_url}")


if __name__ == "__main__":
    main()
```
