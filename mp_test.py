from tqdm import tqdm
import time
import os
import numpy
import multiprocessing as mp
import keyboard

# file_path = './mt_test_log'
# is_exit = False

def count(num,lock,kwargs):
    fp=kwargs['fp']
    kwargs['list'].append(num)
    tb = tqdm(total=num)
    for i in range(num):
        time.sleep(0.1)
        tb.update(1)
    tb.close()
    lock.acquire()
    with open(fp,'a') as lf:
        lf.write(str(num)+' done\n')
        lf.flush()
    lock.release()

if __name__ == "__main__":
    file_path = 'log_file'
    pool = mp.Pool(processes=20)
    lock = mp.Manager().Lock()
    kwargs = mp.Manager().dict()
    kwargs['fp']=file_path
    kwargs['list'] = []
    for i in range(100,200):
        pool.apply_async(count, (i,lock,kwargs))

    while True:
        if keyboard.is_pressed('w'):
            pool.terminate()
            print('sasasa',kwargs['list'])
            break

    pool.close()
    pool.join()
