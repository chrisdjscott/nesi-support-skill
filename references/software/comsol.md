# COMSOL Multiphysics

Commercial finite-element multiphysics solver. Strong GUI, MATLAB LiveLink interface, and reasonable batch-cluster support.

## Loading

```bash
module spider COMSOL
module load COMSOL/<version>
comsol --help        # all batch flags
```

## Cluster-relevant flags

| Flag                    | Meaning                                                       |
| ----------------------- | ------------------------------------------------------------- |
| `-mpibootstrap slurm`   | Take MPI layout from Slurm                                    |
| `-np <cpus>`            | Threads per task (= `${SLURM_CPUS_PER_TASK}`)                 |
| `-nn <tasks>`           | Total tasks (= `${SLURM_NTASKS}`)                             |
| `-nnhost <tasks>`       | Tasks per node (= `${SLURM_NTASKS_PER_NODE}`)                 |
| `-inputfile <file.mph>` | Model file                                                    |

If you do not pass `--output`, COMSOL overwrites the input `.mph` with results.

## Serial

```sl
#!/bin/bash -e
#SBATCH --account  nesi99991
#SBATCH --job-name comsol-serial
#SBATCH --licenses comsol@uoa_foe
#SBATCH --time     00:30:00
#SBATCH --mem      2G

module load COMSOL/<version>
comsol batch -inputfile my_input.mph
```

## Shared memory

```sl
#SBATCH --cpus-per-task 8
#SBATCH --mem           4G

module load COMSOL/<version>
comsol batch -mpibootstrap slurm -inputfile my_input.mph
```

## Distributed memory

```sl
#SBATCH --ntasks      8
#SBATCH --mem-per-cpu 1500M

module load COMSOL/<version>
comsol batch -mpibootstrap slurm -inputfile my_input.mph
```

## Hybrid MPI + OpenMP

```sl
#SBATCH --ntasks        4
#SBATCH --cpus-per-task 16
#SBATCH --mem-per-cpu   1500M

module load COMSOL/<version>
comsol batch -mpibootstrap slurm -inputfile my_input.mph
```

## LiveLink with MATLAB

```sl
#SBATCH --cpus-per-task 16
#SBATCH --mem-per-cpu   1500M

module purge
module load COMSOL/<version>
module load MATLAB/2021b

comsol mphserver -silent &
matlab -batch "addpath('/opt/nesi/share/COMSOL/comsol154/multiphysics/mli/'); mphstart; MyScript"
```

## Gotchas

- Prefer `--cpus-per-task` over `--ntasks` for single-node runs; COMSOL is reasonably efficient with threads.
- SMT helps under ~8 CPUs only.
- "Disk quota exceeded" with plenty of space free is usually exhausted `TMPDIR`. Redirect it:

  ```bash
  export TMPDIR=/nesi/nobackup/nesi99991/comsoltmp
  export _JAVA_OPTIONS=-Djava.io.tmpdir=/nesi/nobackup/nesi99991/comsoltmp
  comsol --tmpdir /nesi/nobackup/nesi99991/comsoltmp ...
  ```

- For the GUI on the login node, set up X11 first (see `../access-and-login.md`). Large jobs must not run on the login node.

## Upstream

- <https://www.comsol.com/>
- Cluster KB: <https://www.comsol.com/support/knowledgebase/1001/>
