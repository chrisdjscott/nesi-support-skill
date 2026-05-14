# Trinity

*De novo* transcriptome assembly from RNA-Seq reads. Three sequential modules: Inchworm, Chrysalis, Butterfly. From the Broad Institute and Hebrew University of Jerusalem.

## Loading

```bash
module spider Trinity
module load Trinity/2.14.0-gimkl-2022a       # example
```

## Filesystem and quotas

Run Trinity under `/nesi/nobackup/...` (no disk quota, but a file-count quota applies). Trinity creates very many files, especially under `read_partitions/`. Request a file-count quota increase from NeSI support before large runs. See `../filesystems.md`.

QC reads first. Without it, assemblies fail or stall.

## Recommended workflow: two phases

NeSI recommends splitting Trinity into two job submissions; this is faster and cheaper than the default single-job behaviour.

### Phase 1: clustering (Inchworm, Chrysalis)

High memory, supports multi-threading. Sizes shown are placeholders; benchmark first with a subset.

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      trinity-phase1
#SBATCH --time          30:00:00
#SBATCH --ntasks        1
#SBATCH --cpus-per-task 16
#SBATCH --mem           220G

module purge
module load Trinity/<version>

srun Trinity --no_distributed_trinity_exec \
    --CPU ${SLURM_CPUS_PER_TASK} --max_memory 200G \
    [your_other_trinity_options]
```

`--no_distributed_trinity_exec` stops Trinity before Phase 2. Set `--max_memory` slightly below `--mem`.

### Phase 2: parallel mini-assemblies via HPC GridRunner

Phase 2 runs many small commands (often hundreds of thousands), each independent and I/O heavy. Distribute them across nodes via HPC GridRunner.

Create `SLURM.conf` in the submission directory:

```text
[GRID]
gridtype=SLURM

cmd=sbatch --partition=large,bigmem --mem=5G --ntasks=1 --cpus-per-task=1 --time=01:00:00 --account=nesi99991

max_nodes=10
cmds_per_node=50
```

- `cmds_per_node`: commands per sub-job batch.
- `max_nodes`: how many sub-jobs may sit in the queue concurrently.
- Don't set `-e`/`-o` in `cmd`; HPC GridRunner sets them internally.
- Trinity docs say 1 GB per command, but spikes above 4 GB happen. Allow headroom.

Master batch script:

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      trinity-phase2grid
#SBATCH --time          30:00:00
#SBATCH --ntasks        1
#SBATCH --cpus-per-task 1
#SBATCH --mem           20G
#SBATCH --partition     bigmem
#SBATCH --hint          nomultithread

module purge
module load Trinity/<version>
module load HpcGridRunner/20210803

srun Trinity --CPU ${SLURM_CPUS_PER_TASK} --max_memory 20G \
    --grid_exec "hpc_cmds_GridRunner.pl --grid_conf ${SLURM_SUBMIT_DIR}/SLURM.conf -c" \
    [your_other_trinity_options]
```

`--CPU` and `--max_memory` are ignored in grid mode but still required.

## Benchmarks

Grid mode is significantly faster and cheaper than the default single-node Phase 2. For an 8-million-read test, default 16-core Phase 2 ran 24 h and used 387 core-hours; grid mode with `max_nodes=60, cmds_per_node=500` ran in 2 h 37 min for 160 core-hours.

For a 286-million-read marine sediment sample, Phase 1 needed ~15 h on 18 threads + 220 GB on `bigmem`. Phase 2 took ~19 h with `max_nodes=cmds_per_node=100` and 5 GB sub-jobs, for ~1,800 core-hours.

## Upstream

- <https://github.com/trinityrnaseq/trinityrnaseq/wiki>
