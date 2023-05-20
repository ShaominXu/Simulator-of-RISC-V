
class DataMem(object):
    def __init__(self, name, ioDir):
        self.id = name
        self.ioDir = ioDir
        self.MemSize = 1000
        with open(ioDir + "/dmem.txt") as dm:
            self.DMem = [data.replace("\n", "") for data in dm.readlines()]
            for i in range(self.MemSize - len(self.DMem)):
                self.DMem.append('0'*8)



    def readDataMem(self, ReadAddress):
        # read data memory

        data_str = ''
        for i in range(4):
            data_str += self.DMem[ReadAddress + i]

        return int(data_str, 2)




    def writeDataMem(self, Address, WriteData):
        # write data into byte addressable memory
        WriteData = format(WriteData, 'b')
        WriteData = WriteData.zfill(32)

        for i in range(4):
            self.DMem[Address + i] = WriteData[i*8:(i+1)*8]

    def outputDataMem(self):
        resPath = self.ioDir + "/" + self.id + "_DMEMResult.txt"
        with open(resPath, "w") as rp:
            rp.writelines([str(data) + "\n" for data in self.DMem])