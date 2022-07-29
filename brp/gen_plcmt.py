import os
from copy import deepcopy
import itertools as it

os.chdir("./brp")
_W_H_ = 4 #network width and height
_N_ = 3 #number of boundary routers
_K_ = 0 #neighbor-mask threshold
_PWF_ = 0 #strong mask or weak mask
output_file = "plcmt_2d_wh"+str(_W_H_)+"_n"+str(_N_)+".txt"

cnt = 0
def is_valid_2d(x,y,n):
    if x < 0 or y < 0:
        return False
    if x >= n or y >= n:
        return False
    return True


def get_2d_neighbor(i,n,k,pwf):
    x = i % n
    y = i // n
    l = []
    if k == 0:
        l.append(i)
        return l

    if pwf == 1:
        for dx in range(x-k,x+k+1):
            for dy in range(y-k,y+k+1):
                if is_valid_2d(dx,dy,n):
                    l.append(dx + dy*n)

    elif pwf == 0:
        for dx in range(x-k,x+k+1):
            if is_valid_2d(dx,y,n):
                l.append(dx + y*n)
        for dy in range(y-k,y+k+1):
            if is_valid_2d(x,dy,n):
                l.append(x + dy*n)
        l += get_2d_neighbor(i,n,k-1,1)

    return l


def rmv_from(a,b):
    for i in b:
        try:
            a.remove(i)
        except:
            pass


def gen_comb(rcp_pi,temp_res,index,r,res,f):
    global cnt
    if index == r:  
        cnt += 1
        for i in temp_res:
            f.write(str(i)+"\n")
        return
    acp_pi_plus = deepcopy(rcp_pi)
    ct = deepcopy(temp_res)
    rcp_pi_plus = []
    flag = True
    for p in rcp_pi:
        if flag:
            ct.append(p)
        else:
            ct[index] = p
        if index != r-1:
            acp_pi_plus.remove(p)
            rcp_pi_plus = deepcopy(acp_pi_plus)
            rmv_from(rcp_pi_plus,get_2d_neighbor(p,_W_H_,_K_,_PWF_))
        gen_comb(rcp_pi_plus,ct,index+1,r,res,f)
        flag = False


if __name__ == "__main__":
    acp = [] # all candidate placement
    for i in range(_W_H_**2):
        acp.append(i)
    res = []
    t = []
    with open(output_file,"w") as f:
        gen_comb(acp,t,0,_N_,res,f)
        print("number of placements:",cnt)
        f.flush()

