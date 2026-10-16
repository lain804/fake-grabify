from curl_cffi import requests
from argparse import ArgumentParser
from bs4 import BeautifulSoup
import random
from fake_grabify.constants import DEFAULT_SEND_COUNT, MAX_REFERRER_BYTES, MAX_USERAGENT_BYTES

def worker(url,headers):
    with requests.Session(
        headers=headers,
        impersonate="chrome"
    ) as s:
        r = s.get(url)
        r.raise_for_status()

        soup = BeautifulSoup(r.text,"lxml")

        _token = soup.find(
            "meta",
            {
                "name": "csrf-token"
            }
        )

        if _token is None:
            return

        _token = _token.get("content")

        if _token is None:
            return

        special_id = soup.find(
            "meta",
            {
                "name": "id"
            }
        )

        if special_id is None:
            return

        special_id = special_id.get("content")

        if special_id is None:
            return

        data = {
            '_token': _token,
            'tos_accepted': '1',
            'privacy_accepted': '1',
            'special_id': special_id,
        }

        r = s.post(url, data=data)
        r.raise_for_status()

        print(".",end="")

def main():
    parser = ArgumentParser()

    parser.add_argument(
        "-ua", "-u", "--user-agent", 
        type=str,
        dest="user_agent",
        default=""
    )

    parser.add_argument(
        "-r", "--referrer", "--referer", 
        dest="referrer",
        type=str,
        default=""
    )

    parser.add_argument(
        "-c", "--count", 
        dest="count",
        type=int,
        default=DEFAULT_SEND_COUNT
    )

    parser.add_argument("url")

    args = parser.parse_args()

    user_agent = args.user_agent
    if user_agent == "":
        user_agent = random.randbytes(MAX_USERAGENT_BYTES).hex().upper()

    referrer = args.referrer
    if referrer == "":
        referrer = random.randbytes(MAX_REFERRER_BYTES).hex().upper()

    headers = {
        'User-Agent': user_agent,
        "Referer": referrer
    }

    for _ in range(args.count):
        worker(args.url, headers)

if __name__ == "__main__":
    main()