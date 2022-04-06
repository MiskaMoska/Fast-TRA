import os
import sys
import copy
import torch
import threading
import multiprocessing as mp
import rewrite as rw
from tqdm import tqdm
from math import factorial as ft
import numpy as np
import networkx as nx
from copy import deepcopy
import itertools as it
from construct_cdg import *
from utils import *


def run_a_process(lock,**kwargs):
    '''
    This function runs for a single thread in multi-thread mode

    Parameters
    ---------------------
    @ lock      :mutex

    @ kwargs

    arch        :architecture of the target network (str)
    i           :index of current boundary router list (int)
    w           :network width (int)
    h           :network height (int)
    d           :number of the dimension of the cube network (int)
    r           :maximum recursion depth (int)
    brl:        :boundary router list (list)
    bab         :indicates whether adopting BAB-MDFA (bool)
    fp          :log file path (str)
    af          :archive file path (str)
    apn         :number of all boundary router placements (int)
    '''
    arch = kwargs['arch']
    i = kwargs['i']
    w = kwargs['w']
    h = kwargs['h']
    d = kwargs['d']
    r = kwargs['r']
    brl = kwargs['brl']
    is_bab = kwargs['bab']
    fp = kwargs['fp']
    af = kwargs['af'] 
    apn = kwargs['apn']

    if arch == 'mesh':
        cdg = construct_mesh_cdg(w=w,h=h)
    elif arch == 'torus':
        cdg = construct_torus_cdg(w=w,h=h)
    elif arch == 'cube':
        cdg = construct_cube_cdg(d=d)
    else:
        print('invalid topology:',arch)
        sys.exit()

    set_abstract_node(cdg)
    res = dict(lp=[],ofv=0,os=None,itc=[0]) #private res for each thread
    #// cdg = copy.deepcopy(G) #copy the CDG
    set_bound_router(cdg,arch=arch,brl=brl,d=d)
    connect_all_bound(cdg,arch=arch,brl=brl)
    b_turns = init_b_turns(brl=brl,arch=arch,w=w,h=h,d=d)

    # sort all candidate turns
    if is_bab:
        b_turns = sort_all_turns(cdg,arch=arch,w=w,h=h,d=d,brl=brl,act=b_turns)
    p_turns = []
    b_len = len(b_turns)
    basis = [] #basis of every layer progress
    prog = [] #coefficient of every layer progress
    for j in range(r):
        basis.append(int(ft(b_len-1-j)/ft(b_len-r)))
        prog.append(0)
    p_bar_len = int(ft(b_len)/ft(b_len-r))
    p_bar = tqdm(total=p_bar_len)
    p_bar.set_description(str(i+1)+'/'+str(apn))

    set_turns_bkwd(cdg,b_turns,p_turns,b_len,0,0,arch=arch,
            res=res,basis=basis,prog=prog,p_bar=p_bar,b_len=b_len,
            brl=brl,opt=True,r=r,w=w,h=h,d=d,p_bar_len=p_bar_len)

    # end progress bar
    p_bar.n=p_bar_len
    p_bar.refresh()
    p_bar.close()

    # write to log file
    lock.acquire()
    with open(fp,'a') as llf:
        llf.write('{:<20}{:<30}{:<30}{:<20}{:<30}{:<30}\n'.format(str(i+1)+'/'+str(apn),
                    'actual_iter:'+str(res['itc'][0]),'total_iter:'+str(complete_comb(b_len,r)),
                    'get solution' if res['os'] else '-',res['ofv'],'boundary_router:'+str(brl)))
        llf.flush()

    # save checkpoint
    sd = torch.load(af)
    sd['i'].append(i)
    sd['ofv'] = None #not used
    sd['os'] = None #not used
    sd['itc'] = None #not used
    torch.save(sd,af)
    lock.release()


def run_a_thread(G,**kwargs):
    '''
    This function runs for a single thread in multi-thread mode

    Parameters
    ---------------------
    @ G         :target CDG

    @ kwargs

    arch        :architecture of the target network (str)
    i           :index of current boundary router list (int)
    w           :network width (int)
    h           :network height (int)
    d           :number of the dimension of the cube network (int)
    r           :maximum recursion depth (int)
    brl:        :boundary router list (list)
    bab         :indicates whether adopting BAB-MDFA (bool)
    llf         :the handle of opened log file (handle)

    sd          :global state_dict (dict)
        -abp    :all boundary router placements (list)
        -i      :[multi-thread mode]the index of current boundary routers (int)
                :[single-thread mode]the indexes of all searched boundary routers (list)   
        -ofv    :latest-updated object function value (float) --only valid at optimal mode
        -os     :latest-updated optimal solution (list) --only valid at optimal mode
        -itc    :latest-updated iteration count (list) --only valid at optimal mode
        
    af          :archive file path (str)
    lock        :global thread lock (threading.lock)
    smp         :global semaphore (threading.semaphore)
    apn         :number of all boundary router placements (int)
    '''
    arch = kwargs['arch']
    i = kwargs['i']
    w = kwargs['w']
    h = kwargs['h']
    d = kwargs['d']
    r = kwargs['r']
    brl = kwargs['brl']
    is_bab = kwargs['bab']
    llf = kwargs['llf']
    sd = kwargs['sd'] #state_dict
    af = kwargs['af'] #arch_file
    lock = kwargs['lock']
    smp = kwargs['smp']
    apn = kwargs['apn']

    smp.acquire()
    res = dict(lp=[],ofv=0,os=None,itc=[0]) #private res for each thread
    cdg = copy.deepcopy(G) #copy the CDG, for different boundary router placements should be independent
    set_bound_router(cdg,arch=arch,brl=brl,d=d)
    connect_all_bound(cdg,arch=arch,brl=brl)
    b_turns = init_b_turns(brl=brl,arch=arch,w=w,h=h,d=d)

    # sort all candidate turns
    if is_bab:
        b_turns = sort_all_turns(cdg,arch=arch,w=w,h=h,d=d,brl=brl,act=b_turns)
    p_turns = []
    b_len = len(b_turns)
    basis = [] #basis of every layer progress
    prog = [] #coefficient of every layer progress
    for j in range(r):
        basis.append(int(ft(b_len-1-j)/ft(b_len-r)))
        prog.append(0)
    p_bar_len = int(ft(b_len)/ft(b_len-r))
    p_bar = tqdm(total=p_bar_len)
    p_bar.set_description(str(i+1)+'/'+str(apn))

    set_turns_bkwd(cdg,b_turns,p_turns,b_len,0,0,arch=arch,
            res=res,basis=basis,prog=prog,p_bar=p_bar,b_len=b_len,
            brl=brl,opt=True,r=r,w=w,h=h,d=d,p_bar_len=p_bar_len)

    # end progress bar
    p_bar.n=p_bar_len
    p_bar.refresh()
    p_bar.close()

    # write to log file
    lock.acquire()
    llf.write('{:<20}{:<30}{:<30}{:<20}{:<10}\n'.format(str(i+1)+'/'+str(apn),
                'actual_iter:'+str(res['itc'][0]),'total_iter:'+str(complete_comb(b_len,r)),
                'get solution' if res['os'] else '-','boundary_router:'+str(brl)))
    llf.flush()

    # save checkpoint
    sd['i'].append(i)
    sd['ofv'] = None #not used
    sd['os'] = None #not used
    sd['itc'] = None #not used
    torch.save(sd,af)
    lock.release()
    smp.release()


def place_boundary_router(G,**kwargs):
    '''
    This function tries all possible boundary router placements and sets turns

    Parameters
    ---------------------
    @ G         :target CDG

    @ kwargs

    arch        :architecture of the target network (str)
    w           :network width (int)
    h           :network height (int)
    n           :number of boundary routers (int)
    d           :number of dimension of the cube network (int)
    r           :maximum recursion depth (int)
    brl:        :boundary router list (list)
    opt         :indicates whether at optimal mode, otherwise at list-all mode (bool)
    bab         :indicates whether adopting BAB-MDFA (bool)
    popt        :indicates whether run partial optimization (bool) --only valid at optimal mode
    mp          :indicates whether using multi-process (bool)
    mt          :indicates whether using multi-thread (bool)
    pn          :process number (int) --only valid when mp is True
    tn          :thread number (int) --only valid when mt is True
    ctn         :indicates whether load an archive and continue searching (bool)

    lf          :log file path (str)
    lpf         :legal placement file path (str)
    af          :archive file path (str)

    ckpt        :checkpoint dict (dict)
        -abp    :all boundary router placements (list)
        -i      :[multi-thread mode]the index of current boundary routers (int)
                :[single-thread mode]the indexes of all searched boundary routers (list)   
        -ofv    :latest-updated object function value (float) --only valid at optimal mode
        -os     :latest-updated optimal solution (list) --only valid at optimal mode
        -itc    :latest-updated iteration count (list) --only valid at optimal mode

    res         :result dict of the whole algorithm (dict)
        -lp     :list of all legal places (list) --only valid at list-all mode
        -ofv    :real-time-updated object function value (float) --only valid at optimal mode
        -os     :real-time-updated optimal solution (list) --only valid at optimal mode
        -itc    :latest-updated iteration count (list) --only valid at optimal mode
    '''
    arch = kwargs['arch']
    w = kwargs['w']
    h = kwargs['h']
    d = kwargs['d']
    n = kwargs['n']
    r = kwargs['r']
    is_opt = kwargs['opt']
    is_bab = kwargs['bab']
    popt = kwargs['popt']
    is_mp = kwargs['mp']
    is_mt = kwargs['mt']
    pn = kwargs['pn']
    tn = kwargs['tn']
    ctn = kwargs['ctn']
    log_file = kwargs['lf']
    lp_file = kwargs['lpf']
    arch_file = kwargs['af']
    ckpt = kwargs['ckpt']
    res = kwargs['res']
    all_router = []

    if arch == 'mesh' or arch == 'torus':
        for x in range(w):
            for y in range(h):
                all_router.append((x,y))
    elif arch == 'cube':
        for i in range(2**d):
            all_router.append(dec2bin(i,bit_wide=d))

    all_boundary_placement = ckpt['abp'] if ctn else list(it.combinations(all_router,n)) 
    all_placement_number = len(all_boundary_placement)
    state_dict = dict.fromkeys(['abp','i','ofv','os','itc'])
    state_dict['abp'] = all_boundary_placement

    if is_mp: #multi-process
        if not ctn: #there is default to be no archive file, so create a archive file
            start_state = dict(abp=all_boundary_placement,i=[],ofv=None,os=None,itc=None)
            torch.save(start_state,arch_file)
        state_dict['i'] = ckpt['i'] if ctn else []
        print('Already done:',len(state_dict['i']),'out of',str(all_placement_number))
        lock = mp.Manager().Lock()
        if not ctn:
            with open(log_file,'w') as llf:
                llf.write('Multi-process Accelerating....\n')
                llf.flush()
        for i in range(all_placement_number//pn+1):
            process_list = []
            for j in range(pn):
                idx = i*pn + j
                if idx in state_dict['i'] or idx >= all_placement_number:
                    continue
                bound_router = all_boundary_placement[idx]
                _kwargs = mp.Manager().dict()
                _kwargs = {'arch':arch,'i':idx,'w':w,'h':h,'d':d,'r':r,'brl':bound_router,'bab':is_bab,
                                    'fp':log_file,'af':arch_file,'apn':all_placement_number}
                tp = mp.Process(target=run_a_process, args=(lock, ), kwargs=_kwargs)
                process_list.append(tp)
            if len(process_list) > 0:
                for tp in process_list:
                    tp.start()
                for tp in process_list:
                    tp.join()
                print("Ending an old batch,starting a new batch.... Please don't move")

    elif is_mt: #multi-thread
        state_dict['i'] = ckpt['i'] if ctn else []
        print('Already done:',len(state_dict['i']),'out of',str(all_placement_number))
        smp=threading.Semaphore(tn)
        lock = threading.Lock()
        if not ctn:
            with open(log_file,'w') as llf:
                llf.write('Multi-thread Accelerating....\n')
                llf.flush()
        with open(log_file,'a') as llf:
            _args =  (G, )
            thread_list = [] #mark all the running threads
            for i in range(0,all_placement_number):
                if i in state_dict['i']:
                    continue
                bound_router = all_boundary_placement[i]
                _kwargs = dict(i=i,w=w,h=h,d=d,r=r,brl=bound_router,bab=is_bab,llf=llf,sd=state_dict,
                                af=arch_file,lock=lock,smp=smp,apn=all_placement_number,arch=arch)
                tt = threading.Thread(target=run_a_thread, args=_args, kwargs=_kwargs)
                thread_list.append(tt)
                tt.start()
            for thread in thread_list:
                thread.join()
            print('Done')

    else: #single thread
        with open(log_file,'a' if ctn or not is_opt else 'w') as llf, \
                open(lp_file, 'a' if ctn or is_opt else 'w') as lpf:
            for i in range(ckpt['i']+1 if ctn else 0,all_placement_number):
                bound_router = all_boundary_placement[i]
                cdg = copy.deepcopy(G) #copy the CDG, for different boundary router placements should be independent
                set_bound_router(cdg,arch=arch,brl=bound_router,d=d)
                connect_all_bound(cdg,arch=arch,brl=bound_router)

                print("\n\n")
                print(str(i+1)+"/"+str(all_placement_number)+80*"-")
                print("Starting_optimal_value:",res['ofv'])
                print("Method:"+("BAB-MDFA" if is_bab else "MDFA"))
                # print("is_connected at the beginning:",is_connected(cdg,w=w,h=h))
                
                # initialize all candidate turns
                b_turns = init_b_turns(arch=arch,brl=bound_router,w=w,h=h,d=d)

                # sort all candidate turns
                if is_bab:
                    b_turns = sort_all_turns(cdg,arch=arch,w=w,h=h,d=d,brl=bound_router,act=b_turns)

                p_turns = []
                b_len = len(b_turns)
                basis = [] #basis of every layer progress
                prog = [] #coefficient of every layer progress
                
                for j in range(r):
                    basis.append(int(ft(b_len-1-j)/ft(b_len-r)))
                    prog.append(0)

                # write to files
                if is_opt:
                    llf.write('\n\n')
                    llf.write(str(i+1)+"/"+str(all_placement_number)+80*"-"+'\n')
                    llf.write("Starting_optimal_value:"+str(res['ofv'])+'\n')
                    llf.write("Method:"+("BAB-MDFA\n" if is_bab else "MDFA\n"))
                    llf.write("Boundary router list:\n")
                    llf.write(str(bound_router)+'\n')
                    llf.write("Number of all candidate turns:"+str(b_len)+"\n")
                    llf.flush()
                else:
                    lpf.write('\n\n')
                    lpf.write(str(i+1)+"/"+str(all_placement_number)+80*"-"+'\n')
                    lpf.write("Starting_optimal_value:"+str(res['ofv'])+'\n')
                    llf.write("Method:"+("BAB-MDFA\n" if is_bab else "MDFA\n"))
                    lpf.write("Boundary router list:\n")
                    lpf.write(str(bound_router)+'\n')
                    lpf.write("Number of all candidate turns:"+str(b_len)+"\n")
                    lpf.flush()
                    
                print("Boundary router list:")
                print(bound_router)
                print("Number of all candidate turns:",b_len)
                
                p_bar_len = int(ft(b_len)/ft(b_len-r))
                p_bar = tqdm(total=p_bar_len)

                res['lp'].clear()
                set_turns_bkwd(cdg,b_turns,p_turns,b_len,0,0,arch=arch,
                        res=res,basis=basis,prog=prog,p_bar=p_bar,b_len=b_len,d=d,
                        brl=bound_router,opt=is_opt,r=r,w=w,h=h,p_bar_len=p_bar_len)

                # end progress bar 
                p_bar.n=p_bar_len
                p_bar.refresh()
                p_bar.close()

                # write to files
                if is_opt:
                    llf.write("Ending_optimal_value:"+str(res['ofv'])+'\n')
                    llf.write("Partial optimal turn-setting:\n")
                    llf.write(str(res['os'])+'\n')
                    print("Ending_optimal_value:"+str(res['ofv']))
                    print("Partial optimal turn-setting:")
                    print(str(res['os']))
                    if popt:
                        llf.write("Partial actual iteration:"+str(res['itc'][0])+"\n")
                        llf.write("Partial total iteration:"+str(complete_comb(b_len,r))+"\n")
                        print("Partial actual iteration:"+str(res['itc'][0]))
                        print("Partial total iteration:"+str(complete_comb(b_len,r)))
                        res['itc'] = [0]
                        res['ofv'] = 0
                        res['os'] = 'No solution'
                    llf.flush()
                elif len(res['lp']) > 0:
                    for j in range(len(res['lp'])):
                        lpf.write(str(res['lp'][j])+'\n')
                    lpf.flush()

                # save checkpoint
                state_dict['i'] = i
                state_dict['ofv'] = res['ofv']
                state_dict['os'] = res['os']
                state_dict['itc'] = res['itc']
                torch.save(state_dict,arch_file)

            if is_opt and not popt:
                llf.write("\nActual iteration:"+str(res['itc'][0])+'\n')
                llf.flush()



def set_turns(G,bt,pt,start,end,index,**kwargs):
    '''
    This function tries to set prohibited turns for a given boundary router placement,
    which is proposed originally in the paper.
    However, this function is no longer allowed to be used in this project, because it 
    is no longer maintained and this may cause compatibility problems.

    Parameters
    ---------------------
    @ G         :target CDG

    @ kwargs

    w           :network width (int)
    h           :network height (int)
    r           :maximum recursion depth (int)
    brl:        :boundary router list (list)
    opt         :indicates whether at optimal mode, otherwise at list-all mode (bool)
    basis       :basis of progress (list)
    prog        :coefficient of progress (list)
    p_bar       :progress bar (tqdm)
    p_bar_len   :progress bar length (int)

    res         :result dict of the whole algorithm (dict)
        -lp     :list of all legal places (list) --only valid at list-all mode
        -ofv    :real-time-updated object function value (float) --only valid at optimal mode
        -os     :real-time-updated optimal solution (list) --only valid at optimal mode
    '''

    w = kwargs['w']
    h = kwargs['h']
    r = kwargs['r']
    brl = kwargs['brl']
    is_opt = kwargs['opt']
    basis = kwargs['basis']
    prog = kwargs['prog']
    p_bar = kwargs['p_bar']
    p_bar_len = kwargs['p_bar_len']
    res = kwargs['res']

    prog_sum = 1
    for i in range(r):
        prog_sum += basis[i] * prog[i]
    if prog_sum > p_bar_len:
        prog_sum = p_bar_len
    p_bar.n = prog_sum
    p_bar.refresh()

    cpt = deepcopy(pt)
    cdg = deepcopy(G)
    cdg.remove_edges_from(cpt)

    if not is_connected(cdg,w=w,h=h): #system not connected
        return 
    else:
        if is_opt:
            _cdg = copy.deepcopy(cdg)
            _cdg.remove_node('abstract_node')
            #now object function value 
            now_ofv = avg_bound_reach(_cdg,brl=brl,w=w,h=h)/ \
                        avg_bound_dist(cdg,w=w,h=h)
            if res['ofv'] >= now_ofv: #object function value not minimal
                return

        if not rw.find_cycle(G): #CDG no cycle
            if is_opt:
                res['ofv'] = now_ofv
                res['os'] = cpt
            else:
                res['lp'].append(cpt)
            return

        elif index == r or start > end:
            return
        
        for i in range(start,end+1):
            if i==start:
                cpt.append(bt[i])
            else:
                cpt[index] = bt[i]
            if i <= end:
                for m in range(r):
                    if index==m:
                        prog[m]=i

            set_turns(cdg,bt,cpt,i+1,end,index+1,**kwargs)



def set_turns_bkwd(G,bt,pt,start,end,index,**kwargs):
    '''
    This function tries to set prohibited turns for a given boundary router placement,
    by adopting our-proposed BAB-MDFA. However, this function doesn't implement BAB-MDFA itself,
    it just provided a "backward-searching" method for BAB-MDFA.
    Please make sure to always use this function to search in this project.

    Parameters
    ---------------------
    @ G         :target CDG

    @ kwargs

    arch        :architecture of the target network (str)
    w           :network width (int)
    h           :network height (int)
    d           :number of the dimension of the cube network (int)
    r           :maximum recursion depth (int)
    brl:        :boundary router list (list)
    opt         :indicates whether at optimal mode, otherwise at list-all mode (bool)
    basis       :basis of progress (list)
    prog        :coefficient of progress (list)
    p_bar       :progress bar (tqdm)
    b_len       :number of all candidate turns
    p_bar_len   :progress bar length (int)

    res         :result dict of the whole algorithm (dict)
        -lp     :list of all legal places (list) --only valid at list-all mode
        -ofv    :real-time-updated object function value (float) --only valid at optimal mode
        -os     :real-time-updated optimal solution (list) --only valid at optimal mode
        -itc    :latest-updated iteration count (list) --only valid at optimal mode
    '''

    arch = kwargs['arch']
    w = kwargs['w']
    h = kwargs['h']
    d = kwargs['d']
    r = kwargs['r']
    brl = kwargs['brl']
    is_opt = kwargs['opt']
    basis = kwargs['basis']
    prog = kwargs['prog']
    p_bar = kwargs['p_bar']
    b_len = kwargs['b_len']
    p_bar_len = kwargs['p_bar_len']
    res = kwargs['res']

    prog_sum = 1
    for i in range(r):
        prog_sum += basis[i] * prog[i]
    if prog_sum > p_bar_len:
        prog_sum = p_bar_len
    p_bar.n = prog_sum
    p_bar.refresh()

    cpt = deepcopy(pt)
    cdg = deepcopy(G)
    cdg.remove_edges_from(cpt)

    # for i in range(len(list(cdg.edges))):
    #     print(list(cdg.edges)[i])
    if not is_connected(cdg,arch=arch,w=w,h=h,d=d): #system not connected
        return 
    else:
        if is_opt:
            _cdg = copy.deepcopy(cdg)
            _cdg.remove_node('abstract_node')
            #now object function value 
            now_ofv = avg_bound_reach(_cdg,arch=arch,brl=brl,w=w,h=h,d=d)/ \
                        avg_bound_dist(cdg,arch=arch,w=w,h=h,d=d)
            if res['ofv'] >= now_ofv: #object function value not minimal
                return

        if not rw.find_cycle(cdg): #CDG no cycle
            if is_opt:
                res['ofv'] = now_ofv
                res['os'] = cpt
            else:
                _cdg = copy.deepcopy(cdg)
                _cdg.remove_node('abstract_node')
                #now object function value 
                ofv = avg_bound_reach(_cdg,arch=arch,brl=brl,w=w,h=h,d=d)/ \
                        avg_bound_dist(cdg,arch=arch,w=w,h=h,d=d)
                res['lp'].append((cpt,ofv,"_"))
            return

        elif index == r or start <= end:
            return
        
        for i in range(end,start):
            res['itc'][0] += 1
            real_i = start + end - i
            if i==end:
                cpt.append(bt[real_i-1])
            else:
                cpt[index] = bt[real_i-1]
            for m in range(r):
                if index==m:
                    prog[m]=b_len-real_i

            set_turns_bkwd(cdg,bt,cpt,b_len,real_i,index+1,**kwargs)