import sys


class InsMem(object):
    def __init__(self, name, ioDir):
        self.id = name

        with open(ioDir + "/imem.txt") as im:
            self.IMem = [data.replace("\n", "") for data in im.readlines()]

    def readInstr(self, ReadAddress):
        # read instruction memory
        if ReadAddress < len(self.IMem) :
            Instr = ''
            for i in range(4):
                Instr += self.IMem[ReadAddress + i]
        else:
            #print("No instruction")
            Instr = "0" * 32


            #sys.exit()

        # return 32 bit str
        return Instr