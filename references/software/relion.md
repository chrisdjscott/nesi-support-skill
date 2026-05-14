# Relion

Cryo-electron microscopy image processing. Most tools benefit greatly from a GPU.

## Loading

```bash
module spider Relion
module load Relion/<version>
```

## GUI workflow

Start the X11 GUI on a login node (forward X11 over SSH; see `../access-and-login.md`):

```bash
module load Relion
relion
```

Configure your job in the GUI, click **Check command**, and the constructed command line appears in the terminal. Paste it into a Slurm batch script.

## Serial commands

If the GUI shows a `which relion_run_ctffind ...` line, you can simplify to just:

```bash
relion_run_ctffind ...
```

## MPI commands

If MPI is enabled the GUI will produce a command like:

```bash
which relion_run_ctffind_mpi ...
```

Launch the MPI binary under `srun`:

```bash
srun relion_run_ctffind_mpi ...
```

## GPU MotionCorr2

For licensing reasons NeSI does not ship the GPU-accelerated MotionCorr2. Install it yourself if Relion's bundled CPU version is too slow.

## Upstream

- <https://relion.readthedocs.io/>
