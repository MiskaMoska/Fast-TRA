#include <iostream>
#include <vector>
#include <list>
#include <string>
#include <algorithm>
#include <fstream>
#include <stdio.h>
#include <mutex>
#include <thread>
#include <atomic>
#include <unistd.h>
#include <chrono>
using namespace std;

// int L=55;
int N=7;

void getAllPlacements(vector<int> &input_set,vector<int> temp_comb,
                        vector<vector<int>> &output_set,int start,int index,int r){
    if(index==r){
        // output_set.push_back(temp_comb);
        return;
    }
    if(start>int(input_set.size())-1) return;
    for(int i=start;i<int(input_set.size());i++){
        // if(i==start) temp_comb.push_back(input_set[i]);
        // else temp_comb[index] = input_set[i];
        getAllPlacements(input_set,temp_comb,output_set,i+1,index+1,r);
    }
}

void task(int L){
    vector<int> set;
    vector<int> comb;
    vector<vector<int>> res;
    for(int i=0;i<L;i++){
        set.push_back(i);
    }
    getAllPlacements(set,comb,res,0,0,N);

}
void work(int a,int b){
    for(int i=a;i<b;i++){
        sleep(0.1);
        cout << i << endl;
    }
}

//SetThreadAffinityMask
// int main(){
//     vector<thread> t_list;
//     auto tt0 = chrono::steady_clock::now();
//     for(int i=0;i<10;i++){
//         // thread temp(work,10*i,10*i+10);
//         t_list.emplace_back(task,4);
//     }
//     for(auto it=t_list.begin();it!=t_list.end();it++){
//         (*it).join();
//     }
//     cout << "all done" << endl;
//     auto tt1 = chrono::steady_clock::now();
//     cout << "elapsed time: " << chrono::duration_cast<std::chrono::milliseconds>(tt1-tt0).count() << "ms" << endl;
//     return 0;
// }

int main(){
    cout << thread::hardware_concurrency() << endl;
    return 0;
}

void seek_to_line(ifstream &in, int line){
    string str;
    // in.seekg(0, ios::beg);
    for(int i = 1; i < line; i ++){
        getline(in,str);
    }
}

int getFileLen(ifstream &in){
    string str;
    int i = 0;
    while(getline(in,str)) i++;
    return i;
}

// int main(){
//     string file_plc = "./brp/plcmt_2d_wh3_n3.txt";
//     ifstream fin;
//     fin.open(file_plc);
//     string s;
//     cout << getFileLen(fin) << endl;
// }


