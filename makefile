COMPILER = g++ -Wall -pthread
HEADERS = ftra.h channel_name.h
OBJ_DIR = obj

all : run_mesh_st run_mesh_mt

run_mesh_st: $(OBJ_DIR)/mesh_cdg.o $(OBJ_DIR)/ftra.o $(OBJ_DIR)/utils.o $(OBJ_DIR)/run_mesh_st.o $(OBJ_DIR)/graph.o
	$(COMPILER)  $^ -o $@

run_mesh_mt: $(OBJ_DIR)/mesh_cdg.o $(OBJ_DIR)/ftra.o $(OBJ_DIR)/utils.o $(OBJ_DIR)/run_mesh_mt.o $(OBJ_DIR)/graph.o $(OBJ_DIR)/thread_pool.o
	$(COMPILER)  $^ -o $@

$(OBJ_DIR)/%.o: %.cpp $(HEADERS)
	$(COMPILER) -c $< -o $@

clean:
	-rm -f run_mesh_st run_mesh_mt $(OBJ_DIR)/*
