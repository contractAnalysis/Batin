from batin.mapper.soliditycontract import SolidityContract

class Mapper():
    def __init__(self, solidity_file:str, contract_name:str):
        self.solidty_file=solidity_file
        self.contract_name=contract_name
        self.solidityContract=SolidityContract(self.solidty_file,self.contract_name)
        self.instruction_list=self.solidityContract.disassembly.instruction_list
        self.mappings=self.solidityContract.mappings
        self.byteAddress_2_lineNumber={}


    def byteAddress_to_lineNumber(self):
        print(f'mapping from the byte addresses of the contract creation code to the line numbers of the source code')

        for index, instruction in enumerate(self.instruction_list):

            if index >= len(self.mappings): break
            file_index = self.mappings[index].solidity_file_idx
            if file_index >= 0:
                solidity_file = self.solidityContract.solc_indices[file_index]
                filename = solidity_file.filename
                offset = self.mappings[index].offset
                length = self.mappings[index].length
                code = solidity_file.data.encode("utf-8")[offset: offset + length].decode(
                    "utf-8", errors="ignore"
                )
                address=instruction['address']
                lineno = self.mappings[index].lineno
                self.byteAddress_2_lineNumber[address] =lineno
                print(f'byte address: {address}')
                # print(f'instruciton:{instruction}')
                # print(f'filename:{filename}')
                print(f'line no: {lineno}')
                # print(f'code:{code}')
                # print(f'solc_mapping:{self.mappings[index].solc_mapping}')

        return str(self.byteAddress_2_lineNumber)

    def get_offset_of_runtime_code(self):
        constructor_mapping=self.solidityContract.constructor_mappings
        creation_instruction_list=self.solidityContract.creation_disassembly.instruction_list
        for index in range(len(constructor_mapping), len(constructor_mapping)+10):
            instruction=creation_instruction_list[index]
            if instruction['opcode']==str('PUSH1') and \
                (instruction['argument'] == str('0x80') or
                instruction['argument'] == str('0x60')):

                next_instruction=creation_instruction_list[index+1]
                if next_instruction['opcode'] == str('PUSH1') and \
                    next_instruction['argument'] == str('0x40'):
                    offset=instruction['address']
                    return offset
        return -1

