#ifndef _FTRA_H
#define _FTRA_H
#include <iostream>
#include <stdlib.h>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <vector>
#include <functional>
#include <queue>
using namespace std;

struct Edge{
    int sv,dv; 
    int next_edge; //index in vector
};

struct Vertex{
    int id;
    int first_edge = -1; //index in vector 
};

/*---------------------------graph.cpp-----------------------------*/
class Graph{ 
    public:
        int vnum;
        vector<struct Vertex> VertexSet;
        vector<struct Edge> EdgeSet;
        void addEdge(int sv,int dv);
        void rmvEdge(int sv,int dv);
        void addEdgesFrom(vector<int> &rt);
        void rmvEdgesFrom(vector<int> &pt);
        void printEdges();
        bool hasLoop(); //recommended only for testing if a construction is deadlock-free
        bool hasPath(int sv,int dv);

    protected:
        bool DFS(int tgt_vid,int now_vid,vector<bool> &visited); //find loop or find path
        void searchOut(int now_vid,vector<int> &dist,int depth);
        void searchIn(int now_vid,int dst_vid,vector<int> &dist,int depth);
};

/*---------------------------mesh_cdg.cpp-----------------------------*/
struct MeshCode{
    int x;
    int y;
    string chan;
};

class MeshCdg: public Graph{ 
    public:
        int W,H; //width and height of the mesh network
        vector<int> brl;
        MeshCdg(int w,int h);
        bool hasGLoop(); //recommended when running algorithm
        bool isConnected();
        int getBoundDist(bool dir,int rid); //dir: 0-inBound 1-outBound
        void setBoundRouters(vector<int> brl); //brl contains the indexes of routers, not vertexes
        void initBoundTurns(vector<int> &bt);
        int getAvgBoundDst(); //average boundary distance
        int getAvgBoundRch(); //average boundary reacheability
        void rmvBoundLinks(); //copy a CDG and remove all its boundary links before getAvgBoundRch
        void repBoundLinks(); //users are allowed to repare the boundary links after removing them
        int routeAtSrc(int srid,int drid);
        int routeAtDst(int srid,int drid);
        int encodeVid(int rid,int cid);
        void decodeVid(struct MeshCode &code,int vid);

    protected:
        void setOriginEdges();
};

/*---------------------------ftra.cpp-----------------------------*/
struct Results{
    double ofv=0; //object function value
    vector<int> os; //optimal solution
    unsigned long itc=0; //iteration count
};

void setTurns(MeshCdg G,vector<int> &bt,vector<int> pt,int start,int end,int index,int r,struct Results &res);
void setTurnsBkwd(MeshCdg G,vector<int> &bt,vector<int> pt,int start,int end,int index,int r,struct Results &res);
void setTurnsDirect(MeshCdg &G,vector<int> &brl,struct Results &res);

/*---------------------------utils.cpp-----------------------------*/
struct Grade{
    int sv;
    int dv;
    double ofv;
};

void getAllPlacements(vector<int> &input_set,vector<int> temp_comb,vector<vector<int>> &output_set,int start,int index,int r);
void sortAllTurns(MeshCdg &G,vector<int> &turns,bool dir,char off);
bool compare(struct Grade &a,struct Grade &b);
void seekToLine(ifstream &in, int line);
int getFileLen(ifstream &in);
bool isInVector(int a,vector<int> &v);
unsigned long getTimeData();

/*---------------------------run_mesh_st.cpp-----------------------------*/
void runMeshSingleThread(int mode,bool go,int w,int h,int n,int r);

/*---------------------------run_mesh_mt.cpp-----------------------------*/
void runMeshThread(int mode,int w,int h,int r,int idx,int ts);
void runMeshMultiThread(int mode,int w,int h,int n,int r,int tn);

/*---------------------------thread_pool.cpp-----------------------------*/
typedef function<void()> Task;

class ThreadPool{
    public:
        ThreadPool();
        ~ThreadPool();
        
    public:
        size_t initnum;
        vector<thread> threads;
        queue<Task> task;
        mutex _mutex;
        condition_variable cond;
        bool done ;
        bool isEmpty ;
        bool isFull;

    public:
        void addTask(const Task&f);
        void start(int num);
        void setSize(int num);
        void runTask();
        void finish();
};
#endif 