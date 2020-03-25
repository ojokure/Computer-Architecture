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
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.branchtable = {}
        self.branchtable[LDI] = self.handle_LDI
        self.branchtable[PRN] = self.handle_PRN
        self.branchtable[MUL] = self.handle_MUL
        self.branchtable[HLT] = self.handle_HLT
        self.branchtable[POP] = self.handle_POP
        self.branchtable[PUSH] = self.handle_PUSH
        self.halt = False

    def ram_write(self, value, MAR):
        self.ram[MAR] = value

    def ram_read(self, MAR):
        MDR = self.ram[MAR]
        return MDR

    def handle_LDI(self, operand_1, operand_2):
        self.ram_write(operand_2, operand_1)
        # self.reg[operand_1] = operand_2

    def handle_PRN(self, operand_1):
        print(self.reg[operand_1])

    def handle_PUSH(self, operand_1):
        self.reg[SP] -= 1

        value = self.ram[operand_1]
        self.ram[self.reg[SP]] = value

    def handle_POP(self, operand_1):
        value = self.ram[self.reg[SP]]
        self.reg[operand_1] = value

        self.reg[SP] += 1

    def handle_MUL(self, operand_1, operand_2):
        self.alu("MUL", operand_1, operand_2)

    def handle_HLT(self):
        self.halt = True
        sys.exit(1)

    def load(self):
        """Load a program into memory."""

        if len(sys.argv) != 2:
            print("usage: ls8.py filename")
            sys.exit(1)

        try:
            prog_name = sys.argv[1]

            address = 0

            with open(prog_name) as program:

                for line in program:

                    line_split = line.split("#")
                    op = line_split[0].strip()

                    if op == "":
                        continue

                    IR = int(op, 2)

                    self.ram[address] = IR
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

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
            IR = self.ram[self.pc]
            operand_1 = self.ram_read(self.pc + 1)
            operand_count = IR >> 6  # AA(Instruction Layout)
            is_ALU_op = IR >> 5  # B(Instruction Layout)

            if is_ALU_op == 1:
                operand_2 = self.ram_read(self.pc + 2)
                if IR == MUL:
                    # if self.IR << 4 == 0b00100000:  # (10100010 MUL)
                    self.alu("MUL", operand_1, operand_2)

            elif operand_count == 1:
                self.branchtable[IR](operand_1)

            elif operand_count == 2:
                operand_2 = self.ram_read(self.pc + 2)
                self.branchtable[IR](operand_1, operand_2)

            elif IR == 0 or None:
                print(f"exited at {self.pc}")
                sys.exit(1)

            self.pc += operand_count + 1
