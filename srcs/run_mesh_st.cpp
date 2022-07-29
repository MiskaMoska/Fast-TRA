#include <iostream>
#include <string>
#include <vector>
#include <ctime>
#include <fstream>
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
bool _GO_ = false;
/* user defined hyper parameters end */

vector<vector<int>> all_placements;
string output_path,file_name;
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

    go:global optimization
        true:global optimal value marking
        false:partitional optimal value marking

    w:network width
    h:network height
    n:number of boundary routers
    r:maximum turn restriction number
----------------------------------------------------------------------------------*/
void runMeshSingleThread(int mode,bool go,int w,int h,int n,int r){
    string plc_file = "./brp/plcmt_2d_wh" + to_string(_W_) + "_n" + to_string(_N_) + ".txt";
    ifstream fin;
    string ts;
    ofstream fout;
    double st,dt,gst,gdt;
    fout.setf(std::ios::left);
    MeshCdg init_G(w,h),G(w,h);
    vector<int> bt,pt;
    vector<int> brl;
    vector<int> plc;
    struct Results res;
    struct MeshCode code;
    fout.open(file_name);
    fin.open(plc_file);
    int cnt = 0;
    while(getline(fin,ts)){
        cnt ++;
        plc.push_back(atoi(ts.c_str()));
        if(!(cnt % _N_)){
            all_placements.push_back(plc);
            plc.clear();
        }
    }
    fin.close();
    cout << "read " << all_placements.size() << " placements." << endl;
    gst = clock();

    //output table header
    fout.width(20);fout << "idx";
    fout.width(20);fout << "ofv";
    fout.width(20);fout << "itc";
    fout.width(20);fout << "time";
    fout.width(n*20);fout << "brl";
    fout << "pt"; //variable length
    fout << endl;

    for(auto it=all_placements.begin();it!=all_placements.end();it++){
        static int i=0;
        i++;
        G = init_G;
        cout << "-----------------------------------------------------" 
                << i << "/" << all_placements.size() << endl;
        st = clock();
        brl = *it;
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
        dt = clock();

        //output data
        cout << "ofv: " << res.ofv << endl;
        cout << "itc: " << res.itc << endl;
        fout.width(20);fout << i;
        fout.width(20);fout << res.ofv;
        fout.width(20);fout << res.itc;
        fout.width(20);fout << (dt-st)*1000/CLOCKS_PER_SEC;
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

        //whether to clear results
        if(!go){
            res.ofv = 0; res.itc = 0; res.os.clear();
        }
    }
    gdt = clock();
    cout << "elapsed time: " << (gdt-gst)*1000/CLOCKS_PER_SEC << "ms" << endl;
    fout << "elapsed time: " << (gdt-gst)*1000/CLOCKS_PER_SEC << "ms" <<endl;
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
    output_path = "./output_mesh_w" + to_string(_W_) + "_h" + 
                            to_string(_H_) + "_n" + to_string(_N_);
    file_name = output_path + "/st_go" + to_string(_GO_) + "_mode" + to_string(_MODE_) + "_r" + to_string(_R_) + ".txt";
    
    system(("mkdir -p " + output_path).c_str());
    system(("cd "+ output_path).c_str());
    runMeshSingleThread(_MODE_,_GO_,_W_,_H_,_N_,_R_);
    return 0;
}
