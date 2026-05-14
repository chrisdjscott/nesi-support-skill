# Delft3D

Hydrodynamics, morphodynamics, particle, water-quality and wave modelling suite from Deltares.

## Loading

```bash
module spider Delft3D
module load Delft3D/<version>
```

## Serial

```sl
#!/bin/bash -e
#SBATCH --account  nesi99991
#SBATCH --job-name delft3d-serial
#SBATCH --time     00:30:00
#SBATCH --mem      1G

module load Delft3D/<version>
d_hydro test_input.xml
```

## Shared memory (domain decomposition, one node)

Each subdomain runs in a thread inside one executable.

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      delft3d-omp
#SBATCH --time          01:00:00
#SBATCH --cpus-per-task 4
#SBATCH --mem           2G

module load Delft3D/<version>
srun d_hydro test_input.xml
```

## Distributed memory (automatic stripwise partitioning)

```sl
#!/bin/bash -e
#SBATCH --account     nesi99991
#SBATCH --job-name    delft3d-mpi
#SBATCH --time        02:00:00
#SBATCH --ntasks      16
#SBATCH --mem-per-cpu 1G

module load Delft3D/<version>
srun d_hydro test_input.xml
```

Requesting more tasks than the model has partitions will cause failure.

## Distributed-memory limitations

The MPI partitioning is incompatible with:

- DomainDecomposition
- Fluid mud
- Online coupling
- Drogues / moving observation points
- Culverts
- Power stations with inlet and outlet in different partitions
- Non-hydrostatic solvers
- Walking discharges
- 2D skewed weirs
- `max(mmax,nmax)/npart <= 4`
- Roller model
- Mormerge
- Mass balance polygons

Use shared-memory mode for any of these.

## Upstream

- <https://oss.deltares.nl/web/delft3d>
