"""
The MIT License (MIT)

Copyright (c) 2023-present AbstractUmbra

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

from Crypto import Random  # noqa: S413 # not `pycrypto`
from Crypto.Cipher import AES  # noqa: S413 # not `pycrypto`
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad

from .utils import from_json

SHITTY_NEWTONSOFT_SUB_PATTERN: re.Pattern[str] = re.compile(r"(?<={|,)\s*(\d+)\s*:")

if TYPE_CHECKING:
    from os import PathLike

__all__ = (
    "decrypt",
    "encrypt",
)


def _resolve_shitty_newtonsoft_int_dict_keys(input_: str) -> str:
    return SHITTY_NEWTONSOFT_SUB_PATTERN.sub(r'"\1":', input_)


def _strip_shitty_type_kv(input_: dict[str, Any] | list[str] | str) -> dict[str, Any] | list[str] | str:
    if isinstance(input_, dict):
        return {k: _strip_shitty_type_kv(v) for k, v in input_.items() if k != "__type"}
    if isinstance(input_, list):
        return [_strip_shitty_type_kv(item) for item in input_]  # pyright: ignore[reportReturnType] # this is icky due to nesting
    return input_


def encrypt(*, path: str | PathLike[str] | Path | None = None, data: bytes | None = None, password: str) -> bytes:
    if not path and not data:
        raise ValueError("Either `path` or `data` must be provided.")

    if path:
        if not isinstance(path, Path):
            path = Path(path)

        with path.open("rb") as fp:
            data_to_encrypt = fp.read()
    else:
        data_to_encrypt = data
        assert data_to_encrypt  # guarded earlier

    # Generate a random IV (Initialization Vector)
    init_vector = Random.new().read(16)

    # Derive the key using PBKDF2 with SHA1 hash algorithm
    key = PBKDF2(password, init_vector, dkLen=16, count=100)

    # Create AES cipher object
    cipher = AES.new(key, AES.MODE_CBC, init_vector)  # pyright: ignore[reportUnknownMemberType] # the overload is broken

    # Pad the data with PKCS7 before encryption
    padded_data = pad(data_to_encrypt, AES.block_size)

    # Encrypt the data
    return init_vector + cipher.encrypt(padded_data)


def decrypt(
    *, path: str | PathLike[str] | Path | None = None, data: bytes | None = None, password: str, strip_type_key: bool = False
) -> Any:  # it returns the type of file we decrypt but alas
    if not path and not data:
        raise ValueError("Either `path` or `data` must be provided.")

    if path:
        if not isinstance(path, Path):
            path = Path(path)

        with path.open("rb") as fp:
            read_data = fp.read()
    else:
        read_data = data
        assert read_data  # guarded earlier

    # The initialisation vector is the first 16 bytes of the save file.
    init_vector = read_data[:16]
    # then we take the proceeding N bytes as the data
    to_decrypt = read_data[16:]

    # create the decryption key from the provided data
    decryption_key = PBKDF2(password, init_vector, dkLen=16, count=100)

    # with the key we create the needed cipher
    cipher = AES.new(decryption_key, AES.MODE_CBC, init_vector)  # pyright: ignore[reportUnknownMemberType] # the overload is broken

    # and now we decrypt the data
    decrypted_data = unpad(cipher.decrypt(to_decrypt), AES.block_size)

    # and it's always UTF-8
    resolved_data = decrypted_data.decode("utf-8")
    resolved_data = _resolve_shitty_newtonsoft_int_dict_keys(resolved_data)
    json_data = from_json(resolved_data)

    return _strip_shitty_type_kv(json_data) if strip_type_key else json_data  # pyright: ignore[reportArgumentType] # nested typed
