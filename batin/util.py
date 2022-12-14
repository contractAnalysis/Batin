"""This module contains various utility functions regarding unit conversion and
solc integration."""
import binascii
import json
import sys
import os
import platform
from pathlib import Path
from subprocess import PIPE, Popen
import solc
from ethereum.abi import encode_abi, encode_int, method_id
from ethereum.utils import zpad

from batin.exceptions import CriticalError,CompilerError
from semantic_version import Version
from batin import util

import re
import logging
log = logging.getLogger(__name__)


if sys.version_info[1] >= 6:
    import solcx
    from solcx.exceptions import SolcNotInstalled


def safe_decode(hex_encoded_string):
    """

    :param hex_encoded_string:
    :return:
    """
    if hex_encoded_string.startswith("0x"):
        return bytes.fromhex(hex_encoded_string[2:])
    else:
        return bytes.fromhex(hex_encoded_string)


def get_solc_json(file, solc_binary="solc", solc_settings_json=None):
    """

    :param file:
    :param solc_binary:
    :param solc_settings_json:
    :return:
    """
    # cmd = [solc_binary, "--optimize", "--standard-json", "--allow-paths", "."]
    cmd = [solc_binary, "--standard-json", "--allow-paths", "."]

    settings = json.loads(solc_settings_json) if solc_settings_json else {}
    settings.update(
        {
            "outputSelection": {
                "*": {
                    "": ["ast"],
                    "*": [
                        "metadata",
                        "evm.bytecode",
                        "evm.deployedBytecode",
                        "evm.methodIdentifiers",
                    ],
                }
            }
        }
    )
    input_json = json.dumps(
        {
            "language": "Solidity",
            "sources": {file: {"urls": [file]}},
            "settings": settings,
        }
    )

    try:
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate(bytes(input_json, "utf8"))

    except FileNotFoundError:
        raise CompilerError(
            "Compiler not found. Make sure that solc is installed and in PATH, or set the SOLC environment variable."
        )

    out = stdout.decode("UTF-8")

    result = json.loads(out)

    for error in result.get("errors", []):
        if error["severity"] == "error":
            raise CompilerError(
                "Solc experienced a fatal error.\n\n%s" % error["formattedMessage"]
            )

    return result


def encode_calldata(func_name, arg_types, args):
    """

    :param func_name:
    :param arg_types:
    :param args:
    :return:
    """
    mid = method_id(func_name, arg_types)
    function_selector = zpad(encode_int(mid), 4)
    args = encode_abi(arg_types, args)
    return "0x" + function_selector.hex() + args.hex()


def get_random_address():
    """

    :return:
    """
    return binascii.b2a_hex(os.urandom(20)).decode("UTF-8")


def get_indexed_address(index):
    """

    :param index:
    :return:
    """
    return "0x" + (hex(index)[2:] * 40)


def solc_exists(version):
    """

    :param version:
    :return:
    """

    default_binary = "/usr/bin/solc"
    if sys.version_info[1] >= 6:
        if platform.system() == "Darwin":
            solcx.import_installed_solc()
        solcx.install_solc("v" + version)
        solcx.set_solc_version("v" + version)
        solc_binary = solcx.install.get_executable()
        return solc_binary
    elif Version("0.4.2") <= Version(version) <= Version("0.4.25"):
        if not solc.main.is_solc_available():
            solc.install_solc("v" + version)
            solc_binary = solc.install.get_executable_path("v" + version)
            return solc_binary
        else:
            solc_binaries = [
                os.path.join(
                    os.environ.get("HOME", str(Path.home())),
                    ".py-solc/solc-v" + version,
                    "bin/solc",
                )  # py-solc setup
            ]
            for solc_path in solc_binaries:
                if os.path.exists(solc_path):
                    return solc_path
    elif os.path.exists(default_binary):
        return default_binary

    else:
        return None

def _init_solc_binary(version: str) -> str:
    """
    Only proper versions are supported. No nightlies, commits etc (such as available in remix).
    :param version: Version of the solc binary required
    :return: The solc binary of the corresponding version
    """

    if not version:
        return os.environ.get("SOLC") or "solc"

    # tried converting input to semver, seemed not necessary so just slicing for now
    main_version = solc.get_solc_version_string()

    # In case instead of just the version number, --solv v0.x.x is used

    if version.startswith("v"):
        version = version[1:]

    main_version_number = re.match(r"\d+.\d+.\d+", main_version)
    if main_version is None:
        raise CriticalError(
            "Could not extract solc version from string {}".format(main_version)
        )
    if version == main_version_number:
        log.info("Given version matches installed version")
        solc_binary = os.environ.get("SOLC") or "solc"
    else:
        solc_binary = util.solc_exists(version)
        if solc_binary is None:
            if sys.version_info[1] >= 6:
                raise CriticalError(
                    "The version of solc that is needed cannot be installed automatically"
                )
            elif sys.version_info[1] == 5:
                raise CriticalError(
                    "Py-Solc doesn't support 0.5.*+. You can switch to python 3.6 which uses solcx."
                )
            else:
                raise CriticalError(
                    "There was an error when trying to install the specified solc version"
                )
        else:
            log.info("Setting the compiler to %s", solc_binary)

    return solc_binary
