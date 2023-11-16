import io
import re
import zipfile
from collections import Counter
from typing import Dict

import requests


def get_jav_config(remote: str = "https://oldschool.runescape.com/jav_config.ws") -> Dict[str, str]:
    r = requests.get(remote)
    assert r.ok

    raw = r.text.replace("msg=", "msg_").replace("param=", "param_")
    return dict(pair.split("=", 1) for pair in raw.strip().split("\n"))


def get_gamepack(jav_config: Dict[str, str]) -> bytes:
    if jav_config is None:
        jav_config = get_jav_config()

    r = requests.get(jav_config["codebase"] + jav_config["initial_jar"])
    assert r.ok

    return r.content


def get_rev_and_date(gamepack: bytes) -> (int, int):
    z = zipfile.ZipFile(io.BytesIO(gamepack))

    with z.open("client.class") as client_class:
        client_bytes = client_class.read()

    match = Counter(re.findall(bytes.fromhex('11 02fd 11 01f7 11') + b'(..)', client_bytes)).most_common(1)[0][0]

    return int.from_bytes(match, "big"), z.getinfo("client.class").date_time


def get_world_list(world_list_remote: str):
    r = requests.get(world_list_remote)
    assert r.ok

    return r.content


if __name__ == '__main__':
    jav_config: Dict[str, str] = get_jav_config()
    #world_list: bytes = get_world_list(jav_config["param_17"])
    gamepack: bytes = get_gamepack(jav_config)
    revision, _ = get_rev_and_date(gamepack)

    # zip_buffer = io.BytesIO()
    # with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
    #     zip_file.writestr('jav_config.kv', '\n'.join(f'{k}={v}' for k, v in jav_config.items()))
    #     zip_file.writestr('gamepack.jar', gamepack)
    #
    # import argparse
    #
    # parser = argparse.ArgumentParser("download")
    # parser.add_argument("-o", "--output", default=f"osrs-r{revision}.zip")
    # args = parser.parse_args()
    #
    # with open(args.output, "wb") as f:
    #     f.write(zip_buffer.getvalue())

    with open("gamepack.jar", "wb") as f:
        f.write(gamepack)

    with open("jav_config.kv", "w") as f:
        f.write('\n'.join(f'{k}={v}' for k, v in jav_config.items()))

    print(revision)




