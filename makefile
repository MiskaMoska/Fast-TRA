COMPILER = g++ -Wall -pthread
OBJ_DIR = obj
SRC_DIR = srcs
HEADERS = ftra.h channel_name.h
RUN_MESH_ST_DEPEND = mesh_cdg.o ftra.o utils.o run_mesh_st.o graph.o
RUN_MESH_MT_DEPEND = mesh_cdg.o ftra.o utils.o run_mesh_mt.o graph.o thread_pool.o
vpath %.h $(SRC_DIR)

all : run_mesh_st run_mesh_mt 

run_mesh_st: $(addprefix $(OBJ_DIR)/, $(RUN_MESH_ST_DEPEND))
	$(COMPILER)  $^ -o $@

run_mesh_mt: $(addprefix $(OBJ_DIR)/, $(RUN_MESH_MT_DEPEND))
	$(COMPILER)  $^ -o $@

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp $(HEADERS)
	$(COMPILER) -c $< -o $@

clean:
	rm -f run_mesh_st run_mesh_mt $(OBJ_DIR)/*.o

cleancp:
	rm -f checkpoints/*
