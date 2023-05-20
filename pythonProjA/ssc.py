import sys
import copy

from core import Core


class SingleStageCore(Core):
    def __init__(self, ioDir, imem, dmem):
        super(SingleStageCore, self).__init__(ioDir + "/SS_", imem, dmem)
        self.opFilePath = ioDir + "/StateResult_SS.txt"

    def step(self):
        # Your implementation
        self.nextState.ID["Instr"] = self.ext_imem.readInstr(self.state.IF["PC"])

        #rd
        self.nextState.EX["Wrt_reg_addr"] = int(self.nextState.ID['Instr'][-12:-7], 2)
        #rs1
        self.nextState.EX["Rs"] = int(self.nextState.ID['Instr'][-20:-15], 2)
        #rs2
        self.nextState.EX["Rt"] = int(self.nextState.ID['Instr'][-25:-20], 2)

        self.nextState.EX["Read_data1"] = self.myRF.readRF(self.nextState.EX["Rs"])
        self.nextState.EX["Read_data2"] = self.myRF.readRF(self.nextState.EX["Rt"])

        # ADD
        if (self.nextState.ID["Instr"][-7:] == '0110011') and (self.nextState.ID["Instr"][-15:-12] == '000') and \
                (self.nextState.ID["Instr"][:-25] == '0000000') :
            self.nextState.MEM["ALUresult"] = self.nextState.EX["Read_data1"] + self.nextState.EX["Read_data2"]
            self.myRF.writeRF(self.nextState.EX["Wrt_reg_addr"], self.nextState.MEM["ALUresult"])

        # SUB
        elif (self.nextState.ID["Instr"][-7:] == '0110011') and (self.nextState.ID["Instr"][-15:-12] == '000') and \
                (self.nextState.ID["Instr"][:-25] == '0100000'):
            self.nextState.MEM["ALUresult"] = self.nextState.EX["Read_data1"] - self.nextState.EX["Read_data2"]
            self.myRF.writeRF(self.nextState.EX["Wrt_reg_addr"], self.nextState.MEM["ALUresult"])

        # XOR
        elif (self.nextState.ID["Instr"][-7:] == '0110011') and (self.nextState.ID["Instr"][-15:-12] == '100') and \
                (self.nextState.ID["Instr"][:-25] == '0000000'):
            self.nextState.MEM["ALUresult"] = self.nextState.EX["Read_data1"] ^ self.nextState.EX["Read_data2"]
            self.myRF.writeRF(self.nextState.EX["Wrt_reg_addr"], self.nextState.MEM["ALUresult"])
        # OR
        elif (self.nextState.ID["Instr"][-7:] == '0110011') and (self.nextState.ID["Instr"][-15:-12] == '110') and \
                (self.nextState.ID['Instr'][:-25] == '0000000'):
            self.nextState.MEM["ALUresult"] = self.nextState.EX["Read_data1"] | self.nextState.EX["Read_data2"]
            self.myRF.writeRF(self.nextState.EX["Wrt_reg_addr"], self.nextState.MEM["ALUresult"])
        # AND
        elif (self.nextState.ID["Instr"][-7:] == '0110011') and (self.nextState.ID["Instr"][-15:-12] == '111') and \
                (self.nextState.ID["Instr"][:-25] == '0000000'):
            self.nextState.MEM["ALUresult"] = self.nextState.EX["Read_data1"] & self.nextState.EX["Read_data2"]
            self.myRF.writeRF(self.nextState.EX["Wrt_reg_addr"], self.nextState.MEM["ALUresult"])
        # ADDI
        elif (self.nextState.ID["Instr"][-7:] == '0010011') and (self.nextState.ID["Instr"][-15:-12] == '000') :
            self.nextState.EX["Imm"] = int(self.nextState.ID["Instr"][1:12], 2)
            self.nextState.EX["Imm"] -= int(self.nextState.ID["Instr"][0]) * 2 ** 11
            self.nextState.MEM["ALUresult"] = self.nextState.EX["Read_data1"] + self.nextState.EX["Imm"]
            self.myRF.writeRF(self.nextState.EX["Wrt_reg_addr"], self.nextState.MEM["ALUresult"])
        # XORI
        elif (self.nextState.ID["Instr"][-7:] == '0010011') and (self.nextState.ID["Instr"][-15:-12] == '100') :
            self.nextState.EX["Imm"] = int(self.nextState.ID["Instr"][1:12], 2)
            self.nextState.EX["Imm"] -= int(self.nextState.ID["Instr"][0]) * 2 ** 11
            self.nextState.MEM["ALUresult"] = self.nextState.EX["Read_data1"] ^ self.nextState.EX["Imm"]
            self.myRF.writeRF(self.nextState.EX["Wrt_reg_addr"], self.nextState.MEM["ALUresult"])
        # ORI
        elif (self.nextState.ID["Instr"][-7:] == '0010011') and (self.nextState.ID["Instr"][-15:-12] == '110') :
            self.nextState.EX["Imm"] = int(self.nextState.ID["Instr"][1:12], 2)
            self.nextState.EX["Imm"] -= int(self.nextState.ID["Instr"][0]) * 2 ** 11
            self.nextState.MEM["ALUresult"] = self.nextState.EX["Read_data1"] | self.nextState.EX["Imm"]
            self.myRF.writeRF(self.nextState.EX["Wrt_reg_addr"], self.nextState.MEM["ALUresult"])
        # ANDI
        elif (self.nextState.ID["Instr"][-7:] == '0010011') and (self.nextState.ID["Instr"][-15:-12] == '111') :
            self.nextState.EX["Imm"] = int(self.nextState.ID["Instr"][1:12], 2)
            self.nextState.EX["Imm"] -= int(self.nextState.ID["Instr"][0]) * 2 ** 11
            self.nextState.MEM["ALUresult"] = self.nextState.EX["Read_data1"] & self.nextState.EX["Imm"]
            self.myRF.writeRF(self.nextState.EX["Wrt_reg_addr"], self.nextState.MEM["ALUresult"])
        # JAL
        elif self.nextState.ID["Instr"][-7:] == '1101111' :
            self.myRF.writeRF(self.nextState.EX["Wrt_reg_addr"], self.state.IF["PC"] + 4)
            imm_str = self.nextState.ID["Instr"][0] + self.nextState.ID["Instr"][12:20]
            imm_str += self.nextState.ID["Instr"][11] + self.nextState.ID["Instr"][1:11] + '0'
            self.nextState.EX["Imm"] = int(imm_str[1:21], 2) - int(imm_str[0]) * 2 ** 20
            self.nextState.IF["PC"] += self.nextState.EX["Imm"] - 4
        # BEQ
        elif (self.nextState.ID["Instr"][-7:] == '1100011') and (self.nextState.ID["Instr"][-15:-12] == '000'):
            imm_str = self.nextState.ID["Instr"][0] + self.nextState.ID["Instr"][24] + self.nextState.ID["Instr"][1:7]
            imm_str += self.nextState.ID["Instr"][20:24] + '0'
            self.nextState.EX["Imm"] = int(imm_str[1:13], 2) - int(imm_str[0]) * 2 ** 12
            if self.nextState.EX["Read_data1"] == self.nextState.EX["Read_data2"]:
                self.nextState.IF["PC"] += self.nextState.EX["Imm"] - 4
        # BNE
        elif (self.nextState.ID["Instr"][-7:] == '1100011') and (self.nextState.ID["Instr"][-15:-12] == '001'):
            imm_str = self.nextState.ID["Instr"][0] + self.nextState.ID["Instr"][24] + self.nextState.ID["Instr"][1:7]
            imm_str += self.nextState.ID["Instr"][20:24] + '0'
            self.nextState.EX["Imm"] = int(imm_str[1:13], 2) - int(imm_str[0]) * 2 ** 12
            if self.nextState.EX["Read_data1"] != self.nextState.EX["Read_data2"]:
                self.nextState.IF["PC"] += self.nextState.EX["Imm"] - 4
        # LW
        elif (self.nextState.ID["Instr"][-7:] == '0000011') and (self.nextState.ID["Instr"][-15:-12] == '000') :
            self.nextState.EX["Imm"] = int(self.nextState.ID["Instr"][1:12], 2)
            self.nextState.EX["Imm"] -= int(self.nextState.ID["Instr"][0]) * 2 ** 11
            self.nextState.MEM["ALUresult"] = self.nextState.EX["Read_data1"] + self.nextState.EX["Imm"]
            self.nextState.WB["Wrt_data"] = self.ext_dmem.readDataMem(self.nextState.MEM["ALUresult"])
            self.myRF.writeRF(self.nextState.EX["Wrt_reg_addr"], self.nextState.WB["Wrt_data"])
        # SW
        elif (self.nextState.ID["Instr"][-7:] == '0100011') and (self.nextState.ID["Instr"][-15:-12] == '010') :
            imm_str = self.nextState.ID["Instr"][:-25] + self.nextState.ID["Instr"][-12:-7]
            self.nextState.EX["Imm"] = int(imm_str[1:12], 2) - int(imm_str[0]) * 2 ** 11
            self.nextState.MEM["ALUresult"] = self.nextState.EX["Read_data1"] + self.nextState.EX["Imm"]
            self.ext_dmem.writeDataMem(self.nextState.MEM["ALUresult"],self.nextState.EX["Read_data2"])

        # HALT
        elif self.nextState.ID["Instr"][-7:] == '1111111':
            self.nextState.IF["nop"] = 1

        else:
            print('The instruction is not supported')
            print(f'instruction : {self.nextState.ID["Instr"][:-25]} {self.nextState.ID["Instr"][-25:-20]} '
                  f'{self.nextState.ID["Instr"][-20:-15]} {self.nextState.ID["Instr"][-15:-12]} '
                  f'{self.nextState.ID["Instr"][-12:-7]} {self.nextState.ID["Instr"][-7:]}')
            sys.exit()

        '''if self.nextState.IF["nop"]:
            self.halted = 1
        else:
            self.nextState.IF["PC"] += 4'''

        if not self.nextState.IF["nop"]:
            self.nextState.IF["PC"] += 4

        if self.state.IF["nop"]:
            self.halted = 1

        #test
        if self.cycle == -1:
            self.halted = 1
            print(f'cycle = {self.cycle}')
            print(self.nextState.ID['Instr'])
            print(self.nextState.ID['Instr'][-7:])
            print(self.nextState.ID['Instr'][-15:-12])
            print(self.nextState.ID['Instr'][:-25])

            print(f'rs = {self.nextState.EX["Rs"]}')
            print(f'rt = {self.nextState.EX["Rt"]}')
            print(f'rsd = {self.nextState.EX["Read_data1"]} {bin(self.nextState.EX["Read_data1"])}')
            print(f'rtd = {self.nextState.EX["Read_data2"]} {bin(self.nextState.EX["Read_data2"])}')
            print(f'ALUresult = {self.nextState.MEM["ALUresult"]}')

            print(f'imm = {self.nextState.EX["Imm"]} {bin(self.nextState.EX["Imm"])}')






        self.myRF.outputRF(self.cycle)  # dump RF
        self.printState(self.nextState, self.cycle)  # print states after executing cycle 0, cycle 1, cycle 2 ...

        self.state = copy.deepcopy(self.nextState)  # The end of the cycle and updates the current state with the values calculated in this cycle
        self.cycle += 1

    def printState(self, state, cycle):
        printstate = ["State after executing cycle: " + str(cycle) + "\n"]
        printstate.append("IF.PC: " + str(state.IF["PC"]) + "\n")
        printstate.append("IF.nop: " + str(state.IF["nop"]) + "\n")

        if (cycle == 0):
            perm = "w"
        else:
            perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)

