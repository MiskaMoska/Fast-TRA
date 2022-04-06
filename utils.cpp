#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <ctime>
#include <algorithm>
#include "channel_name.h"
#include "ftra.h"
using namespace std;

void getAllPlacements(vector<int> &input_set,vector<int> temp_comb,
                        vector<vector<int>> &output_set,int start,int index,int r){
    if(index==r){
        output_set.push_back(temp_comb);
        return;
    }
    if(start>int(input_set.size())-1) return;
    for(int i=start;i<int(input_set.size());i++){
        if(i==start) temp_comb.push_back(input_set[i]);
        else temp_comb[index] = input_set[i];
        getAllPlacements(input_set,temp_comb,output_set,i+1,index+1,r);
    }
}

/*----------------------------------------------------------------------------------
    dir:sorting direction
        true:fake ftra
        false:real ftra

    off:object function form
        1:1/AD
        2:AR/1
        3:AR/AD
----------------------------------------------------------------------------------*/
void sortAllTurns(MeshCdg &G,vector<int> &turns,bool dir,char off){ 
    auto cdg = G;
    vector<struct Grade> _turns;
    struct Grade a_turn;
    double ofv;
    int ar = 1;
    int ad = 1;
    for(unsigned int i=0;i<(turns.size()>>1);i++){
        cdg = G;
        cdg.rmvEdge(turns[i<<1],turns[(i<<1)+1]);

        if(off & 1){
            ad = cdg.getAvgBoundDst();
        }

        if(off & 2){
            cdg.rmvBoundLinks();
            ar = cdg.getAvgBoundRch();
        }
        
        ofv = (double)ar/(double)ad;
        a_turn.sv = turns[i<<1];
        a_turn.dv = turns[(i<<1)+1];
        if(dir) ofv = -ofv;
        a_turn.ofv = ofv;
        _turns.push_back(a_turn);
    }
    sort(_turns.begin(),_turns.end(),compare);

    for(unsigned int i=0;i<_turns.size();i++){
        turns[i<<1] = _turns[i].sv;
        turns[(i<<1)+1] = _turns[i].dv;
    }
}

bool compare(struct Grade &a,struct Grade &b){
    return a.ofv < b.ofv;
}

void seekToLine(ifstream &in, int line){
    string str;
    for(int i = 0; i < line; i ++){
        getline(in,str);
    }
}

int getFileLen(ifstream &in){
    string str;
    int i = 0;
    while(getline(in,str)) i++;
    return i;
}

bool isInVector(int a,vector<int> &v){
    for(auto it=v.begin();it!=v.end();it++){
        if(*it==a) return true;
    }
    return false;
}