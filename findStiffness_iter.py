import pyperclip as pc
import findStiffness as fs

stiffnesslist = []
i=100
incrSize =1
while i > 0:
    stiffnesslist.append(fs.findStiffness(i,incrSize))
    i = i-1
    pc.copy(''.join(stiffnesslist))

