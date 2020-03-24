"""CPU functionality."""

import sys


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

    def handle_LDI(self, IR, RO, value):

        self.ram_write(value, RO)
        self.pc += 3

    def handle_PRN(self, RO):
        self.pc += 2

        return self.ram[RO]

    def handle_MUL(self, IR, RO, value):

        self.ram_write(value, RO)
        self.pc += 3

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
            print("usage: cpu.py filename")
            sys.exit(1)

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

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc

        elif op == "MUL":
            result = self.reg[reg_a] * self.reg[reg_b]
            self.ram_write(reg_a, result)

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
            IR = self.ram[self.pc]

            if IR == 0b10000010:
                RO = self.ram_read(self.pc + 1)
                value = self.ram_read(self.pc + 2)

                self.ram_write(value, RO)

                self.pc += 3

            elif IR == 0b01000111:
                RO = self.ram_read(self.pc + 1)

                self.handle_PRN(RO)

            elif IR == 0b00000001:
                halt = True

            else:
                print("Unknown Instruction")
                sys.exit(1)
