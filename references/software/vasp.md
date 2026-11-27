# VASP

Vienna Ab initio Simulation Package: plane-wave DFT, Hartree-Fock and hybrid functionals with periodic boundary conditions, for materials bulk properties.

## Licence

Restricted, per-research-group. You will have access to VASP4, VASP5, or VASP6 depending on what your group has purchased; minor releases share the major-version licence. Request access from NeSI support and CC your group leader; you may need to provide proof of licence.

## Loading

```bash
module spider VASP
module load VASP/6.5.1-foss-2023a       # CPU
module load VASP/6.5.1-nvofbf-2023b     # GPU
```

Binaries: `vasp_std`, `vasp_gam`, `vasp_ncl`. There is no separate `vasp_gpu`; modules with `nvofbf` in the name are built with OpenACC GPU support in the standard binaries.

## VASP 6 on CPUs (hybrid MPI + OpenMP)

VASP 6 parallelises across MPI ranks (`--ntasks`, bands/orbitals) and OpenMP threads (`--cpus-per-task`, work within one orbital). `NCORE` in `INCAR` is ignored. FFTs need frequent all-to-all communication, so keep tasks within NUMA domains (see `../parallel-computing.md#numa-domains`). `--cores-per-socket` is `21` on `genoa` and `16` on `milan`.

```sl
#!/bin/bash -e
#SBATCH --account          nesi99991
#SBATCH --job-name         vasp
#SBATCH --time             01:00:00
#SBATCH --partition        genoa
#SBATCH --ntasks           8
#SBATCH --cpus-per-task    4
#SBATCH --mem-per-cpu      1G
#SBATCH --cores-per-socket 21
#SBATCH --threads-per-core 1
#SBATCH --distribution     *:block:*
#SBATCH --mem-bind         local
#SBATCH --profile          task

module purge
module load VASP/6.5.1-foss-2023a

export OMP_PROC_BIND=true
export OMP_PLACES=cores

srun vasp_std
```

`--threads-per-core 1` keeps SMT off; VASP runs slower with it. Do not set `--hint=multithread`.

### VASP 5

MPI only (e.g. `VASP/5.4.4-intel-2020a`). Leave `--cpus-per-task 1`, raise `--ntasks`, and share orbital work across ranks with `NCORE` in `INCAR` (e.g. `NCORE = 4`). Keep the same NUMA directives.

## GPU (VASP 6, `nvofbf` modules)

One MPI rank per GPU. Same NUMA directives as the CPU script, plus GPU binding:

```sl
#SBATCH --gpus-per-node    h100:1
#SBATCH --ntasks           1
#SBATCH --cpus-per-task    1
#SBATCH --mem-per-cpu      8G
#SBATCH --cores-per-socket 21
#SBATCH --threads-per-core 1
#SBATCH --distribution     *:block:*
#SBATCH --mem-bind         local
#SBATCH --gres-flags       enforce-binding
#SBATCH --gpu-bind         closest

module purge
module load VASP/6.5.1-nvofbf-2023b
```

On `milan` use `--gpus-per-node a100:1 --constraint a100_80gb --cores-per-socket 16`. Benefit depends on the calculation; benchmark GPU and CPU configurations against compute-unit cost before production runs.

GPU memory is separate from `--mem`; you get all VRAM on each allocated GPU. `cuMemAlloc returned error 2: Out of memory` means VRAM ran out: request more GPUs, larger-VRAM GPUs, or both. See `../hardware.md`.

## Parallel tuning

Converge `INCAR`/`KPOINTS` parameters first, then tune cores, on one representative system.

Test with a fixed-iteration `INCAR`:

```
EDIFFG = 0
NSW    = 3
NELMIN = 3
NELM   = 3
```

Vary the MPI/OpenMP ratio at constant total cores (e.g. `4x4`, `2x8`, `8x2`). For multi-k-point calculations, increase `KPAR` (must divide `--ntasks`). Multithreading mostly benefits hybrid functionals and high-precision electronic structure work.

### Benchmarking tools

- `vasp-parameter-benchmarking`: converge `INCAR`/`KPOINTS` parameters (`ENCUT`, `LREAL`, etc.). <https://github.com/geoffreyweal/vasp-parameter-benchmarking>
- `vasp-core-benchmarking`: sweep `ntasks`/`cpus-per-task` to minimise electronic-step time. <https://github.com/geoffreyweal/vasp-core-benchmarking>

## Visualisation

Load a Python module and use `ase-gui POSCAR` (from Atomic Simulation Environment) to inspect/modify structures. See <https://docs.ase-lib.org/>.

## Upstream

- <https://www.vasp.at/>
- <https://www.vasp.at/wiki/index.php/The_VASP_Manual>
- <https://www.vasp.at/wiki/index.php/OpenACC_GPU_port_of_VASP>
