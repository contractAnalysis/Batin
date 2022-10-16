#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""batin.py: Bug hunting on the Ethereum blockchain

   http://www.github.com/ConsenSys/mythril
"""

import argparse
import json
import logging
import os
import sys

import coloredlogs
import traceback


from argparse import ArgumentParser, Namespace, RawTextHelpFormatter

from batin.exceptions import (
    CriticalError,
)

from batin.__version__ import __version__ as VERSION
from batin.mapper.mapper import Mapper

ANALYZE_LIST = ("analyze", "a")
DISASSEMBLE_LIST = ("disassemble", "d")


log = logging.getLogger(__name__)

COMMAND_LIST = (
    ANALYZE_LIST
    + DISASSEMBLE_LIST
    + (
        "version",
        "help",
    )
)


def exit_with_error(format_, message):
    """
    Exits with error
    :param format_: The format of the message
    :param message: message
    """
    if format_ == "text" or format_ == "markdown":
        log.error(message)
    elif format_ == "json":
        result = {"success": False, "error": str(message), "issues": []}
        print(json.dumps(result))
    else:
        result = [
            {
                "issues": [],
                "sourceType": "",
                "sourceFormat": "",
                "sourceList": [],
                "meta": {"logs": [{"level": "error", "hidden": True, "msg": message}]},
            }
        ]
        print(json.dumps(result))
    sys.exit()


def get_output_parser() -> ArgumentParser:
    """
    Get parser which handles output
    :return: Parser which handles output
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "-o",
        "--outform",
        choices=["text", "markdown", "json", "jsonv2"],
        default="text",
        help="report output format",
        metavar="<text/markdown/json/jsonv2>",
    )

    return parser

def get_utilities_parser() -> ArgumentParser:
    """
    Get parser which handles utilities flags
    :return: Parser which handles utility flags
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--solc-json",
        help="Json for the optional 'settings' parameter of solc's standard-json input",
    )
    parser.add_argument(
        "--solv",
        help="specify mapper compiler version. If not present, will try to install it (Experimental)",
        metavar="SOLV",
    )
    return parser

def main() -> None:
    """The main CLI interface entry point."""

    output_parser = get_output_parser()
    utilities_parser = get_utilities_parser()
    parser = argparse.ArgumentParser(
        description="Security analysis of Ethereum smart contracts"
    )

    parser.add_argument(
        "-v", type=int, help="log level (0-5)", metavar="LOG_LEVEL", default=2
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")
    analyzer_parser = subparsers.add_parser(
        ANALYZE_LIST[0],
        help="Triggers the analysis of the smart contract",
        parents=[
            output_parser,
            utilities_parser,
        ],
        aliases=ANALYZE_LIST[1:],
        formatter_class=RawTextHelpFormatter,
    )

    create_analyzer_parser(analyzer_parser)

    disassemble_parser = subparsers.add_parser(
        DISASSEMBLE_LIST[0],
        help="Disassembles the smart contract",
        aliases=DISASSEMBLE_LIST[1:],
        parents=[
            utilities_parser,
        ],
        formatter_class=RawTextHelpFormatter,
    )

    create_disassemble_parser(disassemble_parser)


    subparsers.add_parser(
        "version", parents=[output_parser], help="Outputs the version"
    )

    subparsers.add_parser("help", add_help=False)

    # Get config values
    args = parser.parse_args()
    parse_args_and_execute(parser=parser, args=args)


def create_disassemble_parser(parser: ArgumentParser):
    """
    Modify parser to handle disassembly
    :param parser:
    :return:
    """
    # Using nargs=* would the implementation below for getting code for both disassemble and analyze
    parser.add_argument(
        "solidity_files",
        nargs="*",
        help="Inputs file name and contract name. Currently supports a single contract\n"
        "usage: file1.sol:OptionalContractName",
    )


def create_analyzer_parser(analyzer_parser: ArgumentParser):
    """
    Modify parser to handle analyze command
    :param analyzer_parser:
    :return:
    """
    analyzer_parser.add_argument(
        "solidity_files",
        nargs="*",
        help="Inputs file name and contract name. \n"
        "usage: file1.sol:OptionalContractName file2.sol file3.sol:OptionalContractName",
    )
    commands = analyzer_parser.add_argument_group("commands")

    commands.add_argument("-g", "--graph", help="generate a control flow graph")

    options = analyzer_parser.add_argument_group("options")
    options.add_argument(
        "--runtime-code-offset",
        type=int,
        default=1,
        help="1: show the offset of the runtime code within the creation code; others: no",
    )



def validate_args(args: Namespace):
    """
    Validate cli args
    :param args:
    :return:
    """
    if args.__dict__.get("v", False):
        if 0 <= args.v < 6:
            log_levels = [
                logging.NOTSET,
                logging.CRITICAL,
                logging.ERROR,
                logging.WARNING,
                logging.INFO,
                logging.DEBUG,
            ]
            coloredlogs.install(
                fmt="%(name)s [%(levelname)s]: %(message)s", level=log_levels[args.v]
            )
            logging.getLogger("batin").setLevel(log_levels[args.v])
        else:
            exit_with_error(
                args.outform, "Invalid -v value, you can find valid values in usage"
            )
    if args.command in DISASSEMBLE_LIST and len(args.solidity_files) > 1:
        exit_with_error("text", "Only a single arg is supported for using disassemble")

    if args.command in ANALYZE_LIST:
        pass


def execute_command(
    parser: ArgumentParser,
    args: Namespace,
):
    """
    Execute command
    :param disassembler:
    :param address:
    :param parser:
    :param args:
    :return:
    """

    if args.command == "read-storage":
        print("read-storage")

    elif args.command in ANALYZE_LIST:
        if len(args.solidity_files)==1:
            items=str(args.solidity_files[0]).split(':')
            solidity_file=items[0]
            contract_name=items[1]
            mapper=Mapper(solidity_file,contract_name)
            re=mapper.byteAddress_to_lineNumber()

            if args.runtime_code_offset==1:
                # offset=mapper.get_offset_of_runtime_code()
                # print(f'#@runtime_code_offset:{offset}')
                ...

            # if args.outform == "text":
            #     output_file_path=solidity_file+"_"+contract_name+"_byteAddress_to_sourceLine.txt"
            #     with open(output_file_path, 'w') as f:
            #         f.write(re)
            #     f.close()


    else:
        parser.print_help()




def parse_args_and_execute(parser: ArgumentParser, args: Namespace) -> None:
    """
    Parses the arguments
    :param parser: The parser
    :param args: The args
    """

    if args.command not in COMMAND_LIST or args.command is None:
        parser.print_help()
        sys.exit()

    if args.command == "version":
        if args.outform == "json":
            print(json.dumps({"version_str": VERSION}))
        else:
            print("Mythril version {}".format(VERSION))
        sys.exit()

    if args.command == "list-detectors":
        sys.exit()

    if args.command == "help":
        parser.print_help()
        sys.exit()

    # Parse cmdline args
    validate_args(args)
    try:
        execute_command(
            parser=parser, args=args
        )


    except CriticalError as ce:
        exit_with_error(args.__dict__.get("outform", "text"), str(ce))
    except Exception:
        exit_with_error(args.__dict__.get("outform", "text"), traceback.format_exc())


if __name__ == "__main__":
    main()
