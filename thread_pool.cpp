#include <iostream>
#include <stdlib.h>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <vector>
#include <functional>
#include <queue>
#include "ftra.h"
using namespace std;

ThreadPool ::ThreadPool():done(false),isEmpty(true),isFull(false){
}

void ThreadPool::setSize(int num){
        (*this).initnum = num ;
}

void ThreadPool::addTask(const Task&f){
    if(!done){ 
        unique_lock<mutex> lk(_mutex);
        
        while(isFull){
            cond.wait(lk);
        }

        task.push(f);
        if(task.size()==initnum)
            isFull = true;
        isEmpty = false ;
        cond.notify_one();
    }
}

void ThreadPool::finish(){
        done = true;
        for(size_t i=0;i<threads.size();i++){
            threads[i].join();
        }
}

void ThreadPool::runTask(){
    while(true){
        unique_lock<mutex> lk(_mutex);
        
        while(isEmpty){
            cond.wait(lk);
        }
        
        Task ta ;
        ta = move(task.front());  
        task.pop();
        
        if(task.empty()){
            isEmpty = true;    
        }    
        
        isFull =false ;
        lk.unlock();
        ta();
        lk.lock();
        if(isEmpty && done){
            break;
        }
        cond.notify_one();
    }
}

void ThreadPool::start(int num){
    
    setSize(num);
    
    for(int i=0;i<num;i++){        
        threads.push_back(thread(&ThreadPool::runTask,this));
    }
}

ThreadPool::~ThreadPool(){   
}

