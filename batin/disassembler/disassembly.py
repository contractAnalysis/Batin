"""This module contains the class used to represent disassembly code."""
from batin import util
from batin.disassembler import asm

from typing import Dict, List, Tuple

class Disassembly(object):
    """Disassembly class.

    Stores bytecode, and its disassembly.
    Additionally it will gather the following information on the existing functions in the disassembled code:
    - function hashes
    - function name to entry point mapping
    - function entry point to function name mapping
    """

    def __init__(self, code: str, enable_online_lookup: bool = False) -> None:
        """

        :param code:
        :param enable_online_lookup:
        """
        self.bytecode = code
        self.instruction_list = asm.disassemble(util.safe_decode(code))

        self.func_hashes = []  # type: List[str]
        self.function_name_to_address = {}  # type: Dict[str, int]
        self.address_to_function_name = {}  # type: Dict[int, str]
        self.enable_online_lookup = enable_online_lookup



    def get_easm(self):
        """

        :return:
        """
        return asm.instruction_list_to_easm(self.instruction_list)


