# OpenFOAM

Open-source CFD toolbox (also used for solid mechanics, chemistry). No licence restrictions; native MPI parallelisation makes it well-suited to Mahuika.

## Loading

```bash
module spider OpenFOAM
module load OpenFOAM/<version>
source $FOAM_BASH
```

`$FOAM_BASH` must be sourced *after* loading the module and after any `FOAM_USER_*` overrides.

## Slurm template (MPI)

```sl
#!/bin/bash -e
#SBATCH --account     nesi99991
#SBATCH --job-name    openfoam
#SBATCH --time        04:00:00
#SBATCH --ntasks      16
#SBATCH --mem-per-cpu 512M
#SBATCH --output      %x.out

# Working dir must contain 'system', 'constant', '0'
module purge
module load OpenFOAM/<version>
source ${FOAM_BASH}

decomposePar
srun simpleFoam -parallel
reconstructPar -latestTime
```

Past ~16 tasks scaling depends heavily on the case and decomposition; benchmark before requesting more.

## Common gotchas

- Many bundled tutorials start with `cd ${0%/*} || exit`. This breaks under Slurm (the script is copied into `/var/spool/slurm/job*`). Remove the line or `cd` to the case directory explicitly.
- Avoid `srun` for serial `decomposePar` / `reconstructPar` invocations; run them directly.

## Filesystem pressure

OpenFOAM writes vast numbers of small files. Inode-quota exhaustion will crash any job writing to that filesystem (see `../filesystems.md`).

Mitigations in `system/controlDict`:

- `writeInterval` higher
- `purgeWrite N` keeps only the last `N` time directories
- `runTimeModifiable false` avoids re-reading dictionaries each step
- `writeFormat binary` (smaller files, less I/O than ASCII)
- Run on `/nesi/nobackup` (no disk-space quota, large inode allowance)

Check usage with `storage_quota`.

## Environment variables in dictionaries

```text
numberOfSubdomains ${SLURM_NTASKS};
startFrom ${START_TIME};
```

Or edit dictionaries from the Slurm script:

```bash
NSUBDOMAINS=10
sed -i "s/\(numberOfSubdomains \)[[:digit:]]*\(;\)/\1${NSUBDOMAINS}\2/g" system/controlDict
```

## Custom solvers

Install per-user / per-project, not system-wide. Compile with `wmake` after `module load OpenFOAM; source $FOAM_BASH`. Most third-party packages ship a top-level build script.

Redirect compilation output to your project, not the system tree:

```bash
module load OpenFOAM/<version>
export FOAM_USER_LIBBIN=/nesi/project/nesi99991/custom_of/lib
export FOAM_USER_APPBIN=/nesi/project/nesi99991/custom_of/bin
source $FOAM_BASH      # must come AFTER the exports
wmake
```

If `Make/options` references `$FOAM_LIBBIN` or `$FOAM_APPBIN`, change them to the `$FOAM_USER_*` variants.

## Upstream

- <https://openfoam.org/>
- <https://www.openfoam.com/>
- <https://cfd.direct/openfoam/user-guide/>
