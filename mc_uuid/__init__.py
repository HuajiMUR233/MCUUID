# GPL-2.0 Only
# Copyright (c) 2021 Huaji_MUR233

from uuid import UUID
import hashlib
import json
import re

import requests

__all__=["nameUUIDFromBytes","checkPlayerName","offlineUUID","onlineUUID"]


def nameUUIDFromBytes(name: bytes) -> UUID:
    md5 = hashlib.md5()
    md5.update(name)
    md5Bytes = bytearray(md5.digest())
    md5Bytes[6] &= 0x0F
    md5Bytes[6] |= 0x30
    md5Bytes[8] &= 0x3F
    md5Bytes[8] |= 0x80
    return UUID(bytes=bytes(md5Bytes))


def checkPlayerName(player: str) -> bool:
    return (re.fullmatch(r"\w+",player) is not None) and len(player)<=16


def offlineUUID(player: str) -> UUID:
    if not checkPlayerName(player):
        return None
    return nameUUIDFromBytes(("OfflinePlayer:" + player).encode())


def onlineUUID(player: str) -> UUID:
    if not checkPlayerName(player):
        return None
    response = requests.get("https://api.mojang.com/users/profiles/minecraft/" + player)
    if response.status_code == 204:
        raise Exception("No player with the given username")
    elif response.status_code != 200:
        raise Exception("Unknown error")
    result = response.json()
    trimmedUUID=result['id']
    return UUID(trimmedUUID)
