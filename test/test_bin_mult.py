# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0
# Simple tests for an adder module
import cocotb
from cocotb.triggers import Timer
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles, with_timeout, ReadOnly
import random
from cocotb.binary import BinaryValue

async def  write_ram(dut, address, value):
    await RisingEdge(dut.clk)              # Synchronise to the read clock
    dut.we = 1
    dut.addr_w = address
    dut.data_in = value
    await RisingEdge(dut.clk)              # Wait 1 clock cycle
    dut.we  = 0                        # Disable write

async def read_ram(dut, address):
    await RisingEdge(dut.clk)               # Synchronise to the read clock
    dut.addr_r = address                   # Drive the value onto the signal
    await RisingEdge(dut.clk)               # Wait for 1 clock cycle

async def RST(dut):
    dut.rst  <= 1
    await ClockCycles(dut.clk, 2)
    dut.rst <= 0;
    await ClockCycles(dut.clk, 2)

async def bit_count(i):
    return bin(i).count('1')

@cocotb.test()
async def test_bin_mult(dut):
    """Test reading data from RAM"""
    clock = Clock(dut.clk, 10, units="us")
    cocotb.fork(clock.start())

    packed_input_h = int(0)
    img_matrix = []
    # generate random stream of data for the image
    for i in range(4):
        bin_val_h = random.getrandbits(7)
        img_matrix.append(bin_val_h)
        packed_input_h = packed_input_h | bin_val_h
        print(bin(packed_input_h), bin(bin_val_h))
        if i < 3:
            packed_input_h = packed_input_h << 7 

    print(bin(packed_input_h))
    
    # generate random stream of data for the image
    packed_input_l = int(0)
    for i in range(3):
        # print(i)
        bin_val_l = random.getrandbits(7)
        img_matrix.append(bin_val_l)
        packed_input_l = packed_input_l | bin_val_l
        print(bin(packed_input_l), bin(bin_val_l))
        if i < 2:
            packed_input_l = packed_input_l << 7 

    print(bin(packed_input_l))
    

    w = random.getrandbits(7)
    packed_input_l = packed_input_l << 7 
    packed_input_l = packed_input_l | w
    
    debug_op = []
    print(bin(w), w, [ bin(x) for x in img_matrix])
    # xnor popcount and sum up
    pc_sum_out_expected = 0
    for i in range(7):
        img = img_matrix[i] 
        # python uses complement for  negation as integers are signed, so this does a correction as unsigned (7 bits only) 
        xn = ((~( img ^ w) & 0xFF) & ((1<<7) - 1))
        pc = await bit_count(xn)
        im = format(img, "07b")
        wg = format(w, "07b")
        xo = format(xn, "07b")
        debug_op.append(xo)
        print("\nWEIGHT: {} \nIMAGE : {} \nXNOR  : {}\n{} \nPOPCOUNT:{}".format(wg, im, xo, bin(xn),  pc))
        pc_sum_out_expected = pc_sum_out_expected + pc

    print(debug_op)

    await RST(dut)
    dut.data_high = BinaryValue(packed_input_h)
    dut.data_low = BinaryValue(packed_input_l)
    dut.w_en <= 1 
    dut.c_rst <= 1
    await ClockCycles(dut.clk, 8)
    observed = dut.be_out.value
    expected = pc_sum_out_expected
    # print(format(expected, '07b'), observed)
    print(format(expected, '07b'), observed)
    assert observed == expected,\
               "expected = %s, observed = %s" % (expected, observed)

    dut.w_en <= 0
    dut.c_rst <= 0
    await RisingEdge(dut.clk)

      
