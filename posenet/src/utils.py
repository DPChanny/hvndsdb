import hashlib
import hmac
import re


def generate_hmac_signature(ts: str, key: str) -> str:
    return hmac.new(key.encode(), ts.encode(), hashlib.sha256).hexdigest()


import os


def get_last_checkpoint(folder_path: str):
    try:
        pattern = re.compile(r"^chkpnt(\d+)\.pth$")
        numbers = []

        for filename in os.listdir(folder_path):
            match = pattern.match(filename)
            if match:
                number = int(match.group(1))
                numbers.append(number)

        if not numbers:
            return None

        return max(numbers)
    except FileNotFoundError:
        return None


def clean_posenet(path: str):
    chk_pattern = re.compile(r"^chkpnt(\d+)\.pth$")
    chkpnts = []

    for f in os.listdir(path):
        match = chk_pattern.match(f)
        if match:
            chkpnts.append((int(match.group(1)), f))

    if chkpnts:
        chkpnts.sort()
        for _, f in chkpnts[:-1]:
            os.remove(os.path.join(path, f))
