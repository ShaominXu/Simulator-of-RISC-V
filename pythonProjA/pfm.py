import sys


class PerfMe(object):
    def __init__(self, name, ioDir, stage_core):
        self.id = name
        self.stageCore = stage_core
        self.opFilePath = ioDir + "/PerformanceMetrics_Result.txt"


    def PrintPerf(self):
        PC = 0
        while (True):
            instr = self.stageCore.ext_imem.readInstr(PC)
            if instr == '0' * 32:
                num_instr = PC / 4
                break
            else:
                PC += 4
        cpi = self.stageCore.cycle / num_instr
        ipc = 1 / cpi

        if self.id == 'SS':
            printperf = ["Single Stage Core Performance Metrics " + "-" * 20 + "\n"]
            perm = "w"
        elif self.id == 'FS':
            printperf = ["Five Stage Core Performance Metrics " + "-" * 20 + "\n"]
            perm = "a"
        else:
            print("The stage core name is wrong!")
            sys.exit()

        printperf.append("Number of cycles taken: " + str(self.stageCore.cycle) + "\n")
        printperf.append("Cycles per instruction: {0:1.6}\n".format(cpi))
        printperf.append("Instructions per cycle: {0:1.6}\n".format(ipc))
        printperf.append("\n")

        with open(self.opFilePath, perm) as wf:
            wf.writelines(printperf)



