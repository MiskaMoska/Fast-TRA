# Fast-TRA

## Overview
The modular turn restriction (MTR) methodology was proposed to achieve modular-deadlock-free for chiplet-based systems[1]. The turn restriction algorithm (TRA) is the core algorithm of MTR, which searches through all the boundary turn restriction combinations of the Network-on-Chip (NoC) on the target chiplet. Fast-TRA (FTRA) is proposed to accelerate the TRA by searching in a subspace of the solution space to reduce the time complexity by 2-4 degrees of magnitude and the optimal solution of FTRA is proved to acquire nearly equal performance to TRA. This project provides the algorithm code for TRA and FTRA.

## Branches
This project has 2 branches: cpp and python, each of which is implemented by the corresponding language. The cpp branch is created due to the extreme inefficiency of python, thus, we only need to focus on the cpp branch.

## Structure

+ **srcs** Source cpp codes for the TRA and FTRA algorithm.

+ **brp** Codes to generate the boundary router placements for the given network information.

+ **runcase** Defines some run cases based on the generated boudnary router placements.

+ **obj** Intermediate object files for compilation.

+ **output_*** Output log files for the algorithms.

+ **analysis** Scripts to perform analysis based on the output log files.

## How to Run

1. Run

   ```makefile
   make
   ```

   to generate the executable files, which are located at the project root directory.
2. Modify the `./brp/gen_plcmt.py` as you need and run

   ```shell
   python3 ./brp/gen_plcmt.py
   ```

   to generate to boundary router  placement files.

3. Create the runcase files in `./runcase`, please adopt the correct file name format according to `./srcs/run_mesh_st.cpp` and `./srcs/run_mesh_mt.cpp`.

4. List out the command in `./run.sh` to run the created cases.

5. Run

   ```bash
   source run.sh
   ```

     to launch the program.

## References

+ [1]J. Yin, Z. Lin, O. Kayiran, M. Poremba, M. S. B. Altaf, N. Enright Jerger, and G. H. Loh, “Modular routing design for chiplet-based systems,” in Proceedings of the International Symposium on Computer Architecture, 2018.  