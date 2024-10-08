import sys
import re

class HackAssembler:
    def __init__(self, input_file):
        self.parser = AssemblerParser(input_file)
        self.symbol_table = SymbolRegistry()

    def execute(self):
        self.first_pass()
        self.parser.reset()
        self.second_pass()

    def first_pass(self):
        instruction_count = 0
        while self.parser.has_more_lines():
            self.parser.next_command()

            if self.parser.current_command_type == 'skip':
                continue
            elif self.parser.current_command_type == 'label':
                self.symbol_table.add(self.parser.get_symbol(), instruction_count)
            else:
                instruction_count += 1

    def second_pass(self):
        output_filename = self.parser.input_file.name.replace('.asm', '.hack')
        with open(output_filename, 'w') as hack_file:
            char_matcher = re.compile(r'[a-zA-Z]+')

            while self.parser.has_more_lines():
                self.parser.next_command()
                if self.parser.current_command_type == 'address':
                    symbol = self.parser.get_symbol()
                    if char_matcher.match(symbol):
                        address = self.symbol_table.get_or_allocate(symbol)
                    else:
                        address = int(symbol)
                    hack_file.write(HackDecoder.to_binary_string(address) + '\n')
                elif self.parser.current_command_type == 'computation':
                    machine_code = self.build_computation_instruction()
                    hack_file.write(machine_code + '\n')

    def build_computation_instruction(self):
        init_bits = HackDecoder.C_COMMAND_PREFIX
        comp_bits = HackDecoder.COMP_BITS[self.parser.get_comp()]
        dest_bits = HackDecoder.DEST_BITS[self.parser.get_dest()]
        jump_bits = HackDecoder.JUMP_BITS[self.parser.get_jump()]
        return init_bits + comp_bits + dest_bits + jump_bits


class HackDecoder:
    C_COMMAND_PREFIX = '111'

    DEST_BITS = {
        None : '000',
        'M'  : '001',
        'D'  : '010',
        'MD' : '011',
        'A'  : '100',
        'AM' : '101',
        'AD' : '110',
        'AMD': '111'
    }

    COMP_BITS = {
        None  : '',
        '0'   : '0101010',
        '1'   : '0111111',
        '-1'  : '0111010',
        'D'   : '0001100',
        'A'   : '0110000',
        'M'   : '1110000',
        '!D'  : '0001101',
        '!A'  : '0110001',
        '!M'  : '1110001',
        '-D'  : '0001111',
        '-A'  : '0110011',
        '-M'  : '1110011',
        'D+1' : '0011111',
        'A+1' : '0110111',
        'M+1' : '1110111',
        'D-1' : '0001110',
        'A-1' : '0110010',
        'M-1' : '1110010',
        'D+A' : '0000010',
        'D+M' : '1000010',
        'D-A' : '0010011',
        'D-M' : '1010011',
        'A-D' : '0000111',
        'M-D' : '1000111',
        'D&A' : '0000000',
        'D&M' : '1000000',
        'D|A' : '0010101',
        'D|M' : '1010101'
    }

    JUMP_BITS = {
        None : '000',
        'JGT': '001',
        'JEQ': '010',
        'JGE': '011',
        'JLT': '100',
        'JNE': '101',
        'JLE': '110',
        'JMP': '111'
    }

    @staticmethod
    def to_binary_string(value):
        return f'{value:016b}'


class SymbolRegistry:
    PREDEFINED_SYMBOLS = {
        'SP'  : 0, 'LCL' : 1, 'ARG' : 2, 'THIS': 3, 'THAT': 4,
        'R0'  : 0, 'R1'  : 1, 'R2'  : 2, 'R3'  : 3, 'R4'  : 4,
        'R5'  : 5, 'R6'  : 6, 'R7'  : 7, 'R8'  : 8, 'R9'  : 9,
        'R10' : 10, 'R11' : 11, 'R12' : 12, 'R13' : 13, 'R14' : 14, 'R15' : 15,
        'SCREEN': 16384, 'KBD'   : 24576
    }

    def __init__(self):
        self.symbol_table = dict(self.PREDEFINED_SYMBOLS)
        self.next_free_address = 16

    def add(self, symbol, address):
        self.symbol_table[symbol] = address

    def contains(self, symbol):
        return symbol in self.symbol_table

    def get_address(self, symbol):
        return self.symbol_table[symbol]

    def get_or_allocate(self, symbol):
        if not self.contains(symbol):
            self.add(symbol, self.next_free_address)
            self.next_free_address += 1
        return self.get_address(symbol)


class AssemblerParser:
    # Procesa línea por línea el archivo de entrada y reporta el tipo de instrucción actual.
    DEST_DELIMITER = '='
    JUMP_DELIMITER = ';'

    def __init__(self, input_file):
        self.input_file = open(input_file, 'r')
        self.current_command = None
        self.has_more_lines_flag = True

    def reset(self):
        self.input_file.seek(0)
        self.current_command = None
        self.has_more_lines_flag = True

    def has_more_lines(self):
        return self.has_more_lines_flag

    def next_command(self):
        self.current_command = self._get_next_clean_line()
        if not self.current_command:
            self.has_more_lines_flag = False
        self._set_command_type()

    def get_dest(self):
        return self.current_command.split(self.DEST_DELIMITER)[0] if self.DEST_DELIMITER in self.current_command else None

    def get_comp(self):
        if self.DEST_DELIMITER in self.current_command:
            return self.current_command.split(self.DEST_DELIMITER)[1]
        elif self.JUMP_DELIMITER in self.current_command:
            return self.current_command.split(self.JUMP_DELIMITER)[0]

    def get_jump(self):
        return self.current_command.split(self.JUMP_DELIMITER)[1] if self.JUMP_DELIMITER in self.current_command else None

    def get_symbol(self):
        return ''.join(c for c in self.current_command if c not in '()@/')

    def _get_next_clean_line(self):
        while True:
            line = self.input_file.readline()
            if not line:
                return None
            clean_line = self._clean(line)
            if clean_line:
                return clean_line

    def _clean(self, line):
        return line.split('//')[0].strip()

    def _set_command_type(self):
        if not self.current_command:
            self.current_command_type = 'skip'
        elif self.current_command.startswith('@'):
            self.current_command_type = 'address'
        elif self.current_command.startswith('('):
            self.current_command_type = 'label'
        else:
            self.current_command_type = 'computation'


if __name__ == '__main__':
    asm_file = sys.argv[1]
    assembler = HackAssembler(asm_file)
    assembler.execute()
