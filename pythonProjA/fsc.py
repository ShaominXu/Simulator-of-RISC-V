import sys
import copy
from core import Core

class FiveStageCore(Core):
    def __init__(self, ioDir, imem, dmem):
        super(FiveStageCore, self).__init__(ioDir + "/FS_", imem, dmem)
        self.opFilePath = ioDir + "/StateResult_FS.txt"

    def step(self):
        # Your implementation
        if self.cycle == 0 :
            self.ForwardA = '00'
            self.ForwardB = '00'
            self.LW_Hazard = 0
            self.branch_stall = 0
            self.beq = 0
            self.bne = 0
            self.jal = 0


        # --------------------- WB stage ---------------------
        if self.state.WB["nop"]:
            #print("WB nop")
            self.nextState.WB["Rs"] = 0
            self.nextState.WB["Rt"] = 0
            self.nextState.WB["Wrt_reg_addr"] = 0
            self.nextState.WB["wrt_enable"] = 0
        else:
            #print("WB")
            if self.state.WB["wrt_enable"]:
                self.myRF.writeRF(self.state.WB["Wrt_reg_addr"], self.state.WB["Wrt_data"])

        # --------------------- MEM stage --------------------
        if self.state.MEM["nop"]:
            #print("MEM nop")
            self.nextState.WB["nop"] = 1
        else:
            #print("MEM")
            self.nextState.WB["nop"] = 0
            self.nextState.WB["Rs"] = self.state.MEM["Rs"]
            self.nextState.WB["Rt"] = self.state.MEM["Rt"]
            self.nextState.WB["Wrt_reg_addr"] = self.state.MEM["Wrt_reg_addr"]
            self.nextState.WB["wrt_enable"] = self.state.MEM["wrt_enable"]
            if self.state.MEM['rd_mem']:
                self.nextState.WB["Wrt_data"] = self.ext_dmem.readDataMem(self.state.MEM["ALUresult"])
            else:
                self.nextState.WB["Wrt_data"] = self.state.MEM["ALUresult"]
            if self.state.MEM["wrt_mem"]:
                self.ext_dmem.writeDataMem(self.state.MEM["ALUresult"],self.state.MEM["Store_data"])

        # --------------------- EX stage ---------------------
        if self.state.EX["nop"]:
            #print("EX nop")
            self.nextState.MEM["nop"] = 1
        else:
            #print("EX")
            self.nextState.MEM["nop"] = 0
            self.nextState.MEM["Rs"] = self.state.EX["Rs"]
            self.nextState.MEM["Rt"] = self.state.EX["Rt"]
            self.nextState.MEM["Wrt_reg_addr"] = self.state.EX["Wrt_reg_addr"]
            self.nextState.MEM["wrt_enable"] = self.state.EX["wrt_enable"]
            self.nextState.MEM["rd_mem"] = self.state.EX["rd_mem"]
            self.nextState.MEM["wrt_mem"] = self.state.EX["wrt_mem"]
            self.nextState.MEM["Store_data"] = self.state.EX["Read_data2"]

            self.alu_input0 = self.state.EX["Read_data1"]
            self.alu_input1 = self.state.EX["Read_data2"]


            if self.LW_Hazard:
                self.LW_Hazard = 0
                # lw hazard forward
                if self.ForwardA == '10':
                    self.alu_input0 = self.state.WB["Wrt_data"]
                elif self.ForwardA == '01':
                    self.alu_input0 = self.myRF.readRF(self.state.EX["Rs"])
                if self.ForwardB == '10':
                    if self.state.EX["wrt_mem"]:
                        self.nextState.MEM["Store_data"] = self.state.WB["Wrt_data"]
                    else:
                        self.alu_input1 = self.state.WB["Wrt_data"]
                elif self.ForwardB == '01':
                    if self.state.EX["wrt_mem"]:
                        self.nextState.MEM["Store_data"] = self.myRF.readRF(self.state.EX["Rt"])
                    else:
                        self.alu_input1 = self.myRF.readRF(self.state.EX["Rt"])
            else:
                # RAW hazard forward
                if self.ForwardA == '10':
                    self.alu_input0 = self.state.MEM["ALUresult"]
                elif self.ForwardA == '01':
                    self.alu_input0 = self.state.WB["Wrt_data"]

                if self.ForwardB == '10':
                    if self.state.EX["wrt_mem"]:
                        self.nextState.MEM["Store_data"] = self.state.MEM["ALUresult"]
                    else:
                        self.alu_input1 = self.state.MEM["ALUresult"]
                elif self.ForwardB == '01':
                    if self.state.EX["wrt_mem"]:
                        self.nextState.MEM["Store_data"] = self.state.WB["Wrt_data"]
                    else:
                        self.alu_input1 = self.state.WB["Wrt_data"]


            if self.state.EX["is_I_type"]:
                self.alu_input1 = self.state.EX["Imm"]

            if self.state.EX["alu_op"] == '00':
                self.nextState.MEM["ALUresult"] = self.alu_input0 + self.alu_input1
            elif self.state.EX["alu_op"] == '01':
                self.nextState.MEM["ALUresult"] = self.alu_input0 - self.alu_input1
            elif self.state.EX["alu_op"] == '10':
                self.nextState.MEM["ALUresult"] = self.alu_input0 & self.alu_input1
            elif self.state.EX["alu_op"] == '11':
                self.nextState.MEM["ALUresult"] = self.alu_input0 | self.alu_input1
            elif self.state.EX["alu_op"] == 'xor':
                self.nextState.MEM["ALUresult"] = self.alu_input0 ^ self.alu_input1
            else:
                print("The ALU operation is not supported!")


        # --------------------- ID stage ---------------------
        if self.state.ID["nop"]:
            #print("ID nop")
            self.nextState.EX["nop"] = 1

        else:
            #print("ID")
            self.nextState.EX["nop"] = 0
            self.nextState.EX["Wrt_reg_addr"] = int(self.state.ID["Instr"][-12:-7], 2)
            self.nextState.EX["Rs"] = int(self.state.ID["Instr"][-20:-15], 2)
            self.nextState.EX["Rt"] = int(self.state.ID["Instr"][-25:-20], 2)

            self.nextState.EX["Read_data1"] = self.myRF.readRF(self.nextState.EX["Rs"])
            self.nextState.EX["Read_data2"] = self.myRF.readRF(self.nextState.EX["Rt"])



            # Data Hazard
            self.ForwardA = '00'
            self.ForwardB = '00'
            if self.nextState.MEM["wrt_enable"] and self.nextState.MEM["Wrt_reg_addr"]:
                if self.nextState.MEM["Wrt_reg_addr"] == self.nextState.EX["Rs"]:
                    self.ForwardA = '10'
                if self.nextState.MEM["Wrt_reg_addr"] == self.nextState.EX["Rt"]:
                    self.ForwardB = '10'
            if self.nextState.WB["wrt_enable"] and self.nextState.WB["Wrt_reg_addr"]:
                if self.nextState.WB["Wrt_reg_addr"] == self.nextState.EX["Rs"]:
                    self.ForwardA = '01'
                if self.nextState.WB["Wrt_reg_addr"] == self.nextState.EX["Rt"]:
                    self.ForwardB = '01'

            # LW Hazard
            self.LW_Hazard = 0
            if self.nextState.MEM["rd_mem"]:
                if (self.nextState.MEM["Wrt_reg_addr"] == self.nextState.EX["Rs"]) or \
                        (self.nextState.MEM["Wrt_reg_addr"] == self.nextState.EX["Rt"]):
                    self.LW_Hazard = 1



            # ADD
            if (self.state.ID["Instr"][-7:] == '0110011') and (self.state.ID["Instr"][-15:-12] == '000') and \
                    (self.state.ID["Instr"][:-25] == '0000000'):
                self.nextState.EX["is_I_type"] = 0
                self.nextState.EX["rd_mem"] = 0
                self.nextState.EX["wrt_mem"] = 0
                self.nextState.EX["alu_op"] = '00'
                self.nextState.EX["wrt_enable"] = 1

            # SUB
            elif (self.nextState.ID["Instr"][-7:] == '0110011') and (self.nextState.ID["Instr"][-15:-12] == '000') and \
                    (self.nextState.ID["Instr"][:-25] == '0100000'):
                self.nextState.EX["is_I_type"] = 0
                self.nextState.EX["rd_mem"] = 0
                self.nextState.EX["wrt_mem"] = 0
                self.nextState.EX["alu_op"] = '01'
                self.nextState.EX["wrt_enable"] = 1
            # XOR
            elif (self.nextState.ID["Instr"][-7:] == '0110011') and (self.nextState.ID["Instr"][-15:-12] == '100') and \
                    (self.nextState.ID["Instr"][:-25] == '0000000'):
                self.nextState.EX["is_I_type"] = 0
                self.nextState.EX["rd_mem"] = 0
                self.nextState.EX["wrt_mem"] = 0
                self.nextState.EX["alu_op"] = 'xor'
                self.nextState.EX["wrt_enable"] = 1
            # OR
            elif (self.nextState.ID["Instr"][-7:] == '0110011') and (self.nextState.ID["Instr"][-15:-12] == '110') and \
                    (self.nextState.ID['Instr'][:-25] == '0000000'):
                self.nextState.EX["is_I_type"] = 0
                self.nextState.EX["rd_mem"] = 0
                self.nextState.EX["wrt_mem"] = 0
                self.nextState.EX["alu_op"] = '11'
                self.nextState.EX["wrt_enable"] = 1
            # AND
            elif (self.nextState.ID["Instr"][-7:] == '0110011') and (self.nextState.ID["Instr"][-15:-12] == '111') and \
                    (self.nextState.ID["Instr"][:-25] == '0000000'):
                self.nextState.EX["is_I_type"] = 0
                self.nextState.EX["rd_mem"] = 0
                self.nextState.EX["wrt_mem"] = 0
                self.nextState.EX["alu_op"] = '10'
                self.nextState.EX["wrt_enable"] = 1
            # ADDI
            elif (self.nextState.ID["Instr"][-7:] == '0010011') and (self.nextState.ID["Instr"][-15:-12] == '000'):
                self.nextState.EX["Imm"] = int(self.nextState.ID["Instr"][1:12], 2)
                self.nextState.EX["Imm"] -= int(self.nextState.ID["Instr"][0]) * 2 ** 11
                self.nextState.EX["is_I_type"] = 1
                self.nextState.EX["rd_mem"] = 0
                self.nextState.EX["wrt_mem"] = 0
                self.nextState.EX["alu_op"] = '00'
                self.nextState.EX["wrt_enable"] = 1
            # XORI
            elif (self.nextState.ID["Instr"][-7:] == '0010011') and (self.nextState.ID["Instr"][-15:-12] == '100'):
                self.nextState.EX["Imm"] = int(self.nextState.ID["Instr"][1:12], 2)
                self.nextState.EX["Imm"] -= int(self.nextState.ID["Instr"][0]) * 2 ** 11
                self.nextState.EX["is_I_type"] = 1
                self.nextState.EX["rd_mem"] = 0
                self.nextState.EX["wrt_mem"] = 0
                self.nextState.EX["alu_op"] = 'xor'
                self.nextState.EX["wrt_enable"] = 1
            # ORI
            elif (self.nextState.ID["Instr"][-7:] == '0010011') and (self.nextState.ID["Instr"][-15:-12] == '110'):
                self.nextState.EX["Imm"] = int(self.nextState.ID["Instr"][1:12], 2)
                self.nextState.EX["Imm"] -= int(self.nextState.ID["Instr"][0]) * 2 ** 11
                self.nextState.EX["is_I_type"] = 1
                self.nextState.EX["rd_mem"] = 0
                self.nextState.EX["wrt_mem"] = 0
                self.nextState.EX["alu_op"] = '11'
                self.nextState.EX["wrt_enable"] = 1
            # ANDI
            elif (self.nextState.ID["Instr"][-7:] == '0010011') and (self.nextState.ID["Instr"][-15:-12] == '111'):
                self.nextState.EX["Imm"] = int(self.nextState.ID["Instr"][1:12], 2)
                self.nextState.EX["Imm"] -= int(self.nextState.ID["Instr"][0]) * 2 ** 11
                self.nextState.EX["is_I_type"] = 1
                self.nextState.EX["rd_mem"] = 0
                self.nextState.EX["wrt_mem"] = 0
                self.nextState.EX["alu_op"] = '10'
                self.nextState.EX["wrt_enable"] = 1
            # JAL
            elif self.nextState.ID["Instr"][-7:] == '1101111':
                imm_str = self.nextState.ID["Instr"][0] + self.nextState.ID["Instr"][12:20]
                imm_str += self.nextState.ID["Instr"][11] + self.nextState.ID["Instr"][1:11] + '0'
                self.nextState.EX["Imm"] = int(imm_str[1:21], 2) - int(imm_str[0]) * 2 ** 20
                self.nextState.EX["is_I_type"] = 0
                self.nextState.EX["rd_mem"] = 0
                self.nextState.EX["wrt_mem"] = 0
                self.nextState.EX["alu_op"] = '00'
                self.nextState.EX["wrt_enable"] = 1
                self.nextState.EX["Read_data1"] = 0
                self.nextState.EX["Read_data2"] = self.state.IF['PC']
                self.jal = 1
                self.branch_stall = 1


            # BEQ
            elif (self.nextState.ID["Instr"][-7:] == '1100011') and (self.nextState.ID["Instr"][-15:-12] == '000'):
                imm_str = self.nextState.ID["Instr"][0] + self.nextState.ID["Instr"][24]
                imm_str += self.nextState.ID["Instr"][1:7] + self.nextState.ID["Instr"][20:24] + '0'
                self.nextState.EX["Imm"] = int(imm_str[1:13], 2) - int(imm_str[0]) * 2 ** 12
                self.nextState.EX["is_I_type"] = 0
                self.nextState.EX["rd_mem"] = 0
                self.nextState.EX["wrt_mem"] = 0
                self.nextState.EX["alu_op"] = 'beq'
                self.nextState.EX["wrt_enable"] = 0
                self.beq = 1

            # BNE
            elif (self.nextState.ID["Instr"][-7:] == '1100011') and (self.nextState.ID["Instr"][-15:-12] == '001'):
                imm_str = self.nextState.ID["Instr"][0] + self.nextState.ID["Instr"][24]
                imm_str += self.nextState.ID["Instr"][1:7] + self.nextState.ID["Instr"][20:24] + '0'
                self.nextState.EX["Imm"] = int(imm_str[1:13], 2) - int(imm_str[0]) * 2 ** 12
                self.nextState.EX["is_I_type"] = 0
                self.nextState.EX["rd_mem"] = 0
                self.nextState.EX["wrt_mem"] = 0
                self.nextState.EX["alu_op"] = 'bne'
                self.nextState.EX["wrt_enable"] = 0
                self.bne = 1




            # LW
            elif (self.state.ID["Instr"][-7:] == '0000011') and (self.state.ID["Instr"][-15:-12] == '000') :
                 self.nextState.EX["Imm"] = int(self.nextState.ID["Instr"][1:12], 2)
                 self.nextState.EX["Imm"] -= int(self.nextState.ID["Instr"][0]) * 2 ** 11
                 self.nextState.EX["is_I_type"] = 1
                 self.nextState.EX["rd_mem"] = 1
                 self.nextState.EX["wrt_mem"] = 0
                 self.nextState.EX["alu_op"] = '00'
                 self.nextState.EX["wrt_enable"] = 1


            # SW
            elif (self.state.ID["Instr"][-7:] == '0100011') and (self.state.ID["Instr"][-15:-12] == '010') :
                imm_str = self.state.ID["Instr"][:-25] + self.state.ID["Instr"][-12:-7]
                self.nextState.EX["Imm"] = int(imm_str[1:12], 2) - int(imm_str[0]) * 2 ** 11
                self.nextState.EX["is_I_type"] = 1
                self.nextState.EX["rd_mem"] = 0
                self.nextState.EX["wrt_mem"] = 1
                self.nextState.EX["alu_op"] = '00'
                self.nextState.EX["wrt_enable"] = 0

            else:
                print('The instruction is not supported')
                print(f'instruction : {self.nextState.ID["Instr"][:-25]} {self.nextState.ID["Instr"][-25:-20]} '
                      f'{self.nextState.ID["Instr"][-20:-15]} {self.nextState.ID["Instr"][-15:-12]} '
                      f'{self.nextState.ID["Instr"][-12:-7]} {self.nextState.ID["Instr"][-7:]}')
                sys.exit()


            # brach condition
            if self.bne or self.beq:
                if self.ForwardA == '10':
                    self.nextState.EX["Read_data1"] = self.nextState.MEM["ALUresult"]
                elif self.ForwardA == '01':
                    self.nextState.EX["Read_data1"] = self.nextState.WB["Wrt_data"]
                if self.ForwardB == '10':
                    self.nextState.EX["Read_data2"] = self.nextState.MEM["ALUresult"]
                elif self.ForwardB == '01':
                    self.nextState.EX["Read_data2"] = self.nextState.WB["Wrt_data"]

                if self.bne:
                    if self.nextState.EX["Read_data1"] != self.nextState.EX["Read_data2"]:
                        self.branch_stall = 1
                if self.beq:
                    if self.nextState.EX["Read_data1"] == self.nextState.EX["Read_data2"]:
                        self.branch_stall = 1





        # --------------------- IF stage ---------------------
        if self.state.IF["nop"]:
            #print("IF nop")
            if not self.LW_Hazard:
                self.nextState.ID["nop"] = 1
        else:
            #print("IF")
            self.nextState.ID["Instr"] = self.ext_imem.readInstr(self.state.IF["PC"])

            # HALT
            if self.nextState.ID["Instr"][-7:] == '1111111':
                self.nextState.IF["nop"] = 1
                self.nextState.ID["nop"] = 1
            else:
                self.nextState.IF["nop"] = 0
                self.nextState.ID["nop"] = 0

        if self.LW_Hazard:
            if self.state.EX["nop"]:
                self.nextState.IF["nop"] = 0
                self.nextState.ID["nop"] = 0
                self.nextState.EX["nop"] = 0
            else:
                self.nextState.IF["nop"] = 1
                self.nextState.ID["nop"] = 1
                self.nextState.EX["nop"] = 1

        if self.bne or self.beq:
            self.bne = 0
            self.beq = 0
            self.nextState.EX["nop"] = 1

        if self.branch_stall:
            #print("branch stall")
            self.branch_stall = 0
            self.nextState.IF["nop"] = 0
            self.nextState.ID["nop"] = 1
            self.nextState.EX["nop"] = 1
            self.nextState.IF["PC"] += self.nextState.EX["Imm"] - 4
            if self.jal:
                self.jal = 0
                self.nextState.EX["nop"] = 0
        else:
            if not self.nextState.IF["nop"]:
                self.nextState.IF["PC"] += 4

        # test
        if self.cycle == -1 :
            self.halted = 1
            print(f'cycle = {self.cycle}')
            print(f'LW_Hazard = {self.LW_Hazard}')
            print(f'ForwardA = {self.ForwardA}')
            print(f'ForwardB = {self.ForwardB}')
            print(f'PC = {self.nextState.IF["PC"]}')
            if self.state.WB["wrt_enable"]:
                print(f'{format(self.state.WB["Wrt_data"],"b")} wr {self.state.WB["Wrt_reg_addr"]}')
            if self.state.MEM["wrt_mem"]:
                print(f'{format(self.state.MEM["Store_data"],"b")} wd {self.state.MEM["ALUresult"]}')

        if self.state.IF["nop"] and self.state.ID["nop"] and self.state.EX["nop"] and self.state.MEM["nop"] and \
                self.state.WB["nop"]:
            self.halted = 1

        self.myRF.outputRF(self.cycle)  # dump RF
        self.printState(self.nextState, self.cycle)  # print states after executing cycle 0, cycle 1, cycle 2 ...

        self.state = copy.deepcopy(self.nextState)  # The end of the cycle and updates the current state with the values calculated in this cycle
        self.cycle += 1

    def printState(self, state, cycle):
        printstate = ["-" * 70 + "\n", "State after executing cycle: " + str(cycle) + "\n"]
        printstate.extend("\n")
        printstate.extend(["IF." + key + ": " + str(val) + "\n" for key, val in state.IF.items()])
        printstate.extend("\n")
        printstate.extend(["ID." + key + ": " + str(val) + "\n" for key, val in state.ID.items()])
        printstate.extend("\n")
        printstate.extend(["EX." + key + ": " + str(val) + "\n" for key, val in state.EX.items()])
        printstate.extend("\n")
        printstate.extend(["MEM." + key + ": " + str(val) + "\n" for key, val in state.MEM.items()])
        printstate.extend("\n")
        printstate.extend(["WB." + key + ": " + str(val) + "\n" for key, val in state.WB.items()])
        printstate.extend("\n")

        if (cycle == 0):
            perm = "w"
        else:
            perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)