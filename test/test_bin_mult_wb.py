"""
test caravel wishbone
"""

from struct import pack
import cocotb
from cocotb.clock import Clock
from cocotb.binary import BinaryValue
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles
from cocotbext.wishbone.driver import WishboneMaster, WBOp
from cocotbext.wishbone.monitor import WishboneSlave
from wb_ram import WishboneRAM
import random

# from J Pallent: 
# https://github.com/thejpster/zube/blob/9299f0be074e2e30f670fd87dec2db9c495020db/test/test_zube.py
async def test_wb_set(caravel_bus, addr, value):
    """
    Test putting values into the given wishbone address.
    """
    await caravel_bus.send_cycle([WBOp(addr, value)])

async def test_wb_get(caravel_bus, addr):
    """
    Test getting values from the given wishbone address.
    """
    res_list = await caravel_bus.send_cycle([WBOp(addr)])
    rvalues = [entry.datrd for entry in res_list]
    return rvalues[0]

async def reset(dut):
    dut.caravel_wb_rst_i = 1
    dut.caravel_wb_dat_i = 0
    await ClockCycles(dut.caravel_wb_clk_i, 5)
    dut.caravel_wb_rst_i = 0
    await ClockCycles(dut.caravel_wb_clk_i, 5)

def split_data(data):

    period      = data & 0xFFFF
    ram_addr    = (data >> 16) & 0xFF
    run         = (data >> 24) & 0x1

    return period, ram_addr, run

def join_data(period, ram_addr, run):
    return (run << 24) + ((0xFF & ram_addr) << 16) + (0xFFFF & period)


# def pack_wb_frame();

def init_data_wb():
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

    

    w = random.getrandbits(7)
    packed_input_l = packed_input_l << 7 
    packed_input_l = packed_input_l | w
    
    print(bin(packed_input_l))
    
    debug_op = []
    print(bin(w), w, [ bin(x) for x in img_matrix])

    print("\n",bin(packed_input_h))
    print("\n",bin(packed_input_l))


    # ram_bus.data[1] = packed_input_h
    # ram_bus.data[2] = packed_input_l

    return (packed_input_l, packed_input_h, img_matrix, w)

def bit_count(i):
    return bin(i).count('1')

@cocotb.test()
async def test_bin_mult_wb(dut):
    """
    Run all the tests
    """
    clock = Clock(dut.caravel_wb_clk_i, 10, units="us")

    #dut.rambus_wb_ack_i = 1;
    #dut.rambus_wb_dat_i = 0xABCDEFAB;

    cocotb.fork(clock.start())

    caravel_bus_signals_dict = {
        "cyc"   :   "caravel_wb_cyc_i",
        "stb"   :   "caravel_wb_stb_i",
        "we"    :   "caravel_wb_we_i",
        "adr"   :   "caravel_wb_adr_i",
        "datwr" :   "caravel_wb_dat_i",
        "datrd" :   "caravel_wb_dat_o",
        "ack"   :   "caravel_wb_ack_o"
    }
    ram_bus_signals_dict = {
        "cyc"   :   "rambus_wb_cyc_o",
        "stb"   :   "rambus_wb_stb_o",
        "we"    :   "rambus_wb_we_o",
        "adr"   :   "rambus_wb_adr_o",
        "datwr" :   "rambus_wb_dat_o",
        "datrd" :   "rambus_wb_dat_i",
        "ack"   :   "rambus_wb_ack_i"
    }

    caravel_bus = WishboneMaster(dut, "", dut.caravel_wb_clk_i, width=32, timeout=10, signals_dict=caravel_bus_signals_dict)
    # ram_bus     = WishboneRAM    (dut, dut.rambus_wb_clk_o, ram_bus_signals_dict)

    # load a triangle wave into the ram, first 15 words (4 bytes per word, so 60 data points), starting at 10, incremementing by 1 each time
    packed_data= init_data_wb()
    img_matrix = packed_data[2]
    w = packed_data[3]
    debug_op = []
    pc_sum_out_expected = 0
    for i in range(7):
        img = img_matrix[i] 
        # python uses complement for doing negation as integers are signed, so this does a correction as unsigned (7 bits only) 
        xn = ((~( img ^ w) & 0xFF) & ((1<<7) - 1))
        pc = bit_count(xn)
        im = format(img, "07b")
        wg = format(w, "07b")
        xo = format(xn, "07b")
        debug_op.append(xo)
        print("\nWEIGHT: {} \nIMAGE : {} \nXNOR  : {}\n{} \nPOPCOUNT:{}".format(wg, im, xo, bin(xn),  pc))
        pc_sum_out_expected = pc_sum_out_expected + pc

    print(debug_op)



    await reset(dut)

    # default base addr
    base_addr = 0x3000_0000
    base_addr_next = 0x3000_0001

    # test defaults
    data = await test_wb_get(caravel_bus, base_addr)
    # print(format(packed_data[0], "031b"))
    await test_wb_set(caravel_bus, base_addr, packed_data[0])

    # # fetch it
    data = await test_wb_get(caravel_bus, base_addr)
    print(data, "------------ADDR --------------")
    await test_wb_set(caravel_bus, base_addr_next, packed_data[1])

    await ClockCycles(dut.caravel_wb_clk_i, 1)

    data2 = await test_wb_get(caravel_bus, base_addr_next)
    print(data2, "----------ADDR + 1 ----------------")
    await ClockCycles(dut.caravel_wb_clk_i, 6)

    observed = dut.be_out.value
    expected = pc_sum_out_expected
    print(format(expected, '07b'), observed, pc_sum_out_expected)
    assert observed == expected,\
               "expected = %s, observed = %s" % (expected, observed)
   

