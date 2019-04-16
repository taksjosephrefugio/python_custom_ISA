#####################################################################################
# @Authors Evan Gruzlewski                                                          #
#          Tak's Joseph Refugio                                                     #
#          Kusai Burhan                                                             #
# University of Illinois at Chicago                                                 #
# This program is a custom assembly simulator which runs assembly given as binary   #
# Input: Custom assembly as binary, adhering to the following guidelines            #
#        as described in the report write-ups.                                      #
# Last Worked by: Evan, 04/04/2019, 4:30PM                                          #
# Version: Full working as intended                                                 #
#####################################################################################

import os
from time import sleep

# User-defined definitions
filename = "input"    # Name of file to run - do not include '.txt'
output_file = True              # Set to true to create a file of the output
step = False                    # Set to true to run step-by-step
delay = 0.8                     # If step == True, sets the delay between steps
max_regs = 4                    # Number of registers to allocate (not including PC)
max_mem = 48                    # Maximum memory to allocate

# Static definitions
register = []                   # List containing register values
memory = {}                     # Dictionary containing memory locations and their associated stored values
instruction = []                # List containing the binary read in from the file
instruction_count = [0]         # Running instruction count
instruction_string = []         # List containing assembly conversion for each instruction

# This function takes in a binary string and returns the corresponding assembly string
def read_instr_strings(binary_string):
    op = binary_string[7]
    rd = binary_string[0:2]
    string_result = "Error"

    if op == '0': # R-TYPE
        rs = binary_string[2:4]
        func = binary_string[4:7]
        if func == "000":
            string_result = "add " + "r" + str(int(rd,2)) + " , r" + str(int(rs,2))
        elif func == "001":
            string_result = "dec " + "r" + str(int(rd,2)) + " , r" + str(int(rs,2))
        elif func == "010":
            string_result = "and " + "r" + str(int(rd,2)) + " , r" + str(int(rs,2))
        elif func == "011":
            string_result = "or " + "r" + str(int(rd,2)) + " , r" + str(int(rs,2))
        elif func == "100":
            string_result = "sdm " + "r" + str(int(rd,2)) + " , r" + str(int(rs,2))
        elif func == "101":
            string_result = "srl " + "r" + str(int(rd,2)) + " , r" + str(int(rs,2))
        elif func == "110":
            string_result = "sb " + "r" + str(int(rd,2)) + " , M[r" + str(int(rs,2)) + "]"
        elif func == "111":
            string_result = "lb " + "r" + str(int(rd,2)) + " , M[r" + str(int(rs,2)) + "]"
    elif op == '1': # I-TYPE
        imm = binary_string[2:6]
        func = binary_string[6]
        if func == '0':
            string_result = "addi " + "r" + str(int(rd,2)) + ", " + str(int(imm,2))
        if func == '1':
            string_result = "bnez " + "r" + str(int(rd,2)) + ", " + str(int(imm,2))
    return string_result

# Initializes registers and memory to 0
def init():
    i = 0
    while i <= max_regs:
        register.append(0)
        i += 1
    mem = 0
    while mem <= max_mem:
        memory[mem] = 0
        mem += 1

# Increases instruction count and pc by 1
def bump():
    instruction_count[0] += 1
    register[max_regs] += 1

# Clears the console, checks for system OS
def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

# Prints all non-zero registers and memory per step, with added clearing
def print_step():
    print("Step " + str(instruction_count))
    print("Instruction = " + instruction_string[register[max_regs]-1])
    i = 0
    for r in register:
        if i < max_regs and r != 0:
            print("R" + str(i) + " = " + str(r))
        i += 1
    pc = register[max_regs]
    print("PC = " + str(pc))
    for m in memory:
        if memory.get(m) != 0:
            print(str(hex(m)) + " = " + str(memory.get(m)))

# Reads the file as defined by filename above.
def read_file():
    input_file = open(filename + ".txt", "r")
    for line in input_file:
        if line.startswith("#") or line == "\n":
            continue
        line = line.replace("0x", "").replace("\n", "")
        line = line[0:8]
        instruction.append(line)
        instruction_string.append(read_instr_strings(line))
    input_file.close()

# This function will compute the input binary
#   Returns False if the binary is either invalid or unsupported, true otherwise
def compute(binary):
    ret = True
    op = binary[7]
    try:
        if op == "0":
            rd = int(binary[0:2], 2)
            rs = int(binary[2:4], 2)
            func = binary[4:7]
            if func == "000":   #add
                register[rd] += register[rs]
            elif func == "001": #dec
                register[rd] = register[rs] - 1
            elif func == "010": #and
                if rd == rs:
                    register[rd] = register[rs] & 0xF
                else:
                    register[rd] = register[rs] & 0x1
            elif func == "011": #xor
                register[rd] = register[rd] ^ register[rs]
            elif func == "100": #sdm
                square = register[rs] * register[rs]
                bin_square = format(square, "016b")
                right = int(bin_square[0:8], 2) & 0xF0
                left = int(bin_square[8:16]) & 0x0F
                register[rd] = right | left
            elif func == "101": #srl
                    register[rd] = register[rd] >> rs + 1
            elif func == "110": #sb
                memory[register[rs]] = register[rd]
            elif func == "111": #lb
                register[rd] = memory[register[rs]]
            else:
                ret = False
        elif op == "1":
            func = binary[6]
            rd = int(binary[0:2], 2)
            imm = int(binary[2:6], 2)
            if func == "0":     #addi
                register[rd] += imm
            elif func == "1":   #bnez
                imm = int(binary[2:6],2) * -1
                if register[rd] != 0:
                    register[max_regs] += imm-1
            else:
                ret = False
    except KeyError:
        ret = False
    return ret

# Sends the binary instructions to compute and provides error checking for debugging purposes
def run():
    size = len(instruction)-1
    while int(register[max_regs]) <= size:
        if not compute(instruction[register[max_regs]]):
            print("[ERROR] - The provided file is either invalid or unsupported")
            print("[ERROR] - The program failed at instruction = " + instruction[register[max_regs]])
            print("[ERROR] - Instruction = " + instruction_string[register[max_regs]] + "\tPC = " + str(register[max_regs]))
            exit(-1)
        else:
            bump()

        if step:
            print_step()
            sleep(delay)
            cls()

# This function displays the contents of: (1) Register Array; (2) Memory Array
# (3) Hamming Weights Array; (4) Seed Average; (5) Hamming Weight Average
def print_results():

    print("######################")
    print("#     END RESULTS    #")
    print("######################")
    print("\nInstruction count = " + str(instruction_count[0]) + "\n")

    i = 0
    while i < max_regs:
        print("R" + str(i) + " = " + str(register[i]))
        i += 1
    print("PC = " + str(register[max_regs]) + "\n")

    i = 8
    print("Generated numbers from s0 = " + str(memory[i]) + ":")
    while i <= 11:
        print("M[" + str(i) + "] = " + str(memory[i]) + "\t" +
              "M[" + str(i+4) + "] = " + str(memory[i+4]) + "\t" +
              "M[" + str(i+8) + "] = " + str(memory[i+8]) + "\t" +
              "M[" + str(i+12) + "] = " + str(memory[i+12]))
        i += 1
    print("\nAverage of generated numbers:\nM[24] = " + str(memory[24]))
    print("\nHamming weights of generated numbers:")
    i = 32
    while i <= 35:
        print("M[" + str(i) + "] = " + str(memory[i]) + "\t" +
              "M[" + str(i+4) + "] = " + str(memory[i+4]) + "\t" +
              "M[" + str(i+8) + "] = " + str(memory[i+8]) + "\t" +
              "M[" + str(i+12) + "] = " + str(memory[i+12]))
        i += 1
    print("\nAverage Hamming weight:\nM[48] = " + str(memory[48]))

# Creates a file of the output of the simulator
def write_results():
    if output_file:
        name = filename[0:12] + "sim_out_" + filename[12:]
        out = open(name + ".txt", "w")

        out.write("Instruction count = " + str(instruction_count[0]) + "\n\n")

        i = 0
        while i < max_regs:
            out.write("R" + str(i) + " = " + str(register[i]) + "\n")
            i += 1
        out.write("PC = " + str(register[max_regs]) + "\n\n")

        i = 8
        out.write("Generated numbers from s0 = " + str(memory[i]) + ":\n")
        while i <= 23:
            out.write("M[" + str(i) + "] = " + str(memory[i]) + "\n")
            i += 1
        out.write("\nAverage of generated numbers:\nM[24] = " + str(memory[24]) + "\n")
        out.write("\nHamming weights of generated numbers:\n")
        i = 32
        while i <= 47:
            out.write("M[" + str(i) + "] = " + str(memory[i]) + "\n")
            i += 1
        out.write("\nAverage Hamming weight:\nM[48] = " + str(memory[48]) + "\n")
        out.close()

if __name__ == "__main__":
    init()
    read_file()
    run()
    print_results()
    write_results()
