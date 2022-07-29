#include <iostream>
#include <string>
#include <vector>
#include <ctime>
#include "channel_name.h"
#include "ftra.h"
using namespace std;

void Graph::addEdge(int sv,int dv){
    struct Edge temp_edge;
    temp_edge.sv = sv;
    temp_edge.dv = dv;
    temp_edge.next_edge = this->VertexSet[sv].first_edge;
    this->EdgeSet.push_back(temp_edge);
    this->VertexSet[sv].first_edge = this->EdgeSet.size()-1;
    // cout << "added an edge" << endl;
}

void Graph::rmvEdge(int sv,int dv){
    int last_eid;
    int now_eid;
    now_eid = this->VertexSet[sv].first_edge;
    if(this->EdgeSet[now_eid].dv==dv){
        this->VertexSet[sv].first_edge = this->EdgeSet[now_eid].next_edge;
        // cout << "removed edge (" << sv << "," << dv << ")" << endl;
        return;
    }
    while(this->EdgeSet[now_eid].dv!=dv){
        if(this->EdgeSet[now_eid].next_edge==-1){
            // cout << "rmvEdge failed:cannot find object edge: (" << sv << "," << dv << ")" << endl;
            return;
        }
        last_eid = now_eid;
        now_eid = this->EdgeSet[last_eid].next_edge;
    }
    this->EdgeSet[last_eid].next_edge=this->EdgeSet[now_eid].next_edge;
    // cout << "removed edge (" << sv << "," << dv << ")" << endl;
}

void Graph::addEdgesFrom(vector<int> &rt){
    for(unsigned int i=0;i<(rt.size()>>1);i++){
        this->addEdge(rt[i<<1],rt[(i<<1)+1]);
    }
}

void Graph::rmvEdgesFrom(vector<int> &pt){
    for(unsigned int i=0;i<(pt.size()>>1);i++){
        this->rmvEdge(pt[i<<1],pt[(i<<1)+1]);
    }
}

void Graph::printEdges(){
    int eid;
    cout << "printEdges" << endl;
    for(int i=0;i<this->vnum;i++){
        eid = this->VertexSet[i].first_edge;
        if(eid==-1) continue;
        while(this->EdgeSet[eid].next_edge!=-1){
            cout << '(' << i << ',' << EdgeSet[eid].dv << ')' << endl;
            eid = EdgeSet[eid].next_edge;
        }
        cout << '(' << i << ',' << EdgeSet[eid].dv << ')' << endl;
    }
}

bool Graph::hasLoop(){
    vector<bool> visited(this->vnum);
    for(int i=0;i<this->vnum;i++){
        if(this->VertexSet[i].first_edge==-1) continue;
        visited = vector<bool>(this->vnum,false);
        if(this->DFS(i,i,visited)){
            return true; // if find loop, stop searching
        }
    } 
    return false;
}

bool Graph::hasPath(int sv,int dv){
    vector<bool> visited(this->vnum);
    return this->DFS(dv,sv,visited);
}

bool Graph::DFS(int tgt_vid,int now_vid,vector<bool> &visited){
    //this function searches a loop/path from a given vertex(now_id)
    //to find a loop, set tgt_vid as the source vertex
    //to find a path, set tgt_vid as the destination vertex
    struct Edge edge;
    int eid;
    visited[now_vid] = true;
    // cout << now_vid << endl;
    eid = this->VertexSet[now_vid].first_edge;
    while(eid!=-1){
        edge = this->EdgeSet[eid];
        if(edge.dv==tgt_vid){ 
            return true; // if find loop/path, stop searching
        }
        if(!visited[edge.dv]){ //not visited
            if(this->DFS(tgt_vid,edge.dv,visited)) 
                return 1; // if find loop/path, stop searching
        }
        eid = edge.next_edge;
    }
    return false;
}

void Graph::searchOut(int now_vid,vector<int> &dist,int depth){
    int eid;
    struct Edge edge;
    eid = this->VertexSet[now_vid].first_edge;
    while(eid!=-1){
        edge = this->EdgeSet[eid];
        if(edge.dv==this->vnum-1){ //the abstract node
            dist.push_back(depth);
            return;
        }
        this->searchOut(edge.dv,dist,depth+1);
        eid = edge.next_edge;
    }
}

void Graph::searchIn(int now_vid,int dst_vid,vector<int> &dist,int depth){
    int eid;
    struct Edge edge;
    eid = this->VertexSet[now_vid].first_edge;
    while(eid!=-1){
        edge = this->EdgeSet[eid];
        if(edge.dv==this->vnum-1){ //the abstract node
            return;
        }
        if(edge.dv==dst_vid){
            dist.push_back(depth); //the destination node
            return;
        }
        this->searchIn(edge.dv,dst_vid,dist,depth+1);
        eid = edge.next_edge;
    }
}
