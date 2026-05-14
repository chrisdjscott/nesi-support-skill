# VTune

Intel performance profiler. Identifies hotspots in CPU code without recompilation; also supports threading, microarchitecture, and memory-access analyses. Works on any executable (no special compile flags), though debug symbols (`-g`) improve attribution.

## Loading

```bash
module load VTune
```

## Collecting a hotspots profile

```bash
srun --ntasks=1 --cpus-per-task=2 \
    vtune -collect hotspots -result-dir vtune-res ./my_program <args>
```

The result directory contains the raw profile data. The CLI prints a summary table like:

```text
Function                  Module          CPU Time
------------------------  --------------  --------
Upwind<3>::advect.omp_fn  upwindCxx       25.979s
_int_free                 libc.so.6        9.170s
operator new              libstdc++.so.6   6.521s
```

Other useful analyses:

- `-collect threading` for thread imbalance and lock contention.
- `-collect hpc-performance` for an MPI/OpenMP overview.
- `-collect memory-access` for memory bandwidth and NUMA effects.

## Drilling in with the GUI

```bash
vtune-gui <result_dir>
```

Needs X11 forwarding (`ssh -X`, see `../access-and-login.md`).

## Profiling Julia

Use the `-VTune` variant Julia modules and enable JIT profiling. See `./julia.md` for the full recipe.

## Profiling MPI applications

Wrap each rank:

```bash
srun vtune -collect hotspots -result-dir vtune-res-%r -- ./my_mpi_program
```

Or use `-collect-with runsa` with hardware event sampling for cross-rank analyses (requires perf_event access; consult VTune docs).

## Tips

- Profile a representative but short run; long profiles produce huge result directories.
- Build with `-g` (and ideally `-fno-omit-frame-pointer`) so VTune resolves symbols.
- Profile on the same CPU type you will run production on (microarchitectural counters differ across genoa/milan/older partitions). See `../hardware.md`.

## Upstream

- <https://www.intel.com/content/www/us/en/developer/tools/oneapi/vtune-profiler.html>
