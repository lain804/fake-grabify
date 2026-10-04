from curl_cffi import requests
from argparse import ArgumentParser
from bs4 import BeautifulSoup
import os

DEFAULT_SEND_COUNT = 5

parser = ArgumentParser()

parser.add_argument(
    "--user-agent","-ua", "-u", 
    type=str,
    dest="user_agent",
    default=""
)

parser.add_argument(
    "--referrer", "--referer", "-r",
    dest="referrer",
    type=str,
    default=""
)

parser.add_argument(
    "--count", "-c",
    dest="count",
    type=int,
    default=DEFAULT_SEND_COUNT
)

parser.add_argument("url")

args = parser.parse_args()

user_agent = args.user_agent

if user_agent == "":
    MAX_USERAGENT_BYTES = 4089
    user_agent = os.urandom(MAX_USERAGENT_BYTES).hex()

referrer = args.referrer
if referrer == "":
    MAX_REFERRER_BYTES = 4089
    referrer = os.urandom(MAX_REFERRER_BYTES).hex()

headers = {
    'User-Agent': user_agent,
    "Referer": referrer
}

def worker():
    with requests.Session(
        headers=headers,
        impersonate="chrome"
    ) as s:
        r = s.get(args.url)
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

        r = s.post(args.url, data=data)
        
        r.raise_for_status()

        print("sent..")

def main():
    for _ in range(args.count):
        worker()

if __name__ == "__main__":
    main()