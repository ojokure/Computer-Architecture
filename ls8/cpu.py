"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
POP = 0b01000110
PUSH = 0b01000101
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
ST = 0b10000100
PRA = 0b01001000
IRET = 0b00010011
LD = 0b10000011
CMP = 0b10100111
JEQ = 0b01010101
JGE = 0b01011010
JGT = 0b01010111
JLE = 0b01011001
JLT = 0b01011000
JMP = 0b01010100
JNE = 0b01010110
SP = 7


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.branchtable = {}

        # IR Handlers
        self.branchtable[LDI] = self.handle_LDI
        self.branchtable[PRN] = self.handle_PRN
        self.branchtable[MUL] = self.handle_MUL
        self.branchtable[ADD] = self.handle_ADD
        self.branchtable[HLT] = self.handle_HLT
        self.branchtable[POP] = self.handle_POP
        self.branchtable[PUSH] = self.handle_PUSH
        self.branchtable[CALL] = self.handle_CALL
        self.branchtable[CMP] = self.handle_CMP
        self.branchtable[JMP] = self.handle_JMP
        self.branchtable[JEQ] = self.handle_JEQ
        self.branchtable[JNE] = self.handle_JNE
        self.branchtable[JGE] = self.handle_JGE
        self.branchtable[JGT] = self.handle_JGT
        self.branchtable[JLE] = self.handle_JLE
        self.branchtable[JLT] = self.handle_JLT
        self.branchtable[PRA] = self.handle_PRA
        self.branchtable[LD] = self.handle_LD
        # self.branchtable[IRET] = self.handle_IRET

        # Internal Registers
        self.halt = False
        self.pc = 0
        self.IR = None
        self.MAR = None
        self.MDR = None

        # FLAGS
        # self.FL
        self.E = 0
        self.L = 0
        self.G = 0

    def ram_write(self, MAR, value):
        self.ram[MAR] = value

    def ram_read(self, MAR):
        MDR = self.ram[MAR]
        return MDR

    def handle_LDI(self, operand_1, operand_2):
        self.ram_write(operand_2, operand_1)
        self.reg[operand_1] = operand_2

    def handle_LD(self, operand_1, operand_2):
        self.ram[operand_1] = self.ram[self.reg[operand_2]]

    def handle_PRN(self, operand_1):
        print(chr(self.reg[operand_1]))

    def handle_PRA(self, operand_1):
        print(self.reg[operand_1])

    # STACK OPERATIONS
    def handle_PUSH(self, operand_1):
        self.reg[SP] -= 1
        self.ram_write(self.reg[SP], self.reg[operand_1])

    def handle_POP(self, operand_1):
        self.handle_LDI(operand_1, self.ram[self.reg[SP]])
        self.reg[SP] += 1

    # SUBROUTINE OPERATIONS
    def handle_CALL(self, operand_1):
        self.reg[SP] -= 1
        self.ram_write(self.reg[SP], self.pc + 2)
        self.pc = self.reg[operand_1]

    def handle_RET(self):
        self.pc = self.ram[self.reg[SP]]
        self.reg[SP] += 1

    # JUMP OPERATIONS
    def handle_JMP(self, operand_1):
        self.pc = self.reg[operand_1]

    def handle_JEQ(self, operand_1):
        if self.E == 1:
            self.handle_JMP(operand_1)

    def handle_JNE(self, operand_1):
        if self.E == 0:
            self.handle_JMP(operand_1)

    def handle_JGE(self, operand_1):
        if self.G == 1 or self.E == 1:
            self.handle_JMP(operand_1)

    def handle_JGT(self, operand_1):
        if self.G == 1:
            self.handle_JMP(operand_1)

    def handle_JLE(self, operand_1):
        if self.L == 1 or self.E == 1:
            self.handle_JMP(operand_1)

    def handle_JLT(self, operand_1):
        if self.L == 1:
            self.handle_JMP(operand_1)

    # ALU OPERATIONS
    def handle_CMP(self, operand_1, operand_2):
        self.alu("CMP", operand_1, operand_2)

    def handle_MUL(self, operand_1, operand_2):
        self.alu("MUL", operand_1, operand_2)

    def handle_AND(self, operand_1, operand_2):
        self.alu("AND", operand_1, operand_2)

    def handle_ADD(self, operand_1, operand_2):
        self.alu("ADD", operand_1, operand_2)

    def handle_OR(self, operand_1, operand_2):
        self.alu("OR", operand_1, operand_2)

    def handle_XOR(self, operand_1, operand_2):
        self.alu("XOR", operand_1, operand_2)

    def handle_NOT(self, operand_1, operand_2):
        self.alu("NOT", operand_1, operand_2)

    def handle_SHL(self, operand_1, operand_2):
        self.alu("SHL", operand_1, operand_2)

    def handle_SHR(self, operand_1, operand_2):
        self.alu("SHR", operand_1, operand_2)

    def handle_MOD(self, operand_1, operand_2):
        self.alu("MOD", operand_1, operand_2)

    def handle_HLT(self):
        self.halt = True
        sys.exit(1)

    def load(self):
        """Load a program into memory."""

        if len(sys.argv) != 2:
            print("usage: ls8.py filename", file=sys.stderr)
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

        elif op == "AND":
            value_a = self.reg[reg_a]
            value_b = self.reg[reg_b]
            result = value_a & value_b

            self.reg[reg_a] = result

        elif op == "OR":
            value_a = self.reg[reg_a]
            value_b = self.reg[reg_b]
            result = value_a | value_b

            self.reg[reg_a] = result

        elif op == "XOR":
            value_a = self.reg[reg_a]
            value_b = self.reg[reg_b]
            result = value_a ^ value_b

            self.reg[reg_a] = result

        elif op == "NOT":
            value = self.reg[reg_a]
            result = ~ value

            self.reg[reg_a] = result

        elif op == "SHL":
            value_a = self.reg[reg_a]
            value_b = self.reg[reg_b]
            result = value_a << value_b

            self.reg[reg_a] = result

        elif op == "SHR":
            value_a = self.reg[reg_a]
            value_b = self.reg[reg_b]
            result = value_a >> value_b

            self.reg[reg_a] = result

        elif op == "MOD":
            value_a = self.reg[reg_a]
            value_b = self.reg[reg_b]

            if value_b != 0:
                result = value_a % value_b
                self.reg[reg_a] = result

            else:
                print("you cannot divide by 0")
                self.handle_HLT()

        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.E = 1

            elif self.reg[reg_a] < self.reg[reg_b]:
                self.L = 1

            else:
                self.G = 1

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
            self.IR = self.ram_read(self.pc)
            operand_1 = self.ram_read(self.pc + 1)
            operand_2 = self.ram_read(self.pc + 2)
            operand_count = self.IR >> 6  # AA(Instruction Layout)
            is_ALU_op = self.IR >> 5  # B(Instruction Layout)
            is_SET_PC = self.IR >> 4 & 0b00000001  # C(Instruction Layout)

            if is_ALU_op == 1:
                if self.IR == MUL:
                    # if self.IR << 4 == 0b00100000:  # (10100010 MUL)
                    self.alu("MUL", operand_1, operand_2)
                if self.IR == ADD:
                    self.alu("ADD", operand_1, operand_2)

            elif operand_count == 2:
                self.branchtable[self.IR](operand_1, operand_2)

            elif operand_count == 1:
                self.branchtable[self.IR](operand_1)

            elif self.IR == 0:
                self.branchtable[self.IR]()

            else:  # self.IR == 0 or None:
                print(f"exited at PC: {self.pc}, Instruction: {self.IR}")
                sys.exit(1)

            if is_SET_PC == 0:
                self.pc += operand_count + 1
