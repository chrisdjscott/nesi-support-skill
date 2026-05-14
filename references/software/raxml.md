# RAxML

Maximum-likelihood inference of phylogenetic trees. GPL v2+.

## Loading

```bash
module spider RAxML
module load RAxML/8.2.12-gimkl-2020a       # example
```

Each module ships several binaries:

- `raxmlHPC-AVX`, `raxmlHPC-SSE3`: serial.
- `raxmlHPC-PTHREADS-AVX`, `raxmlHPC-PTHREADS-SSE3`: shared-memory threaded.
- `raxmlHPC-MPI-AVX`, `raxmlHPC-MPI-SSE3`: distributed-memory MPI (bootstrapped trees only).
- `raxmlHPC-HYBRID-AVX`, `raxmlHPC-HYBRID-SSE3`: MPI + threads (bootstrapped trees only).

AVX is 10-30% faster than SSE3. Prefer AVX unless it fails.

## PTHREADS (single node, multi-threaded)

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      raxml
#SBATCH --time          01:00:00
#SBATCH --ntasks        1
#SBATCH --cpus-per-task 4
#SBATCH --mem           2G

module purge
module load RAxML/<version>

srun raxmlHPC-PTHREADS-AVX -T ${SLURM_CPUS_PER_TASK} \
    -m GTRCAT -s aln.fasta -n tree.out
```

For PTHREADS and HYBRID builds, always pass `-T ${SLURM_CPUS_PER_TASK}`.

## Slurm/binary pairing

- Serial binary: `--ntasks=1`, `--cpus-per-task=1`.
- PTHREADS: `--ntasks=1`, `--cpus-per-task=N`.
- MPI: `--ntasks=N`, `--cpus-per-task=1`.
- HYBRID: `--ntasks=N`, `--cpus-per-task=M`.

## Upstream

- <https://github.com/stamatak/standard-RAxML>
- `raxmlHPC-AVX -help`
