# VASP

Vienna Ab initio Simulation Package: plane-wave DFT, Hartree-Fock and hybrid functionals with periodic boundary conditions, for materials bulk properties.

## Licence

Restricted, per-research-group. You will have access to VASP4, VASP5, or VASP6 depending on what your group has purchased; minor releases share the major-version licence. Request access from NeSI support and CC your group leader; you may need to provide proof of licence.

## Loading

```bash
module spider VASP
module load VASP/6.4.2-foss-2023a       # example
```

Binaries: `vasp_std`, `vasp_gam`, `vasp_ncl`. There is no separate `vasp_gpu`; GPU support is built into the standard binaries on `*-NVHPC-*` modules.

## Hybrid MPI + OpenMP (VASP 6, recommended)

VASP 6 parallelises Kohn-Sham orbital work across both MPI ranks (`--ntasks`) and OpenMP threads (`--cpus-per-task`); the legacy `NCORE` flag in `INCAR` is ignored. Process locality matters significantly because FFTs require frequent all-to-all communication.

```sl
#!/bin/bash -e
#SBATCH --account          nesi99991
#SBATCH --job-name         vasp
#SBATCH --time             01:00:00
#SBATCH --ntasks           8
#SBATCH --cpus-per-task    4
#SBATCH --mem-per-cpu      1G
#SBATCH --extra-node-info  1:*:1          # at least 1 free socket; disable SMT
#SBATCH --distribution     *:block:*       # fill sockets in order
#SBATCH --mem-bind         local
#SBATCH --profile          task

module purge
module load VASP/<version>

srun vasp_std
```

### VASP 5

MPI-only. Use `NCORE` in `INCAR` to share orbital work across ranks:

```sl
#SBATCH --ntasks         32
#SBATCH --cpus-per-task  1
```

## Disable SMT

VASP runs slower with simultaneous multithreading. Do not set `--hint=multithread`. The `--extra-node-info 1:*:1` flag above also disables SMT. See `../parallel-computing.md`.

## GPU (VASP 6 only)

```sl
#SBATCH --partition      genoa
#SBATCH --gpus-per-node  A100:1
#SBATCH --ntasks         1
#SBATCH --cpus-per-task  8
```

Use one MPI rank per GPU. GPU memory is separate from `--mem`; if you hit `cuMemAlloc returned error 2: Out of memory`, request more GPUs or larger-memory GPUs (e.g. 80 GB A100 on `milan`). See `../hardware.md` and `../slurm-examples.md#gpu-jobs`.

## Parallel tuning

Test with a fixed-iteration `INCAR`:

```
EDIFFG = 0
NSW    = 3
NELMIN = 3
NELM   = 3
```

Vary the MPI/OpenMP ratio at constant total cores (e.g. `4x4`, `2x8`, `8x2`).

For multi-**k** calculations, experiment with `KPAR` (must divide `--ntasks`).

Multi-threading mostly benefits hybrid functionals and high-precision electronic structure work.

### Benchmarking tools

NeSI-maintained helpers automate the sweeps:

- `vasp-parameter-benchmarking`: converge `INCAR`/`KPOINTS` parameters (`ENCUT`, `LREAL`, etc.). <https://github.com/geoffreyweal/vasp-parameter-benchmarking>
- `vasp-core-benchmarking`: sweep `ntasks`/`cpus-per-task` to minimise electronic-step time. <https://github.com/geoffreyweal/vasp-core-benchmarking>

## Visualisation

Load a Python module and use `ase-gui POSCAR` (from Atomic Simulation Environment) to inspect/modify structures. See <https://docs.ase-lib.org/>.

## Upstream

- <https://www.vasp.at/>
- <https://www.vasp.at/wiki/index.php/The_VASP_Manual>
- <https://www.vasp.at/wiki/index.php/Optimizing_the_parallelization>
