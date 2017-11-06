#!/usr/bin/python
# -*- coding: utf-8 -*-

# your code goes here

import shlex
import traceback

reg = ['B', 'C', 'D', 'E', 'H', 'L', 'M', 'A', 'SP', 'PSW']
reg_val = {reg[i]: i for i in range(len(reg))}
start_address = 0


def get_hex(start, end, steps):
    return [hex(i)[2:].zfill(2).upper() for i in range(start, end, steps)]


def gh(start, step, valid):  # b,c,d,e,h,l,m,a
    rv = [None] * len(reg)
    l = get_hex(start, start + len(valid) * step, step)
    k = 0
    for i in range(len(reg)):
        if reg[i] in valid:
            rv[i] = l[k]
            k += 1
    return rv


def ghm():
    rv = list()
    start = 64
    for i in range(len(reg) - 2):
        rv.append(get_hex(start, start + 9, 1))
        start += len(rv)
        if reg[i] == 'M':
            rv[i][i] = None
    # for i in range(len(rv)):
    #   for j in range(len(rv[0])):
    #     print(rv[i][j], ' ', end='')
    #   print()
    return rv


valid8 = ['B', 'C', 'D', 'E', 'H', 'L', 'M', 'A']
valid4s = ['B', 'D', 'H', 'SP']
valid4p = ['B', 'D', 'H', 'PSW']
valid2 = ['B', 'D']
adc = gh(136, 1, valid8)
add = gh(128, 1, valid8)
ana = gh(160, 1, valid8)
cnp = gh(184, 1, valid8)
dad = gh(9, 16, valid4s)
dcr = gh(5, 8, valid8)
dcx = gh(11, 16, valid4s)
inr = gh(4, 8, valid8)
inx = gh(3, 16, valid4s)
ldx = gh(10, 16, valid2)
lxi = gh(1, 16, valid4s)
mov = ghm()
mvi = gh(6, 8, valid8)
ora = gh(176, 1, valid8)
pop = gh(193, 16, valid4p)
psh = gh(197, 16, valid4p)
rst = gh(199, 8, valid8)
sbb = gh(152, 1, valid8)
stx = gh(2, 16, valid2)
sub = gh(144, 1, valid8)
xra = gh(168, 1, valid8)
num_itype = 3
ins = list(range(num_itype))
ins[0] = {'ADC': adc, 'ADD': add, 'ANA': ana, 'CMA': '2F', 'CMC': '3F', 'CMP': cnp, 'DAA': '27', 'DAD': dad, 'DCR': dcr,
          'DCX': dcx, 'DI': '43', 'EI': 'FB', 'HLT': '76', 'INR': inr, 'INX': inx, 'LDAX': ldx, 'MOV': mov, 'NOP': '00',
          'ORA': ora, 'PCHL': 'E9', 'POP': pop, 'PUSH': psh, 'RAL': '17', 'RAR': '1F', 'RLC': '07', 'RRC': '0F',
          'RET': 'C9', 'RC': 'D8', 'RNC': 'D0', 'RP': 'F0', 'RM': 'F8', 'RPE': 'E8', 'RPO': 'E0', 'RZ': 'C8',
          'RNZ': 'C0', 'RIM': '20', 'RST': rst, 'SBB': sbb, 'SIM': '30', 'SPHL': 'F9', 'STAX': stx, 'STC': '37',
          'SUB': sub, 'XCHG': 'EB', 'XRA': xra, 'XTHL': 'E3', }
ins[1] = {'ACI': 'CE', 'ADI': 'C6', 'ANI': 'E6', 'CPI': 'FE', 'IN': 'DB', 'OUT': 'D3', 'MVI': mvi, 'ORI': 'F6',
          'SBI': 'DE', 'SUI': 'D6', 'XRI': 'EE', }
ins[2] = {'CALL': 'CD', 'CC': 'DC', 'CNC': 'D4', 'CP': 'F4', 'CM': 'FC', 'CPE': 'EC', 'CPO': 'E4', 'CZ': 'CC',
          'CNZ': 'C4', 'JMP': 'C3', 'JC': 'DA', 'JNC': 'D2', 'JP': 'F2', 'JM': 'FA', 'JPE': 'EA', 'JPO': 'E2',
          'JZ': 'CA', 'JNZ': 'C2', 'LDA': '3A', 'LHLD': '2A', 'LXI': lxi, 'SHLD': '22', 'STA': '32', }
sym_tab = {}


class UnknownSymbolException(Exception):
    def __init__(self, word):
        Exception("Unknown symbol " + word)


class InvalidOperandException(Exception):
    def __init__(self, operand, instruction):
        Exception("Invalid operand " + operand + " for instruction " + instruction)


def get_val(word):
    try:
        # symbol
        if word in sym_tab:
            return sym_tab[word]
        # hex
        if is_hex(word[:-1]):
            return str(word[:-1])
    except:
        raise UnknownSymbolException(word)


def get_bytes(inst):
    for i in range(len(ins)):
        if inst in ins[i]:
            return i + 1
    return 0


def is_ins(word):
    return get_bytes(word) != 0


def is_lbl(word):
    return word[-1] == ':'


def is_hex(string):
    try:
        _ = int(string, 16)
        return True
    except:
        return False


def add_symbol(word, value):
    if word in reg_val or word in sym_tab or is_ins(word):
        raise Exception(word + " is already defined")
    if len(value) > 2:
        value = "{:0<4}".format(value)

    sym_tab[word] = value


def first_pass(lines):
    loc_ctr = hex(0)
    out_lines = list()
    for line in lines:
        words = shlex.split(line, posix=False)
        if words[0] == 'ORG':
            global start_address
            start_address = loc_ctr = int(get_val(words[1]))
        elif words[0] == 'END' or words[0] == 'HLT':
            # print(sym_tab, loc_ctr)
            break
        elif len(words) > 2 and words[1] == 'EQU':
            add_symbol(words[0], get_val(words[2]))
        else:
            out_lines.append("{:04d} {}".format(loc_ctr, line))
            if is_lbl(words[0]):
                lbl = words[0][:-1]
                add_symbol(lbl, str(loc_ctr))
                if len(words) > 1:
                    loc_ctr += get_bytes(words[1])
            elif is_ins(words[0]):
                loc_ctr += get_bytes(words[0])
                # else:
                #   raise Exception("Invalid symbol "+words[0]+" in line "+line)
                # print (line, sym_tab, loc_ctr)
    return out_lines


def get_opcode(words, nbyte):
    if nbyte == 1:
        v = ins[0][words[0]]
        if isinstance(v, list):
            if isinstance(v[0], list):
                if ',' not in words[1]:
                    raise InvalidOperandException(words[1], words[0])
                r1, r2 = words[1].split(',')
                try:
                    return v[reg.index(r1)][reg.index(r2)]
                except:
                    raise InvalidOperandException(words[1], words[0])
            else:
                try:
                    r1 = words[1]
                    return v[reg.index(r1)]
                except:
                    raise InvalidOperandException(words[1], words[0])
        else:
            return v
    elif nbyte == 2:
        v = ins[1][words[0]]
        if isinstance(v, list):
            if ',' not in words[1]:
                raise InvalidOperandException(words[1], words[0])
            r1, o2 = words[1].split(',')
            byte = get_val(o2)
            # print(o2, byte)
            if len(byte) != 2:
                raise InvalidOperandException(words[1], words[0])
            return "{} {:0<2}".format(v[reg.index(r1)], byte)
    else:
        v = ins[2][words[0]]
        if isinstance(v, list):
            if ',' not in words[1]:
                raise InvalidOperandException(words[1], words[0])
            r1, o2 = words[1].split(',')
            byte = get_val(o2)
            # print(o2, byte)
            if len(byte) != 4:
                raise InvalidOperandException(words[1], words[0])
            swapped = ""
            swapped += byte[2:]
            swapped += byte[:2]
            return "{} {:0<4}".format(v[reg.index(r1)], swapped)
        else:
            byte2 = get_val(words[1])
            # print(words[1], byte2)
            if len(byte2) != 4:
                raise InvalidOperandException(words[1], words[0])
            swapped = ""
            swapped += byte2[2:]
            swapped += byte2[:2]
            return "{} {:0<4}".format(v, swapped)


def sec_pass(lines):
    out_lines = list()
    loc_ctr = start_address
    for line in lines:
        words = shlex.split(line, posix=False)
        if is_lbl(words[1]):
            ins_start = 2
        elif is_ins(words[1]):
            ins_start = 1
        else:
            raise UnknownSymbolException(words[1])
        b = get_bytes(words[ins_start])
        if not b:
            raise UnknownSymbolException(words[ins_start])
        else:
            opcode = get_opcode(words[ins_start:], b)
            out_lines.append("{:04d} {}".format(loc_ctr, opcode))
            loc_ctr += b
            # raise Exception("Exception \"" + str(e) + "\" in line " + str(i) + " " + lines[i])
    return out_lines


def main():
    lines = list()
    ## Stdin as input
    try:
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
    except EOFError:
        pass
    ## Text File as input
    # with open('in.txt') as file: 
    #     for line in file.readlines():
    #         lines.append(line.replace('\n', ''))
    print(lines)
    try:
        out1 = first_pass(lines)
        print('\n1st pass\n', '\n'.join(out1), sep='')
        out2 = sec_pass(out1)
        print('\nSymbol Table')
        print(sym_tab)
        print('\n2nd pass\n', '\n'.join(out2), sep='')
        # print('\n'.join(out2))
    except Exception:
        print(traceback.format_exc())


main()
"""
sample input
ORG 1000H
Start: LXI H,2000H : "Initialize HL register pair as a pointer to memory location 2000H."
LXI D,4000H : "Initialize DE register pair as a pointer to memory location 4000H."
MOV B,M    : "Get the contents of memory location 2000H into B register."
LDAX D      : "Get the contents of memory location 4000H into A register."
MOV M,A    : "Store the contents of A register into memory location 2000H."
MOV A,B    : "Copy the contents of B register into accumulator."
STAX D      : "Store the contents of A register into memory location 4000H."
end: HLT         : "Terminate program execution."
"""
