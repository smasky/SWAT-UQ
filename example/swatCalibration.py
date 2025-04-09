import sys
sys.path.insert(0, '.')


from swatuq import SWAT_UQ

nInput = 13
nOutput = 1

projectPath = "E:\\DJBasin\\TxtInOutFSB"
exeName = "swat.exe"
workPath = "E:\\DJ_FSB"
paraFileName = "paras_infos.txt"
evalFileName = "ob1.txt"

problem = SWAT_UQ(nInput = nInput, nOutput = nOutput, projectPath = projectPath, swatExeName = exeName,
                    workPath = workPath, paraFileName = paraFileName, evalFileName = evalFileName)