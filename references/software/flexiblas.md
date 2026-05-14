# FlexiBLAS

Lightweight wrapper around BLAS and LAPACK that lets you choose the backend at runtime. The `foss/2023a` toolchain ships FlexiBLAS as its BLAS/LAPACK library with OpenBLAS as the default backend. Any software built against `foss/2023a` can switch to BLIS or Intel MKL by setting `FLEXIBLAS`.

## Switching backends

```bash
module load Python/3.11.3-foss-2023a    # uses OpenBLAS by default

# Intel MKL
module load imkl/2022.0.2
export FLEXIBLAS=IMKL

# BLIS
module load BLIS/0.9.0-GCC-12.3.0
export FLEXIBLAS=BLIS

# Back to OpenBLAS explicitly
export FLEXIBLAS=OPENBLAS

# Or revert to the toolchain default
unset FLEXIBLAS
```

## When to use

For workloads dominated by dense linear algebra (matrix multiplies, eigenproblems, FFTs via BLAS), benchmarking the three backends is worthwhile. Relative performance differs by CPU type (e.g. milan AMD nodes versus genoa AMD versus older Intel hardware). See `../hardware.md` for partitions.

## Upstream

- <https://www.mpi-magdeburg.mpg.de/projects/flexiblas>
