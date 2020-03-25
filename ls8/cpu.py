"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
HLT = 0b00000001
POP = 0b01000110
PUSH = 0b01000101
SP = 7


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
        print(self.ram[operand_1])
        self.pc += 2

    def handle_POP(self, operand_1):
        self.handle_LDI(operand_1, self.ram[self.reg[SP]])
        self.reg[SP] += 1

    def handle_PUSH(self, operand_1):
        self.reg[SP] -= 1
        self.ram_write(self.reg[SP], self.reg[operand_1])

    def handle_MUL(self, operand_1, operand_2):
        self.alu("MUL", operand_1, operand_2)

    def handle_HLT(self):
        self.halt = True
        sys.exit(1)

    def ram_write(self, value, MAR):
        self.ram[MAR] = value

    def ram_read(self, MAR):
        MDR = self.ram[MAR]
        return MDR

    def load(self, filename):
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
            self.pc += 3

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

        while not self.halt:
            self.IR = self.ram[self.pc]
            operand_1 = self.ram_read(self.pc + 1)
            operand_2 = self.ram_read(self.pc + 2)
            operand_count = self.IR >> 6  # AA(Instruction Layout)
            is_ALU_op = self.IR >> 5  # B(Instruction Layout)
            # is_SET_PC = self.IR >> 4 & 0b00000001  # C(Instruction Layout)

            if is_ALU_op == 1:
                if self.IR == MUL:
                    # if self.IR << 4 == 0b00100000:  # (10100010 MUL)
                    self.alu("MUL", operand_1, operand_2)

            elif operand_count == 2:
                self.branchtable[self.IR](operand_1, operand_2)

            elif operand_count == 1:
                self.branchtable[self.IR](operand_1)

            else:
                self.branchtable[self.IR]()
