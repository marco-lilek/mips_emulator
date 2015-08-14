import struct
import bitstring
from bitstring import ConstBitStream
from bitstring import BitArray
from bitstring import Bits

word_size = 32

# shortcuts for converting after calc
def u_to_bits(num):
    return Bits(uint=num, length=word_size)

def i_to_bits(num):
    return Bits(int=num, length=word_size)

class MipsMachine:
    def __init__(self, word_count):
        self.word_count = word_count
        self.pc = 0
        self.mem = [u_to_bits(0)] * word_count
        self.regs = [u_to_bits(0)] * 32
        self.hi = u_to_bits(0)
        self.lo = u_to_bits(0)
        self.ir = u_to_bits(0)

    def run(self, type, filename, start):
        self.setup(type) 
        try:
            self.load(filename, start) # TODO: eventually add starting addr
            self.fetch_execute_cycle(start)
        except Exception as e:
            print('ERROR: ' + str(e) + '. pc = {0}'.format(hex(self.pc)))
            raise
        else:
            print('execution completed successfully')
            print()

    def setup(self, type):
        self.regs[30] = Bits(int=self.word_count * 4, length=word_size)
        if type == 'twoints':
            self.regs[1] = i_to_bits(int(input('Enter value for register 1: ')))
            self.regs[2] = i_to_bits(int(input('Enter value for register 2: ')))
        elif type == 'array':
            length = int(input('Enter length of array: '))
            s_addr = self.word_count - length # starting addr
            self.regs[2] = i_to_bits(length)
            for ind in range(length):
                self.mem[s_addr + ind] = i_to_bits(int(input('Enter array element {0}: '.format(ind))))
            self.regs[30] = Bits(int=s_addr * 4, length=word_size)
            self.regs[1] = self.regs[30]

    def print_results(self, display_mem):
        if display_mem:
            print('===== memory =====')
            print('{0:<8}   {1:<10}   {2}'.format('addr', 'hex', 'binary'))
            for i, val in enumerate(self.mem):
                print('{0:<8} : 0x{1:<8} : {2}'.format(hex(i * 4), val.hex, val.bin))
            print()
        print('===== registers =====')
        for i, val in enumerate(self.regs):
            if i == 0:
                continue
            print('${0:<2} = 0x{1:8} '.format(i, val.hex), end='')
            if i % 4 == 0:
                print()
        print()
    
    def load(self, filename, start):
        stream = ConstBitStream(filename=filename)
        if stream.len % 4 != 0:
            raise IOError('file length is not a multiple of 4')
        if start % 4 != 0:
            raise Exception('starting address is not a multiple of 4')
        ind = start // 4
        while True:
            try:
                word = stream.read(word_size)
            except bitstring.ReadError:
                break
            self.mem[ind] = word
            ind += 1

    def fetch_execute_cycle(self, start):
        print('===== running MIPS program =====')
        returnAddr = Bits(int=-4, length=word_size)
        self.regs[31] = returnAddr
        self.pc = start
        while True:
            if self.pc // 4 == self.word_count:
                raise RuntimeError('pc reached end of memory')
            self.ir = self.mem[self.pc // 4].uint
            self.pc += 4
            self.execute(self.ir)
            if self.pc == returnAddr.uint:
                return
   
    def execute(self, ir):
        start_ctrl_bits = (ir >> 26) & 0b111111
        end_ctrl_bits = ir & 0b111111
        s_reg_b = (ir >> 21) & 0b11111
        t_reg_b = (ir >> 16) & 0b11111
        d_reg_b = (ir >> 11) & 0b11111
        im_reg_b = Bits(uint=(ir & 0xffff), length=16).int # instead of unsigned

        if start_ctrl_bits == 0: # register command
            if end_ctrl_bits == 0b100000: # add
                self.regs[d_reg_b] = i_to_bits(self.regs[s_reg_b].int + self.regs[t_reg_b].int)
            elif end_ctrl_bits == 0b100010: # sub
                self.regs[d_reg_b] = i_to_bits(self.regs[s_reg_b].int - self.regs[t_reg_b].int)
            elif end_ctrl_bits == 0b011000: # mult
                prod = self.regs[s_reg_b].int * self.regs[t_reg_b].int
                self.lo = u_to_bits(prod & 0xffffffff) # not i_to_bits because & converts to uint
                self.hi = u_to_bits((prod >> 32) & 0xffffffff)
            elif end_ctrl_bits == 0b011001: # multu
                prod = self.regs[s_reg_b].uint * self.regs[t_reg_b].uint
                self.lo = u_to_bits(prod & 0xffffffff)
                self.hi = u_to_bits((prod >> 32) & 0xffffffff)
            elif end_ctrl_bits == 0b011010: # div
                self.hi = i_to_bits(self.regs[s_reg_b].int % self.regs[t_reg_b].int)
                self.lo = i_to_bits(self.regs[s_reg_b].int // self.regs[t_reg_b].int)
            elif end_ctrl_bits == 0b011011: # divu
                self.hi = u_to_bits(self.regs[s_reg_b].uint % self.regs[t_reg_b].uint)
                self.lo = u_to_bits(self.regs[s_reg_b].uint // self.regs[t_reg_b].uint)
            elif end_ctrl_bits == 0b010000: # mfhi
                self.regs[d_reg_b] = self.hi
            elif end_ctrl_bits == 0b010010: # mflo
                self.regs[d_reg_b] = self.lo
            elif end_ctrl_bits == 0b010100: # lis
                self.regs[d_reg_b] = self.mem[self.pc // 4]
                self.pc += 4
            elif end_ctrl_bits == 0b101010: # slt
                if self.regs[s_reg_b].int < self.regs[t_reg_b].int:
                    self.regs[d_reg_b] = u_to_bits(1)
                else:
                    self.regs[d_reg_b] = u_to_bits(0)
            elif end_ctrl_bits == 0b101011: # sltu    
                if self.regs[s_reg_b].uint < self.regs[t_reg_b].uint:
                    self.regs[d_reg_b] = u_to_bits(1)
                else:
                    self.regs[d_reg_b] = u_to_bits(0)
            elif end_ctrl_bits == 0b001000: # jr
                self.pc = self.regs[s_reg_b].uint
            elif end_ctrl_bits == 0b001001: # jalr
                temp = self.regs[s_reg_b].uint
                self.regs[31] = u_to_bits(self.pc)
                self.pc = temp
            else:
                raise RuntimeError('register - unrecognised control bits ' + str(bin(end_ctrl_bits)))
        elif start_ctrl_bits == 0b100011 or start_ctrl_bits == 0b101011: # lw / sw
            addr = self.regs[s_reg_b].uint + im_reg_b
            if addr % 4 != 0:
                raise RuntimeError('access memory at address that is not a multiple of 4')
            if addr < 0:
                raise RuntimeError('attempting to access memory at negative addr')
            
            ind = addr // 4
            if start_ctrl_bits == 0b100011: # lw
                if addr == 0xffff0004:
                    self.regs[t_reg_b] = u_to_bits(ord(input('')))
                else:
                    self.regs[t_reg_b] = self.mem[ind]
            else:
                if addr == 0xffff000c:
                    print(chr(self.regs[t_reg_b].int))
                else:
                    self.mem[ind] = self.regs[t_reg_b]

        elif start_ctrl_bits == 0b000100: # beq
            if self.regs[s_reg_b].int == self.regs[t_reg_b].int:
                self.pc += im_reg_b * 4
        elif start_ctrl_bits == 0b000101: # bne
            if self.regs[s_reg_b].int != self.regs[t_reg_b].int:
                self.pc += im_reg_b * 4
        else:
            raise RuntimeError('immediate - unrecognised control bits ' + str(bin(start_ctrl_bits)))
        
        # regardless of what happens $0 remains 0
        self.regs[0] = u_to_bits(0)
