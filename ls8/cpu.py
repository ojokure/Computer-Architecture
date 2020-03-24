"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
HLT = 0b00000001


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0b00000000] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.branchtable = {}
        self.branchtable[LDI] = self.handle_LDI
        self.branchtable[PRN] = self.handle_PRN
        self.branchtable[MUL] = self.handle_MUL
        self.branchtable[HLT] = self.handle_HLT
        self.halt = False
        self.IR = None

    def handle_LDI(self, operand_1, operand_2):
        self.ram_write(operand_2, operand_1)
        self.pc += 3

    def handle_PRN(self, operand_1):
        self.pc += 2
        return self.ram[operand_1]

    def handle_MUL(self, operand_1, operand_2):
        self.alu("MUL", operand_1, operand_2)

    def handle_HLT(self):
        sys.exit(1)

    def ram_write(self, value, MAR):
        self.ram[MAR] = value

    def ram_read(self, MAR):
        MDR = self.ram[MAR]
        return MDR

    def load(self):
        """Load a program into memory."""

        if len(sys.argv) != 2:
            print("usage: ls8.py filename")
            sys.exit(1)

        try:
            prog_name = sys.argv[1]

            address = 0

            with open(prog_name) as program:

                for op in program:
                    op = op.split("#")[0].strip()
                    if op == "":
                        continue
                    print(op)

                    instruction = int(op, 2)
                    self.ram[address] = instruction
                    address += 1
        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        elif op == "MUL":
            result = self.reg[reg_a] * self.reg[reg_b]
            self.ram_write(reg_a, result)
            self.pc += 3

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        halt = False

        while not halt:
            self.IR = self.ram[self.pc]
            operand_1 = self.ram_read(self.pc + 1)
            operand_2 = self.ram_read(self.pc + 2)

            if int(self.IR, 2) == LDI:
                self.handle_LDI(operand_1, operand_2)

            elif int(self.IR, 2) == PRN:
                self.handle_PRN(operand_1)

            elif int(self.IR, 2) == HLT:
                halt = True
                self.handle_HLT()

            else:
                print("Unknown Instruction")
                sys.exit(1)
