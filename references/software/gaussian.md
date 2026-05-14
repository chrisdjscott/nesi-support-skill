# Gaussian

Commercial electronic structure suite (`g09`, `g16`) for energies, geometries, vibrational frequencies and molecular properties.

## Licence

Closed-source, restricted access. Members of NeSI's Gaussian UNIX group can run it. University of Auckland staff and students are added automatically. Others must request access via NeSI support and demonstrate a valid institutional licence permitting cluster use.

## Loading

```bash
module spider Gaussian
module load Gaussian/09-D.01            # example
```

## Input file requirements

- Every Gaussian input must end with a blank line.
- Set `%Chk=...` for checkpoint files (enables restart).
- `%CPU` in the input must match Slurm's allocated CPUs (use `taskset` to discover them).
- `%Mem` (MB) should be roughly `--mem` minus 2 GB for Gaussian's overhead.

## Shared memory (single node)

Gaussian uses two threads per CPU, so set `%CPU` to the actual core list reported by `taskset`.

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      gaussian-smp
#SBATCH --time          00:15:00
#SBATCH --cpus-per-task 8
#SBATCH --mem           8G

module purge
module load Gaussian/<version>

INPUT_FILE="H2O.gjf"
GAUSSIAN_MEM=$((${SLURM_MEM_PER_NODE} - 2048))

export GAUSS_SCRDIR="/nesi/nobackup/${SLURM_JOB_ACCOUNT}/gaussian_job_${SLURM_JOB_ID}"
mkdir -p "${GAUSS_SCRDIR}"

cat << EOF > "$INPUT_FILE"

%CPU=$(taskset -cp $$ | awk -F':' '{print $2}')
%Mem=${GAUSSIAN_MEM}MB
%Chk=${INPUT_FILE}.chk

# HF/6-31G(d) Opt=ModRedun Test

water geo optimisation HF/6-31G(d)

0 1
H
O 1 0.95
H 2 0.95 1 109.0


EOF

srun g09 < "${INPUT_FILE}"
```

## Distributed memory (Linda, multi-node)

```sl
#!/bin/bash -e
#SBATCH --account         nesi99991
#SBATCH --job-name        gaussian-linda
#SBATCH --time            00:15:00
#SBATCH --nodes           2
#SBATCH --ntasks-per-node 4
#SBATCH --mem             4G

module purge
module load Gaussian/<version>

INPUT_FILE="H2O.gjf"
GAUSSIAN_MEM=$((${SLURM_MEM_PER_NODE} - 2048))

export GAUSS_SCRDIR="/nesi/nobackup/${SLURM_JOB_ACCOUNT}/gaussian_job_${SLURM_JOB_ID}"
mkdir -p "${GAUSS_SCRDIR}"

cat << EOF > "$INPUT_FILE"

%LindaWorkers=$(for n in $(srun hostname | sort -u); do printf "${n}:${SLURM_NPROCS},"; done)
%Mem=${GAUSSIAN_MEM}MB
%Chk=${INPUT_FILE}.chk

# HF/6-31G(d) Opt=ModRedun Test

water geo optimisation HF/6-31G(d)

0 1
H
O 1 0.95
H 2 0.95 1 109.0


EOF

srun g09 < "${INPUT_FILE}"
```

## Scratch directory

Always set `GAUSS_SCRDIR` (e.g. under `/nesi/nobackup/...`); Gaussian writes large `*.rwf`, `*.int`, `*.d2e`, `*.scr` files. See `../filesystems.md`.

## Upstream

- <https://gaussian.com/>
