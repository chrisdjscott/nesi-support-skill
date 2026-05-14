# R

R for statistical computing. Two extended bundles are also available: `R-Geo` (GDAL/GEOS/PROJ stack: `rgeos`, `rgdal`, `sf`, etc.) and `R-bundle-Bioconductor`.

## Loading

```bash
module spider R
module load R/4.2.1-gimkl-2022a            # example
module load R-Geo/4.2.1-gimkl-2022a        # for spatial work
module load R-bundle-Bioconductor/3.17-gimkl-2022a-R-4.3.1
```

## Mahuika-specific notes

- The `snow` package is patched so `RMPISNOW` is not required when using it over MPI.
- `R_LIBS_USER` includes the toolchain string, e.g. `~/R/gimkl-2022a/4.2` instead of the upstream default `~/R/x86_64-pc-linux-gnu-library/4.2`. This keeps user packages from clashing across toolchains.

## Slurm templates

### Serial

```sl
#!/bin/bash -e
#SBATCH --account   nesi99991
#SBATCH --job-name  r-serial
#SBATCH --time      01:00:00
#SBATCH --mem       512M
#SBATCH --output    %x.%j.out
#SBATCH --error     %x.%j.err

module purge
module load R/4.2.1-gimkl-2022a

srun Rscript MySerialRJob.R
```

### Array

```sl
#!/bin/bash -e
#SBATCH --account   nesi99991
#SBATCH --job-name  r-array
#SBATCH --time      01:00:00
#SBATCH --array     1-10
#SBATCH --mem       512M

module purge
module load R/4.2.1-gimkl-2022a

srun Rscript MyArrayRJob.R
```

Inside the R script:

```r
jobid <- as.numeric(Sys.getenv("SLURM_ARRAY_TASK_ID"))
```

### Parallel with doParallel (single node)

```r
library(doParallel)
registerDoParallel(as.numeric(Sys.getenv("SLURM_CPUS_PER_TASK")))

x <- foreach(z = 1000000:1000050, .combine = 'c') %dopar% {
    sum(rnorm(z))
}
```

Set `--cpus-per-task` in the Slurm script. Workers run on one node (limited by physical cores, or logical cores with `--hint=multithread`).

### Parallel with doMPI (multi-node)

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      r-mpi
#SBATCH --time          01:00:00
#SBATCH --ntasks        12
#SBATCH --cpus-per-task 1
#SBATCH --mem-per-cpu   512M

module purge
module load R/4.2.1-gimkl-2022a
module load gimkl/2022a       # exposes MPI

srun Rscript doMPI.R
```

```r
library(doMPI, quiet = TRUE)
cl <- startMPIcluster()
registerDoMPI(cl)

x <- foreach(z = 1000000:1000050, .combine = 'c') %dopar% {
    sum(rnorm(z))
}

closeCluster(cl)
mpi.quit()
```

Worker count is taken from `mpiexec` (i.e. `--ntasks`), no need to pass it explicitly.

## Plot output

R defaults to a screen device. To write to file directly:

```r
png(filename = "plot.png")
plot(...)
dev.off()
```

See R's "Device drivers" docs for alternative formats.

## Package installation

Personal library paths are toolchain-aware, e.g. `~/R/gimkl-2022a/4.2`. List them with `.libPaths()`. To install:

```r
install.packages("sampling")
```

When prompted, say yes to creating a personal library and pick an Australian mirror (the NZ mirror is often out of date).

Project-wide library (shared with the team):

```r
dir.create("/nesi/project/nesi99991/Rpackages", showWarnings = FALSE, recursive = TRUE)
.libPaths(new = "/nesi/project/nesi99991/Rpackages")
```

Or set in `~/.Renviron`:

```bash
R_LIBS=/nesi/project/nesi99991/Rpackages
```

## Custom C extensions

```bash
module load R/4.2.1-gimkl-2022a
R CMD SHLIB mylib.c
```

In R:

```r
dyn.load("~/R/lib64/mylib.so")
```

## Common issues

- "Cannot install `sf`, `rgdal`, etc." Load `R-Geo` instead of base `R`.
- Missing `HarfBuzz`, `FriBidi`, or `devtools` symbols at package install. Load the `devtools` module before R: `module load devtools` then `module load R/<version>`.
- `strtoi(Sys.getenv("SLURM_CPUS_PER_TASK"))` returns `NA` in some R configurations. Use `as.numeric(Sys.getenv("SLURM_CPUS_PER_TASK"))`.
- INLA "GLib version not found": install a specific binary, e.g.

  ```r
  remotes::install_version("INLA", version = "23.06.29",
      repos = c(getOption("repos"),
                INLA = "https://inla.r-inla-download.org/R/testing"), dep = TRUE)
  INLA::inla.binary.install()    # choose centos
  ```

## Upstream

- <https://www.r-project.org/>
- <https://cran.r-project.org/>
- <https://bioconductor.org/>
