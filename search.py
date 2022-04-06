import os
import sys
import time

from sympy import arg
import rewrite as rw
from tqdm import tqdm
from math import factorial as ft
import numpy as np
import networkx as nx
from copy import deepcopy
import argparse
from construct_cdg import * 
from mdfa import *
from utils import *

parser = argparse.ArgumentParser(description='Modular Deadlock-Free Search Algorithm v1.0')
parser.add_argument('--arch', type=str, default='mesh', help='network architecture')
parser.add_argument('--w', type=int, default=4, help='network width')
parser.add_argument('--h', type=int, default=4, help='network height') 
parser.add_argument('--d', type=int, default=4, help='number of the dimension of the cube network') 
parser.add_argument('--opt', action='store_true', help='optimization search mode, otherwise list all practical solution')  
parser.add_argument('--popt',action='store_true', help='partial optimization mode, ignored when opt is False')
parser.add_argument('--r', type=int, default=4, help='maximum number of prohibited turns') 
parser.add_argument('--n', type=int, default=4, help='number of boundary routers') 
parser.add_argument('--ctn', action='store_true', help='load an archive and continue searching')
parser.add_argument('--sar',action='store_true', help='search a round for a given boundary router placement')
parser.add_argument('--bab',action='store_true', help='True: BAB-MDFA, False: MDFA')
parser.add_argument('--brl',type=list, default=[], help='boundary router list')
parser.add_argument('--mt',action='store_true', help='multi-thread accelerating')
parser.add_argument('--tn',type=int, default=4, help='thread number')
parser.add_argument('--mp',action='store_true', help='multi-process accelerating')
parser.add_argument('--pn',type=int, default=4, help='process number')
args = parser.parse_args()


def search_global():
    '''
    Search globally
    '''
    arch = args.arch
    w = args.w
    h = args.h
    d = args.d
    r = args.r
    n = args.n
    ctn = args.ctn
    is_opt = args.opt
    popt = args.popt
    is_bab = args.bab
    is_mt = args.mt
    is_mp = args.mp
    tn = args.tn
    pn = args.pn

    os.chdir('.')
    file_label = '_'+arch+'_w'+str(w)+'_h'+str(h)+'_n'+str(n)+'_r'+str(r)
    if arch == 'cube':
        file_labe = '_'+arch+'_w'+str(d)+'_n'+str(n)+'_r'+str(r)
    if not os.path.exists('./output'+file_label):
        os.makedirs('./output'+file_label)
    os.chdir('./output'+file_label)

    log_file = 'log'+('_bab' if is_bab else '')+('_popt' if popt else '')+'.txt' #optimization running log
    arch_file = 'arch'+('_bab' if is_bab else '')+('_popt' if popt else '')+'.pth' #archive 
    lp_file = 'lp'+('_bab' if is_bab else '')+('_popt' if popt else '')+'.txt' #legal placements

    if is_mt:
        log_file = 'log_mt'+('_bab' if is_bab else '')+'.txt'
        arch_file = 'arch_mt'+('_bab' if is_bab else '')+'.pth' 

    if is_mp:
        log_file = 'log_mp'+('_bab' if is_bab else '')+'.txt'
        arch_file = 'arch_mp'+('_bab' if is_bab else '')+'.pth' 

    checkpoint = torch.load(arch_file) if ctn else None
    result = dict.fromkeys(['lp','ofv','os','itc'])
    result['lp'] = []
    result['ofv'] = checkpoint['ofv'] if ctn else 0
    result['os'] = checkpoint['os'] if ctn else 'No solution'
    result['itc'] = checkpoint['itc'] if ctn else [0]

    if arch == 'mesh':
        G = construct_mesh_cdg(w=w,h=h)
    elif arch == 'torus':
        G = construct_torus_cdg(w=w,h=h)
    elif arch == 'cube':
        G = construct_cube_cdg(d=d)
    else:
        print('invalid topology:',arch)
        sys.exit()

    set_abstract_node(G)
    place_boundary_router(G,arch=arch,w=w,h=h,d=d,n=n,res=result,r=r,opt=is_opt,
                            popt=popt,ctn=ctn,tn=tn,pn=pn,lf=log_file,af=arch_file,
                            lpf=lp_file,ckpt=checkpoint,bab=is_bab,mt=is_mt,mp=is_mp)



def search_a_round():
    '''
    Search for a given boundary router placement
    '''
    arch = args.arch
    w = args.w
    h = args.h
    d = args.d
    r = args.r
    is_opt = args.opt
    is_bab = args.bab
    _brl = args.brl
    brl = []

    # construct real brl
    for i in range(len(_brl)//2):
        brl.append((int(_brl[2*i]),int(_brl[2*i+1])))
    print(brl)

    os.chdir('.')
    if not os.path.exists('./output_a_round_'+arch):
        os.makedirs('./output_a_round_'+arch)
    os.chdir('./output_a_round_'+arch)

    log_file = 'log'+('_bab' if is_bab else '')+'.txt' #optimization running log
    lp_file = 'lp'+('_bab' if is_bab else '')+'.txt' #legal placements

    result = dict.fromkeys(['lp','ofv','os','itc'])
    result['lp'] = []
    result['ofv'] = 0
    result['os'] = 'No solution'
    result['itc'] = [0]

    if arch == 'mesh':
        G = construct_mesh_cdg(w=w,h=h)
    elif arch == 'torus':
        G = construct_torus_cdg(w=w,h=h)
    elif arch == 'cube':
        G= construct_cube_cdg(d=d)
    else:
        print('invalid topology:',arch)
        sys.exit()

    set_abstract_node(G)
    set_bound_router(G,arch=arch,brl=brl,d=d)
    connect_all_bound(G,arch=arch,brl=brl)

    p_turns = []
    b_turns = init_b_turns(arch=arch,brl=brl,w=w,h=h,d=d)

    if is_bab:
        b_turns = sort_all_turns(G,arch=arch,w=w,h=h,d=d,brl=brl,act=b_turns) #sort all turns when using BAB-MDFA

    b_len = len(b_turns)
    basis = [] #basis of every layer progress
    prog = [] #coefficient of every layer progress
    p_bar_len = ft(b_len)//ft(b_len-r)
    p_bar = tqdm(total=p_bar_len)

    for j in range(r):
        basis.append(ft(b_len-1-j)//ft(b_len-r))
        prog.append(0)

    set_turns_bkwd(G,b_turns,p_turns,b_len,0,0,arch=arch,
            res=result,basis=basis,prog=prog,p_bar=p_bar,b_len=b_len,
            brl=brl,opt=is_opt,r=r,w=w,h=h,d=d,p_bar_len=p_bar_len)

    p_bar.n=p_bar_len
    p_bar.refresh()
    p_bar.close()

    with open(log_file,'w' if is_opt else 'a') as llf, \
            open(lp_file, 'a' if is_opt else 'w') as lpf:
        if is_opt:
            llf.write("Network size:"+str(w)+'*'+str(h)+"\n")
            llf.write("Turn restriction number limitation:"+str(r)+"\n")
            llf.write("Method:"+("BAB-MDFA\n" if is_bab else "MDFA\n"))
            llf.write("Boundary router list:\n")
            llf.write(str(brl)+'\n')
            llf.write("Number of all candidate turns:"+str(b_len)+"\n")
            llf.write("Ending_optimal_value:"+str(result['ofv'])+'\n')
            llf.write("Partial optimal turn-setting:\n")
            llf.write(str(result['os'])+'\n')
            llf.write("Actual iteration:"+str(result['itc'][0])+"\n")
            llf.write("Total iteration:"+str(complete_comb(b_len,r))+"\n")
            llf.flush()
        else:
            lpf.write("Network size:"+str(w)+'*'+str(h)+"\n")
            lpf.write("Turn restriction number limitation:"+str(r)+"\n")
            lpf.write("Method:"+("BAB-MDFA\n" if is_bab else "MDFA\n"))
            lpf.write("Boundary router list:\n")
            lpf.write(str(brl)+'\n')
            lpf.write("Number of all candidate turns:"+str(b_len)+"\n")
            if len(result['lp']) > 0:
                for j in range(len(result['lp'])):
                    lpf.write(str(result['lp'][j][0])+'----'+str(result['lp'][j][1])+'----'+str(result['lp'][j][2])+'\n')
                lpf.flush()


if __name__ == "__main__":
    if args.sar:
        search_a_round()
    else:
        search_global()



