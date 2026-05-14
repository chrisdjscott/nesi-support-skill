# FreeSurfer

Cortical reconstruction and volumetric segmentation of structural MRI. Distributed on Mahuika as an Apptainer container (image pulled from <https://hub.docker.com/r/freesurfer/freesurfer>).

## Prerequisites

### Licence

FreeSurfer requires a free licence file:

1. Register at <http://surfer.nmr.mgh.harvard.edu/registration.html>.
2. Save the returned `license.txt` under your home or project directory.

## Container location

- Image: `/opt/nesi/container/FreeSurfer/freesurfer-<version>.aimg`
- Sample dataset: `/opt/nesi/container/FreeSurfer/data`

## Example Slurm script

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      freesurfer-test
#SBATCH --cpus-per-task 2
#SBATCH --mem           2G
#SBATCH --time          00:30:00
#SBATCH --output        slog/%j.out

module purge
module load Apptainer

export SUBJECTS_DIR=${PWD}/subjects_dir
mkdir -p "${SUBJECTS_DIR}"

export FS_LICENSE=${PWD}/license.txt
if [ ! -f "$FS_LICENSE" ]; then
    echo "ERROR: License file not found at $FS_LICENSE"
    exit 1
fi

CONTAINER=/opt/nesi/container/FreeSurfer/freesurfer-7.4.1.aimg
TEST_DATA=${PWD}/data/T1.nii.gz

apptainer exec \
    --env SUBJECTS_DIR=${SUBJECTS_DIR} \
    --env FS_LICENSE=${FS_LICENSE} \
    --bind ${SUBJECTS_DIR}:${SUBJECTS_DIR} \
    --bind $(dirname ${TEST_DATA}):$(dirname ${TEST_DATA}) \
    --bind $(dirname ${FS_LICENSE}):$(dirname ${FS_LICENSE}) \
    ${CONTAINER} \
    recon-all -i ${TEST_DATA} -sd ${SUBJECTS_DIR} -s test_subject -autorecon1 -no-isrunning
```

## Required environment variables

- `SUBJECTS_DIR`: where FreeSurfer stores and reads subject data.
- `FS_LICENSE`: path to your licence file. Both must be passed into the container with `--env` **and** their containing directories bound with `--bind`.

See `../containers.md` for general Apptainer usage on Mahuika.

## Upstream

- <https://surfer.nmr.mgh.harvard.edu/>
