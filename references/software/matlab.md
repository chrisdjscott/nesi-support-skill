# MATLAB

MATLAB on Mahuika. Floating licences are shared with NeSI member institutions. Users outside those institutions can still run compiled MATLAB code via the MATLAB Compiler Runtime (MCR).

## Loading

```bash
module spider MATLAB
module load MATLAB/<version>
```

## Slurm templates

### Run a script

```sl
#!/bin/bash -e
#SBATCH --account   nesi99991
#SBATCH --job-name  matlab-script
#SBATCH --time      01:00:00
#SBATCH --mem       512M

module purge
module load MATLAB/<version>

matlab -nodisplay < MATLAB_job.m
```

### Run a function

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      matlab-func
#SBATCH --time          06:00:00
#SBATCH --cpus-per-task 4
#SBATCH --mem           2G
#SBATCH --output        %x.log

module purge
module load MATLAB/<version>

matlab -batch "addpath(genpath('.'));myFunction(5,20)"
```

For MATLAB older than R2019a use `-nodisplay -r '...'` instead of `-batch`.

Command-line flags use a single `-` (e.g. `-nodisplay`), not the usual GNU `--`. Prefix `!` inside MATLAB runs a shell command, e.g. `!squeue -u $USER`.

## Parallelism

MATLAB does not use MPI. Keep `--ntasks=1` and request more cores via `--cpus-per-task`. For embarrassingly parallel work prefer Slurm job arrays (see `../slurm-examples.md`); they queue faster and have less overhead than `parpool`.

### Implicit threading

Many MATLAB operations multi-thread automatically. Diminishing returns above 4-8 cores.

### parpool (explicit, single node)

By default MATLAB writes per-worker scratch under `~/.matlab/local/<cluster>/jobs`, which causes parallel MATLAB jobs to clash. Point each job at `$TMPDIR`:

```matlab
pc = parcluster('local');
pc.JobStorageLocation = getenv('TMPDIR');
parpool(pc, str2num(getenv('SLURM_CPUS_PER_TASK')));
```

To silence the parpool timezone warning add to your Slurm script:

```bash
export TZ="Pacific/Auckland"
```

Use `parfor` for loops where iterations are independent, or `parfeval` for asynchronous function execution.

When `parpool` jobs are killed (cancelled / timeout), Slurm may report `OUT_OF_MEMORY` due to how worker shutdown is detected. This is not necessarily a real OOM; check actual memory use with `seff` (see `../debugging-efficiency.md`).

## GPU

MATLAB uses CUDA. Each MATLAB release supports a specific CUDA version; check the MathWorks "GPU Support by Release" page. R2021a or newer is required for A100 / A100-1g.5gb GPUs. See `../hardware.md` for GPU partitions.

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      matlab-gpu
#SBATCH --time          01:00:00
#SBATCH --cpus-per-task 4
#SBATCH --mem           10G
#SBATCH --gpus-per-node 1
#SBATCH --output        %x.%j.log

module purge
module load MATLAB/2021a
module load CUDA/11.0.2

matlab -batch "gpuDevice()"
```

A GPU device-hour costs more than a CPU core-hour; size your job carefully.

## mex (C/C++/Fortran extensions)

MATLAB supports compiling C, C++ and Fortran extensions via `mex`. From R2020b onwards, an unsupported compiler version produces an error rather than a warning. Load a compatible compiler module before calling `mex`. Compiler flags are taken from `CFLAGS`, `CXXFLAGS`, `FFLAGS`, `LDFLAGS` (the Windows-only `COMPFLAGS` is ignored).

## Checkpointing

Any MATLAB job over a day should checkpoint. Simple pattern:

```matlab
checkpoint = 'checkpoint_2020-03-09T0916.mat';
if exist(checkpoint,'file') == 2
    load(checkpoint);
    startindex = i;
else
    startindex = 1;
end

for i = startindex:100
    % long-running work
    save(['checkpoint_', datestr(now, 'yyyy-mm-ddTHHMM')])
end
```

## Upstream

- <https://www.mathworks.com/help/matlab/>
- <https://www.mathworks.com/help/parallel-computing/>
