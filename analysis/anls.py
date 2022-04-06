import os

file1 = './output_mesh_w3_h3_n3/sp_go0_mode25_r4.txt'
file2 = './output_mesh_w3_h3_n3/sp_go0_mode32_r4.txt'

f1_ofv = []
f2_ofv = []
with open(file1,'r') as f1:
    for i,line in enumerate(f1):
        try:
            if float(line[20:30])!=0:
                f1_ofv.append(float(line[20:40]))
        except:
            pass

with open(file2,'r') as f2:
    for i,line in enumerate(f2):
        try:
            if float(line[20:30])!=0:
                f2_ofv.append(float(line[20:40]))
        except:
            pass

print(len(f1_ofv))
print(len(f2_ofv))
a = []
for i in range(len(f1_ofv)):
    a.append((f1_ofv[i]-f2_ofv[i])/f1_ofv[i])

print(sum(a)/len(a))