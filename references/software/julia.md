# Julia

Dynamic language for numerical and scientific computing.

## Loading

```bash
module spider Julia
module load Julia/1.10.4       # example
```

## Slurm template

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      julia-job
#SBATCH --time          01:00:00
#SBATCH --cpus-per-task 8
#SBATCH --mem           4G

module purge
module load Julia/<version>

julia --threads ${SLURM_CPUS_PER_TASK} script.jl
```

For MPI use `MPI.jl` and launch with `srun julia script.jl` (the `MPI.jl` package picks up the cluster MPI when built against it).

## Package installation

Julia stores packages under `DEPOT_PATH` and searches `LOAD_PATH` at runtime. Mahuika's centrally-managed packages are on `LOAD_PATH` by default. Put your own packages in `/nesi/project` so the team shares one install and home quota stays clear.

In a Julia session:

```julia
empty!(DEPOT_PATH)
push!(DEPOT_PATH, "/nesi/project/nesi99991/julia")
using Pkg
Pkg.add("Flux")
```

Then expose that directory at runtime by setting `JULIA_LOAD_PATH` in your shell or Slurm script (prepend so your project versions win):

```bash
export JULIA_LOAD_PATH="/nesi/project/nesi99991/julia:${JULIA_LOAD_PATH}"
```

Unset `JULIA_LOAD_PATH` to revert to the centrally-managed set only.

## Profiling with VTune

Mahuika ships `-VTune` variants of Julia built with external-profiler hooks.

```bash
module load Julia/<version>-VTune
module load VTune
export ENABLE_JITPROFILING=1

srun amplxe-cl -collect hotspots -- julia your_program.jl
```

Open the result directory with `amplxe-gui --path-to-open <result-dir>` (needs X11 forwarding, see `../access-and-login.md`). See also `./vtune.md`.

## Upstream

- <https://julialang.org/>
- <https://docs.julialang.org/>
