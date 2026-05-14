# Nextflow

Workflow engine for data-intensive pipelines, widely used in bioinformatics (nf-core). For alternatives see `./cylc.md` and `snakemake.md`.

## Loading

```bash
module spider Nextflow
module load Nextflow/25.10.0    # example
```

## Run modes on Mahuika

Three patterns, picked by the `-profile` and where you launch from:

1. **Interactive Slurm session** for development and debugging. Pipeline ends when the session does.
2. **Batch job** (`-profile local,apptainer`). All sub-processes run inside one Slurm allocation; best for workflows dominated by many short tasks.
3. **Head job** (`-profile slurm,apptainer`). A low-resource long-running job hosts Nextflow, which submits each process to Slurm separately; best when processes vary widely in resource use and most are long-running.

Cache and plugin locations should always be redirected off `/home`:

```bash
export NXF_APPTAINER_CACHEDIR=/nesi/nobackup/nesi99991/apptainer_cache
export NXF_PLUGINS_DIR=/nesi/project/nesi99991/.nextflow/plugins
export NXF_OFFLINE='true'
```

## Interactive session

```bash
srun --account nesi99991 --job-name nf-interactive \
     --cpus-per-task 16 --mem-per-cpu 24000 --time 24:00:00 --pty bash

module load Nextflow/25.10.0
export NXF_APPTAINER_CACHEDIR=/nesi/nobackup/nesi99991/apptainer_cache
export NXF_PLUGINS_DIR=/nesi/project/nesi99991/.nextflow/plugins

nextflow run hello    # test
```

## Batch job (single Slurm allocation)

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      nextflow-workflow
#SBATCH --time          12:00:00
#SBATCH --cpus-per-task 16
#SBATCH --mem           24G

module purge
module load Nextflow/25.10.0
export NXF_APPTAINER_CACHEDIR=/nesi/nobackup/nesi99991/apptainer_cache
export NXF_PLUGINS_DIR=/nesi/project/nesi99991/.nextflow/plugins
export NXF_OFFLINE='true'

nextflow run NEXTFLOW_WORKFLOW \
    -profile local,apptainer \
    --outdir /nesi/project/nesi99991/NEXTFLOW_WORKFLOW/out \
    -w /nesi/nobackup/nesi99991/NEXTFLOW_WORKFLOW/work
```

Size resources for the biggest single process in the workflow.

## Head job (submits processes to Slurm)

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      nextflow-head
#SBATCH --time          12:00:00
#SBATCH --cpus-per-task 4
#SBATCH --mem           4G

module purge
module load Nextflow/25.10.0
export NXF_APPTAINER_CACHEDIR=/nesi/nobackup/nesi99991/apptainer_cache
export NXF_PLUGINS_DIR=/nesi/project/nesi99991/.nextflow/plugins
export NXF_OFFLINE='true'

nextflow run NEXTFLOW_WORKFLOW \
    -profile slurm,apptainer \
    --outdir /nesi/project/nesi99991/NEXTFLOW_WORKFLOW/out \
    -w /nesi/nobackup/nesi99991/NEXTFLOW_WORKFLOW/work
```

Do not use the `slurm` executor for processes that complete in under 30 minutes; it burdens the scheduler with no throughput gain. Use the `local` executor for short tasks and mark only long processes with a `slurm`-targeted label.

## Recommended configuration layering

Use three stacked `.config` files:

1. Pipeline-level (system- and data-agnostic, version-controlled with the pipeline).
2. System-level (NeSI/Mahuika defaults, see below).
3. Run-level (`custom.config`) for per-run tweaks.

Example system-level config (`nextflow.config`):

```text
params {
    config_profile_description = 'NeSI HPC profile'
    max_cpus   = 64
    max_memory = 1024.GB
}

process {
    stageInMode = 'symlink'
    cache       = 'lenient'
}

profiles {
    debug { cleanup = false }
    local { process.executor = 'local' }
    slurm {
        process.executor = 'slurm'
        process.array    = 100
    }
}

executor {
    '$slurm' {
        queueSize         = 500
        submitRateLimit   = '20 min'
        pollInterval      = '30 sec'
        queueStatInterval = '30 sec'
        jobName           = { "${task.process}-${task.hash}" }
        queue             = 'genoa,milan'
    }
}

apptainer {
    apptainer.pullTimeout = '2h'
}

cleanup = true
```

## Selective Slurm submission

To run a workflow as a batch job but flag a few long processes for separate Slurm submission, add a label:

```text
process {
    withLabel: slurm_array {
        executor = 'slurm'
    }
}
```

See the Nextflow docs for full process selector priority rules.

## Reports and trace

For optimisation, enable both the HTML execution report and a trace file. Add to `custom.config`:

```text
params.timestamp = new java.util.Date().format('yyyy-MM-dd_HH-mm-ss')

report {
    enabled = true
    overwrite = false
    file = "./runInfo/report-${params.timestamp}.html"
}

trace {
    enabled = true
    overwrite = false
    file = "./runInfo/trace-${params.timestamp}.txt"
    fields = 'name,status,exit,duration,realtime,cpus,%cpu,memory,%mem,rss,peak_rss,workdir,native_id'
}
```

Useful trace fields:

- `native_id`: Slurm job ID for processes submitted as separate jobs.
- `duration` vs `realtime`: queue+run time vs actual run time.
- `%cpu`, `%mem`, `peak_rss`: efficiency metrics for resource right-sizing.

See `../debugging-efficiency.md` for cross-cutting profiling.

## nf-core

nf-core pipelines expect plugin support, so set `NXF_PLUGINS_DIR` to a cached location (see above) and run with `NXF_OFFLINE='true'` once plugins are present.

## Upstream

- <https://www.nextflow.io/docs/latest/>
- <https://nf-co.re/>
