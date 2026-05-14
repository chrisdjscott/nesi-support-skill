# CESM

Community Earth System Model (NCAR). Coupled atmosphere / ocean / land / sea-ice / land-ice / river-runoff climate model, with the CIME case-control system driving builds and runs.

Note: the upstream guide pre-dates the June 2025 migration. Treat the workflow below as a starting point and contact NeSI support for current paths.

## Prerequisites on Mahuika

```bash
module load git              # newer than system default
```

Wrap in a `SYSTEM_STRING` check in `~/.bashrc` if you also use Maui.

CESM components require Git LFS. Install locally:

```bash
wget https://github.com/git-lfs/git-lfs/releases/download/v3.5.1/git-lfs-linux-amd64-v3.5.1.tar.gz
tar xf git-lfs-linux-amd64-v3.5.1.tar.gz
cd git-lfs-3.5.1 && ./install.sh --local
export PATH=$HOME/.local/bin:$PATH
git lfs version
```

## Downloading CESM

```bash
export PROJECT_CODE=nesi99991
cd /nesi/project/${PROJECT_CODE}
git clone -b release-cesm2.1.5 https://github.com/ESCOMP/CESM.git my_cesm_sandbox
cd my_cesm_sandbox
./manage_externals/checkout_externals
```

Re-run `checkout_externals` if it fails on certificate prompts.

## NeSI CIME configuration

```bash
cd /nesi/project/${PROJECT_CODE}
git clone https://github.com/nesi/nesi-cesm-config.git
cd nesi-cesm-config
mkdir -p ~/.cime
sed "s/nesi99999/${PROJECT_CODE}/g" config_machines.xml > ~/.cime/config_machines.xml
cp config_batch.xml config_compilers.xml ~/.cime/
mkdir -p /nesi/nobackup/${PROJECT_CODE}/cesm/inputdata
```

Check the `DIN_LOC_ROOT` path in `~/.cime/config_machines.xml` exists. Share input data across users in a project rather than duplicating it; CESM input is large.

## Creating and running a test case

```bash
cd /nesi/project/${PROJECT_CODE}/my_cesm_sandbox/cime/scripts
./create_newcase \
    --case /nesi/nobackup/${PROJECT_CODE}/$USER/cesm/output/b.e20.B1850.f19_g17.test \
    --compset B1850 --res f19_g17 --machine mahuika --compiler gnu

cd /nesi/nobackup/${PROJECT_CODE}/$USER/cesm/output/b.e20.B1850.f19_g17.test

# Reduce default 6-node layout for a test (must be before case.setup)
./xmlchange MAX_TASKS_PER_NODE=32
./xmlchange MAX_MPITASKS_PER_NODE=32
./xmlchange --subgroup case.run JOB_WALLCLOCK_TIME="00:20:00"

./case.setup
./preview_run
./case.build              # downloads input data; can take a while
./xmlchange DOUT_S=FALSE  # disable short-term archiving
./case.submit
```

`./case.submit` puts the job in Slurm; monitor with `squeue --me`.

## Performance tuning

CESM PE-layout balancing between atmosphere, ocean, land, ice etc. has a large effect on throughput. The standard approach: short timing runs for each component, identify the bottleneck, redistribute MPI ranks. See <https://esmci.github.io/cime/versions/maint-5.6/html/users_guide/pes-threads.html>.

## Compiler choice

`--compiler gnu` vs `--compiler intel`: keep both case directories around for comparison; one can be 20-30% faster depending on the compset.

## Upstream

- <https://www.cesm.ucar.edu/>
- <https://escomp.github.io/CESM/release-cesm2/>
