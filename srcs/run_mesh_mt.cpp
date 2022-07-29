#include <iostream>
#include <string>
#include <vector>
#include <ctime>
#include <fstream>
#include <thread>
#include <mutex>
#include <atomic>
#include <unistd.h>
#include <chrono>
#include "channel_name.h"
#include "ftra.h"
#include <dirent.h>
using namespace std;

/* user defined hyper parameters begin */
int _W_ = 0;
int _H_ = 0;
int _N_ = 0;
int _R_ = 0;
int _MODE_ = 0;
bool _GO_ = 0; //NOTICE:global searching doesn't support checkpoint!!
int _TN_ = 1; //thread number
bool _RESUME_ = false; //load checkpiont and resume searching
/* user defined hyper parameters end */

vector<thread> thrd_list;
vector<int> now_state;
vector<vector<int>> all_placements;
string output_path,file_name,ckpt_name;
mutex fout_mtx;
ofstream fout,ckptout;
unsigned long start_time;
struct Results global_res;

void runMeshThread(int mode,int w,int h,int r,int idx,int ts){
    MeshCdg G(w,h);
    vector<int> brl;
    vector<int> bt,pt;
    struct Results res;
    struct MeshCode code;

    if(_GO_){
        res.ofv = global_res.ofv;
    }

    auto st = chrono::steady_clock::now();
    brl = all_placements[idx];
    G.setBoundRouters(brl);
    pt.clear();bt.clear();
    G.initBoundTurns(bt);
    if(mode & 32){
        setTurnsDirect(G,brl,res);
    }
    else{
        if(mode & 8){
            if(mode & 16) sortAllTurns(G,bt,mode & 4,mode & 3);
            setTurnsBkwd(G,bt,pt,(int)(bt.size()>>1),0,0,r,res);
        }
        else setTurns(G,bt,pt,0,(int)(bt.size()>>1)-1,0,r,res);
    }
    auto dt = chrono::steady_clock::now();

    //output data
    fout_mtx.lock();
    // cout << "ofv: " << res.ofv << endl;
    // cout << "itc: " << res.itc << endl;
    fout.width(20);fout << idx+1;
    fout.width(20);fout << res.ofv;
    fout.width(20);fout << res.itc;
    fout.width(20);fout << (_GO_ ? getTimeData() - start_time : chrono::duration_cast<chrono::milliseconds>(dt-st).count());
    for(unsigned int j=0;j<brl.size();j++){
        fout.width(20);
        fout << "(" + to_string(brl[j]%h) + "," + to_string(brl[j]/h)  + "),";
    }
    for(unsigned int j=0;j<(res.os.size()>>1);j++){
        G.decodeVid(code,res.os[j<<1]);
        fout << "(" + to_string(code.x) + "," + to_string(code.y) + "," + code.chan + ")-->";
        G.decodeVid(code,res.os[(j<<1)+1]);
        fout << "(" + to_string(code.x) + "," + to_string(code.y) + "," + code.chan + "),   ";
    }
    fout << endl;
    cout << idx+1 << "/" << ts << " done with ofv: " << res.ofv << endl;
    ckptout << to_string(idx) << endl;

    if(_GO_){
        global_res.ofv = res.ofv;
    }

    fout_mtx.unlock();
}

/*----------------------------------------------------------------------------------
    mode:the searching method
        0   :forward searching without presorting
        8   :backward searching without presorting
        25  :backward searching with forward 1/AD presorting
        26  :backward searching with forward AR/1 presorting
        27  :backward searching with forward AR/AD presorting
        29  :backward searching with backward 1/AD presorting
        30  :backward searching with backward AR/1 presorting
        31  :backward searching with backward AR/AD presorting
        32  :Direct-TRA method

    w:network width
    h:network height
    n:number of boundary routers
    r:maximum turn restriction number
    tn:thread number
----------------------------------------------------------------------------------*/
void runMeshMultiThread(int mode,int w,int h,int n,int r,int tn){
    string plc_file = "./brp/plcmt_2d_wh" + to_string(_W_) + "_n" + to_string(_N_) + ".txt";
    cout << plc_file << endl;
    int cnt = 0;
    int ts; //total_size for all thread

    ifstream fin,ckptin;
    string tstr;
    vector<int> plc;
    fout.setf(std::ios::left);
    fout.open(file_name,_RESUME_ ? ios::app : ios::out);

    ThreadPool pool;

    //output table header
    fout.width(20);fout << "idx";
    fout.width(20);fout << "ofv";
    fout.width(20);fout << "itc";
    fout.width(20);fout << "time";
    fout.width(n*20);fout << "brl";
    fout << "pt"; //variable length
    fout << endl;

    fin.open(plc_file);
    while(getline(fin,tstr)){
        cnt ++;
        plc.push_back(atoi(tstr.c_str()));
        if(!(cnt % _N_)){
            all_placements.push_back(plc);
            plc.clear();
        }
    }
    fin.close();
    ts = all_placements.size();

    //resume control begin
    if(_RESUME_){
        ckptin.open(ckpt_name);
        while(getline(ckptin,tstr)){
            now_state.push_back(atoi(tstr.c_str()));
        }
        ckptin.close();
    }
    ckptout.open(ckpt_name,_RESUME_ ? ios::app : ios::out);
    //resume control end

    pool.start(_TN_);
    auto st = chrono::steady_clock::now();
    for(int idx=0;idx<ts;idx++){
        if(!isInVector(idx,now_state)){
            auto task = bind(runMeshThread,mode,w,h,r,idx,ts);
            pool.addTask(task);
        }
    }
    pool.finish();
    auto dt = chrono::steady_clock::now();
    cout << "elapsed time: " << chrono::duration_cast<chrono::milliseconds>(dt-st).count() << "ms" << endl;
    fout << "elapsed time: " << chrono::duration_cast<chrono::milliseconds>(dt-st).count() << "ms" <<endl;
    cout << "all done" << endl;

    //resume control begin
    ckptout.flush();
    ckptout.close();
    //resume control end

    fout.flush();
    fout.close();
}

int main(){
    cin >> _W_;
    cin >> _H_;
    cin >> _N_;
    cin >> _R_;
    cin >> _MODE_;
    cin >> _GO_;
    cin >> _TN_;
    cin >> _RESUME_;

    start_time = getTimeData();
    // cout << start_time << endl;
    output_path = "./output_mesh_w" + to_string(_W_) + "_h" + 
                            to_string(_H_) + "_n" + to_string(_N_);
    file_name = output_path + "/mt_go" + to_string(_GO_) + "_mode" + to_string(_MODE_) + "_r" + to_string(_R_) + ".txt";
    ckpt_name = "./checkpoints/mesh_go" + to_string(_GO_) + "_w" + to_string(_W_) + "_h" + to_string(_H_) + "_n" + to_string(_N_) +
                    "_mode" + to_string(_MODE_) + "_r" + to_string(_R_) + ".txt";

    system(("mkdir -p " + output_path).c_str());
    system(("cd "+ output_path).c_str());
    runMeshMultiThread(_MODE_,_W_,_H_,_N_,_R_,_TN_);
    return 0;
}