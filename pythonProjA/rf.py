
class RegisterFile(object):
    def __init__(self, ioDir):
        self.outputFile = ioDir + "RFResult.txt"
        # self.Registers = [0x0 for i in range(32)]
        self.Registers = ['0'*32 for i in range(32)]

    def readRF(self, Reg_addr):
        return int(self.Registers[Reg_addr], 2)

    def writeRF(self, Reg_addr, Wrt_reg_data):

        #x1 = 0
        if Reg_addr > 0 :
            # int to 32-bit str
            if Wrt_reg_data < 0 :
                Wrt_reg_data += 2 ** 32
            Wrt_reg_data = format(Wrt_reg_data, 'b')
            if len(Wrt_reg_data) <= 32:
                Wrt_reg_data = Wrt_reg_data.zfill(32)
            else:
                Wrt_reg_data = Wrt_reg_data[-32:]
            self.Registers[Reg_addr] = Wrt_reg_data


    def outputRF(self, cycle):
        op = ["State of RF after executing cycle: " + str(cycle) + "\n"]
        op.extend([str(val ) +"\n" for val in self.Registers])
        if (cycle == 0): perm = "w"
        else: perm = "a"
        with open(self.outputFile, perm) as file:
            file.writelines(op)