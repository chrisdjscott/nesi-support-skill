# ANSYS

Commercial multiphysics suite covering CFD (Fluent, CFX), structural mechanics (Mechanical APDL, LS-DYNA), electromagnetics (Electronics Desktop / HFSS), and ice accretion (FENSAP-ICE). Network-licensed; some tools have HPC-token requirements.

## Loading

```bash
module spider ANSYS
module load ANSYS/<version>
```

## Licensing

Three main licence types:

- **Teaching** (`aa_t`): default. Up to 6 CPUs, models under 512k nodes.
- **Research** (`aa_r`): no node restriction. Up to 16 CPUs free; each additional CPU requires an `aa_r_hpc` token.
- **HPC** (`aa_r_hpc`): one per CPU beyond 16 with a research licence.

Switch the licence preference with `prefer_research_license` or `prefer_teaching_license` (after `module load ANSYS`). Preferences are tracked per ANSYS version; use the version matching your job.

Enabling SMT (`--hint=multithread`) doubles `aa_r_hpc` token consumption.

## Journal files

ANSYS solvers consume a "journal" of commands. Generate one inline with a heredoc to support array jobs:

```bash
JOURNAL_FILE=fluent_${SLURM_JOB_ID}.in
cat <<EOF > ${JOURNAL_FILE}
/file/read-case-data case${SLURM_ARRAY_TASK_ID}.cas
/solve/dual-time-iterate 10
/file/write-case-data out${SLURM_ARRAY_TASK_ID}.cas
/exit yes
EOF
```

Always include `/exit yes`, otherwise Slurm marks the job FAILED.

## Fluent

Mandatory dimension/precision flag: `2d`, `3d`, `2ddp` (preferred), `3ddp` (preferred).

### Serial

```sl
#!/bin/bash -e
#SBATCH --account   nesi99991
#SBATCH --job-name  fluent-serial
#SBATCH --time      00:30:00
#SBATCH --mem       2G

module purge
module load ANSYS/<version>

fluent 3ddp -g -i wing.in
```

### Distributed memory (MPI)

```sl
#!/bin/bash -e
#SBATCH --account     nesi99991
#SBATCH --job-name    fluent-mpi
#SBATCH --time        02:00:00
#SBATCH --ntasks      16
#SBATCH --mem-per-cpu 1500M

module purge
module load ANSYS/<version>

fluent 3ddp -g -t ${SLURM_NTASKS} -i wing.in
```

### Checkpointing

```text
/file/autosave/data-frequency 500
(set! checkpoint/exit-filename "./exit-fluent")
```

`touch exit-fluent` makes Fluent save state and exit, writing `restart.inp` for resumption.

### UDFs

In the case setup choose "Compiled UDF" and use a *relative* path to the `.c` source. Load `foss` alongside the ANSYS module so the compiler is available. Force compile from the journal if necessary:

```text
define/user-defined/compiled-functions compile "libudf" yes "myUDF.c" "" ""
define/user-defined/compiled-functions load libudf
```

## CFX

```sl
#!/bin/bash -e
#SBATCH --account     nesi99991
#SBATCH --job-name    cfx
#SBATCH --time        01:00:00
#SBATCH --ntasks      16
#SBATCH --mem-per-cpu 1G

module purge
module load ANSYS/<version>

cfx5solve -batch -def pump.def -part ${SLURM_NTASKS}
```

CFX-Post needs an X server even when headless; wrap with `xvfb-run cfx5post input.cse` in batch jobs.

## Mechanical APDL

### Shared memory

```sl
#SBATCH --cpus-per-task 8
#SBATCH --mem           12G

module load ANSYS/<version>
mapdl -b -np ${SLURM_CPUS_PER_TASK} -i input.dat
```

### Distributed memory

```sl
#SBATCH --ntasks      16
#SBATCH --mem-per-cpu 1500M

module load ANSYS/<version>
mapdl -b -dis -np ${SLURM_NTASKS} -i input.dat
```

Not all MAPDL solvers support distributed memory. Sparse, PCG, PCG-Lanczos, Subspace, Unsymmetric, Damped eigensolvers, element formulation, and results calculation work; ICCG, JCG, QMR, Block-Lanczos, Supernode, QRDAMP, and pre/post-processing do not.

## LS-DYNA

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      lsdyna
#SBATCH --time          02:00:00
#SBATCH --cpus-per-task 16
#SBATCH --mem-per-cpu   1G

module purge
module load ANSYS/<version>

lsdyna i=myinput.k NCPUS=${SLURM_CPUS_PER_TASK} MEMORY2=1G
```

Useful flags: `-dp` (double precision), `MEMORY` (head node), `MEMORY2` (other nodes). Prefix `-` on `NCPUS=-64` for deterministic but slower runs. Keep large output on `/nesi/nobackup` (see `../filesystems.md`).

## FENSAP-ICE

MPI-capable solvers: FENSAP, DROP3D, ICE3D, C3D, OptiGrid. Available in ANSYS 19.2 only.

Two workflow options:

- **GUI**: launch `fensapiceGUI` with X11 forwarding, set `--job-name`, `--account`, `--mem-per-cpu`, `--time` under "Additional mpirun parameters". Run inside `tmux` so closing your SSH session does not interrupt the chain of steps.
- **fensap2slurm**: save the case (do not run), then `fensap2slurm path/to/project` generates one Slurm template per stage. Edit them, then `bash .solvercmd`.

## ANSYS Electronics Desktop (HFSS)

Requires RSM (remote solver manager) on each node. Use the wrapper `startRSM` after the Slurm allocation:

```sl
#!/bin/bash -e
#SBATCH --account         nesi99991
#SBATCH --job-name        edt
#SBATCH --time            04:00:00
#SBATCH --nodes           2
#SBATCH --ntasks-per-node 36
#SBATCH --mem-per-cpu     1500M

module load ANSYS/<version>
startRSM

ansysedt -ng -batchsolve -distributed -machinelistfile=".machinefile" \
    -batchoptions "HFSS/HPCLicenseType=Pool" Sim1.aedt
```

List options with `ansysedt -batchoptionhelp`. Each option needs its own `-batchoptions` flag.

## Multiphysics (MAPDL + Fluent + system coupler)

Run the system coupler, Mechanical and Fluent as three background `srun` invocations sharing a coupling server file. See the upstream ANSYS docs for the exact orchestration; the rough pattern:

```bash
COMP_CPUS=$((SLURM_NTASKS-1))
MECH=1
FLUID=$((COMP_CPUS-MECH))

srun -N1 -n1 $WORKBENCH_CMD ansys.services.systemcoupling.exe \
    -inputFile coupling.sci || scancel $SLURM_JOBID &
# wait for scServer.scs, parse port/node/solver names, then:
mapdl -b -dis -mpi intel -np $MECH -scport $port -schost $node \
    -scname "$mechsolname" -i structural.dat &
fluent 3ddp -g -t$FLUID -scport=$port -schost=$node \
    -scname="$fluentsolname" -i fluidFlow.jou &
wait
```

## Best practices

- GPUs help large jobs; small jobs are dominated by data-transfer overhead.
- Prefer batch journal files over interactive GUI sessions. If a GUI is needed for setup or post-processing, run it via `salloc` or on the login node and connect to a compute-node backend.
- Use `--cpus-per-task` over `--ntasks` for single-node Fluent/CFX/MAPDL when you can; it schedules faster.

## Upstream

- <https://www.ansys.com/>
- Fluent journal reference: <https://docs.hpc.shef.ac.uk/en/latest/referenceinfo/ANSYS/fluent/writing-fluent-journal-files.html>
