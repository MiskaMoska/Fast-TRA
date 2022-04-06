from tqdm import tqdm
from scipy.special import comb
import networkx as nx
from construct_cdg import *
import rewrite as rw
import time
import math
import copy
iter_cnt = 0


def search_p(ls,start,depth,n,r):
    cls = copy.deepcopy(ls)
    if depth == r:
        print(ls)
        return
    for i in range(start,n-r+depth+2):
        if i == start:
            cls.append(i)
        else:
            cls[depth] = i
        # print(i)
        search_p(cls,i+1,depth+1,n,r)

def comb_tree(n,r):
    cnt = 0
    for i in range(0,r):
        cnt += comb(n-i,r-i)
    return cnt

def search_n(a,b,start,end,depth,n,r):
    global iter_cnt
    cb = copy.deepcopy(b)
    if depth == r-2:
        print(cb)
    if depth==r or start <= end:
        return

    for i in range(end,start):
        iter_cnt += 1
        real_i = start + end - i
        if i == end:
            cb.append(a[real_i-1])
        else:
            cb[depth] = (a[real_i-1])
        # if depth == 2:
        #     print(real_i)
        # search_n(n-r+depth+2,real_i,depth+1,n,r)
        search_n(a,cb,n,real_i,depth+1,n,r)

if __name__ == '__main__':
    G = construct_mesh_cdg(w=10,h=10)
    st=time.time()
    rw.find_cycle(G)
    dt=time.time()
    print(dt-st)