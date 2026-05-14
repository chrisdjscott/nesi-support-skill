# MAKER

Genome annotation pipeline.

## Loading

```bash
module spider MAKER
module load MAKER/2.31.9-gimkl-2020a       # example
```

## Local patch

NeSI's MAKER build makes `maker_exe.ctl` optional. If absent, defaults are used directly.

## Parallelism (single-node MPI only)

MAKER uses MPI internally but cannot run across multiple nodes due to an interaction between Infiniband libraries and MAKER's process forking. Keep it on one node, up to 36 tasks (a full regular node).

```sl
#!/bin/bash -e
#SBATCH --account         nesi99991
#SBATCH --job-name        maker
#SBATCH --nodes           1
#SBATCH --ntasks-per-node 36
#SBATCH --mem-per-cpu     1500
#SBATCH --time            24:00:00

module purge
module load MAKER/<version>

srun maker -q
```

## Output and inode usage

MAKER can produce hundreds of thousands of output files, which risks exhausting your project's inode quota. Recommendations:

- Run few MAKER jobs simultaneously.
- Archive or delete output promptly. Use `nn_archive_files` or `tar`.

See `../filesystems.md` for quotas.

## Upstream

- <http://www.yandell-lab.org/software/maker.html>
