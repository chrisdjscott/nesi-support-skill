# WRF

Weather Research and Forecasting Model. Mesoscale numerical weather prediction, MPI-parallel. No NeSI-maintained module on current Mahuika; build it yourself against the system netCDF stack.

## Building WRF

```bash
#!/bin/bash
module purge
module load netCDF-Fortran/4.6.1-gompi-2023a

# silence GCC 10+ strictness needed by WRF Fortran
export fallow_argument=-fallow-argument-mismatch
export boz_argument=-fallow-invalid-boz
export FFLAGS="$fallow_argument $boz_argument -m64"
export FCFLAGS="$fallow_argument $boz_argument -m64"
export CC=gcc
export CXX=gcc
export MPICC=mpicc
export MPICXX=mpicxx
export NETCDF=$EBROOTNETCDFMINFORTRAN

git clone --recurse-submodule https://github.com/wrf-model/WRF.git --depth 1 --branch v4.6.0
cd WRF
./configure        # choose option 34: dmpar gfortran/gcc (GNU)
export J="-j 12"
./compile em_real >& wrf_build.log
```

Compilation takes around 30 minutes. Run from `tmux` (see `../access-and-login.md`) so SSH drops do not interrupt it. Inspect `wrf_build.log` for errors and warnings.

## Running WRF

```sl
#!/bin/bash -e
#SBATCH --account  nesi99991
#SBATCH --job-name wrf
#SBATCH --time     01:00:00
#SBATCH --ntasks   36

module purge
module load netCDF-Fortran/4.6.1-gompi-2023a

srun --kill-on-bad-exit --output=real.log ./real.exe
srun --kill-on-bad-exit --output=wrf.log  ./wrf.exe
```

`--kill-on-bad-exit` ensures the whole job aborts on a single rank's failure. Without it WRF often keeps the allocation alive doing nothing until wall time expires.

## Building WPS

```bash
#!/bin/bash
wget https://github.com/wrf-model/WPS/archive/refs/tags/v4.6.0.tar.gz
tar xf v4.6.0.tar.gz
cd WPS-4.6.0

module purge
module load netCDF-Fortran/4.6.1-gompi-2023a
module load JasPer/2.0.33-GCC-12.3.0

export NETCDF=$EBROOTNETCDFMINFORTRAN
export NETCDFF=$EBROOTNETCDFMINFORTRAN
export HDF5=$EBROOTHDF5
export JASPERLIB=$EBROOTJASPER/lib64/libjasper.so
export JASPERINC=$EBROOTJASPER/include/jasper/jasper.h
export WRF_DIR=/path/to/WRF      # absolute path to WRF build

./clean > /dev/null 2>&1
./configure        # option 1 (serial) or option 3 (dmpar) gfortran
./compile >& WPS_build.log
```

## Running WPS

Most WPS tools (`geogrid.exe`, `ungrib.exe`, `metgrid.exe`) are cheap enough to run on the login node, provided netCDF and JasPer modules are loaded. For longer or memory-heavy preprocessing:

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      wps
#SBATCH --time          01:00:00
#SBATCH --cpus-per-task 1

module purge
module load netCDF-Fortran/4.6.1-gompi-2023a
module load JasPer/2.0.33-GCC-12.3.0
export WRF_DIR=/path/to/WRF

./geogrid.exe
```

## Upstream

- <https://www.mmm.ucar.edu/models/wrf>
- <https://github.com/wrf-model/WRF>
- <https://github.com/wrf-model/WPS>
