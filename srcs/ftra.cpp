#include <iostream>
#include <string>
#include <vector>
#include <ctime>
#include "channel_name.h"
#include "ftra.h"
using namespace std;

void setTurns(MeshCdg G,vector<int> &bt,vector<int> pt,int start,int end,int index,int r,struct Results &res){
    double now_ofv,ad;
    G.rmvEdgesFrom(pt);
    if(!G.isConnected()) return;

    ad = (double)(G.getAvgBoundDst());
    G.rmvBoundLinks();
    now_ofv = (double)(G.getAvgBoundRch())/ad;
    G.repBoundLinks();
    if(res.ofv >= now_ofv) return;

    if(!G.hasGLoop()){
        res.ofv = now_ofv;
        res.os = pt;
        return;
    }
    if(index == r || start > end) return;
    for(int i=start;i<=end;i++){
        res.itc ++;
        if(i==start){
            pt.push_back(bt[i<<1]);
            pt.push_back(bt[(i<<1)+1]);
        }
        else{
            pt[index<<1]=bt[i<<1];
            pt[(index<<1)+1]=bt[(i<<1)+1];
        }
        setTurns(G,bt,pt,i+1,end,index+1,r,res);
    }
}


void setTurnsBkwd(MeshCdg G,vector<int> &bt,vector<int> pt,int start,int end,int index,int r,struct Results &res){
    double now_ofv,ad;
    int real_i;

    G.rmvEdgesFrom(pt);
    if(!G.isConnected()) return;

    ad = (double)(G.getAvgBoundDst());
    G.rmvBoundLinks();
    now_ofv = (double)(G.getAvgBoundRch())/ad; 
    G.repBoundLinks();
    if(res.ofv >= now_ofv) return;

    if(!G.hasGLoop()){
        res.ofv = now_ofv;
        res.os = pt;
        return;
    }
    if(index == r || start <= end) return;
    for(int i=end;i<start;i++){
        res.itc ++;
        real_i = start + end - i;
        if(i==end){
            pt.push_back(bt[(real_i-1)<<1]);
            pt.push_back(bt[((real_i-1)<<1)+1]);
        }
        else{
            pt[index<<1]=bt[(real_i-1)<<1];
            pt[(index<<1)+1]=bt[((real_i-1)<<1)+1];
        }
        setTurnsBkwd(G,bt,pt,start,real_i,index+1,r,res);
    }
}

void setTurnsDirect(MeshCdg &G,vector<int> &brl,struct Results &res){
    int sv,dv;
    bool flag;
    auto cdg = G;
    double now_ofv,ad;
    struct MeshCode code;
    vector<int> pt;
    for(auto free_bnd=brl.begin();free_bnd!=brl.end();free_bnd++){
        // cout << "choose free-bound:" << *free_bnd << endl;
        cdg = G;
        flag = true;
        pt.clear();
        for(auto obj_bnd=brl.begin();obj_bnd!=brl.end();obj_bnd++){
            if(*obj_bnd == *free_bnd) continue;
            res.itc ++;
            sv = cdg.encodeVid(*obj_bnd,MS_BOUND_I); //!for mesh
            dv = cdg.encodeVid(*obj_bnd,cdg.routeAtSrc(*obj_bnd,*free_bnd));
            cdg.rmvEdge(sv,dv);pt.push_back(sv);pt.push_back(dv);

            // //print begin
            // cdg.decodeVid(code,sv);
            // cout << "(" << code.x << "," << code.y << "," << code.chan << ")-->";
            // cdg.decodeVid(code,dv);
            // cout << "(" << code.x << "," << code.y << "," << code.chan << ")" << endl;
            // //print end

            sv = cdg.encodeVid(*obj_bnd,cdg.routeAtDst(*free_bnd,*obj_bnd));
            dv = cdg.encodeVid(*obj_bnd,MS_BOUND_O); //!for mesh
            cdg.rmvEdge(sv,dv);pt.push_back(sv);pt.push_back(dv);

            // //print begin
            // cdg.decodeVid(code,sv);
            // cout << "(" << code.x << "," << code.y << "," << code.chan << ")-->";
            // cdg.decodeVid(code,dv);
            // cout << "(" << code.x << "," << code.y << "," << code.chan << ")" << endl;
            // //print end

            ad = (double)(cdg.getAvgBoundDst());
            cdg.rmvBoundLinks();
            now_ofv = (double)(cdg.getAvgBoundRch())/ad; 
            cdg.repBoundLinks();
            if(res.ofv >= now_ofv){
                flag = false;
                break;
            }
        }
        if(!cdg.hasGLoop() && flag){
            // cout << "find a solution" << endl;
            res.ofv = now_ofv;
            res.os = pt;
        }
    }
}