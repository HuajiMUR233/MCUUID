from uuid import UUID
import hashlib
import re

import requests

__all__ = ["nameUUIDFromBytes", "checkPlayerName", "offlineUUID", "onlineUUID"]


def nameUUIDFromBytes(name: bytes) -> UUID:
    """
    Static factory to retrieve a type 3 (name based) :class:`UUID` based on
    the specified byte array.

    :param name: A byte array to be used to construct a :class:`UUID`

    :return: A :class:`UUID` generated from the specified array
    """
    md5 = hashlib.md5()
    md5.update(name)
    md5Bytes = bytearray(md5.digest())
    md5Bytes[6] &= 0x0F  # clear version
    md5Bytes[6] |= 0x30  # set to version 3
    md5Bytes[8] &= 0x3F  # clear variant
    md5Bytes[8] |= 0x80  # set to IETF variant
    return UUID(bytes=bytes(md5Bytes))


def checkPlayerName(player: str) -> bool:
    """
    Check if player name is legal

    :param player: Player name

    :return: Return `True` if the player name is legal
    """
    return (re.fullmatch(r"\w+", player) is not None) and len(player) <= 16


def offlineUUID(player: str, check_name: bool = True) -> UUID:
    """
    Generate a UUID based on the player name

    :param player: Player name
    :param check_name: Whether to check the legitimacy of the player name

    :return: A :class:`UUID` generated from the player name
    """
    if check_name and not checkPlayerName(player):
        return None
    return nameUUIDFromBytes(("OfflinePlayer:" + player).encode())


def onlineUUID(player: str) -> UUID:
    """
    Get player's online UUID from Mojang API

    :param player: Player name

    :return: A :class:`UUID` get from Mojang API
    """
    if not checkPlayerName(player):
        return None
    response = requests.get("https://api.mojang.com/users/profiles/minecraft/" + player)
    if response.status_code == 204:
        raise Exception("No player with the given username")
    elif response.status_code != 200:
        raise Exception("Unknown error")
    result = response.json()
    trimmedUUID = result["id"]
    return UUID(trimmedUUID)
