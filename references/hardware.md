# Mahuika hardware

## Compute nodes

Jobs land on a node matching the requested CPU:memory ratio. Asking for 2 GB/core puts you on a 2 GB/core node (or 4 GB/core if those are full), and so on. You always get the memory you requested.

### Milan partition (`--partition=milan`)

2× AMD EPYC 7713 (Milan) per node, 8 chiplets × 8 cores = 128 physical cores per node, 126 schedulable.

| Memory | Per-core | GPU | Nodes |
| --- | --- | --- | --- |
| 512 GB | 4 GB | none | 54 |
| 1024 GB | 8 GB | none | 8 |
| 1024 GB | 8 GB | 4× NVIDIA HGX A100 80 GB | 4 |

### Genoa partition (`--partition=genoa`)

2× AMD EPYC 9634 (Genoa) per node, 12 chiplets × 7 cores = 168 physical cores per node, 166 schedulable.

| Memory | Per-core | GPU | Nodes |
| --- | --- | --- | --- |
| 358 GB | 1 GB | none | 44 |
| 716 GB | 2 GB | 2× NVIDIA A100 40 GB | 4 |
| 1432 GB | 4 GB | none | 8 |
| 1432 GB | 4 GB | 2× NVIDIA H100 96 GB | 4 |
| 1432 GB | 4 GB | 4× NVIDIA L4 24 GB | 4 |

Specifying `--partition` is often unnecessary; the scheduler picks based on what you request. Pin it only when you need a specific architecture or GPU.

## GPUs

Request with `--gpus-per-node=<type>:<count>`.

| Type | VRAM | Per node | Partition | Slurm header |
| --- | --- | --- | --- | --- |
| A100 (HGX, 80 GB) | 80 GB | 4 | `milan` | `--partition=milan` + `--gpus-per-node=A100:1` |
| A100 (PCIe, 40 GB) | 40 GB | 2 | `genoa` | `--partition=genoa` + `--gpus-per-node=A100:1` |
| H100 | 96 GB | 2 | `genoa` | `--gpus-per-node=H100:1` |
| L4 | 24 GB | 4 | `genoa` | `--gpus-per-node=L4:1`, no fp64 |
| A40 | 48 GB | n/a | RDC (cloud) | Not via Slurm, teaching/training only |

L4 has no fp64, so anything depending on double-precision floats (some molecular dynamics, some fluid solvers) needs A100 or H100.

If you omit the GPU type (`--gpus-per-node=1`), you may land on any available GPU including unsuitable ones.

`CUDA_VISIBLE_DEVICES` is set automatically, it lists the *indices* of allocated GPUs, not a count.

## Limits

Hard limits applied per job and per user. See `references/slurm.md#hard-limits`.

| Scope | Limit |
| --- | --- |
| Per job | 10 nodes, 21 node-days, 21 days walltime |
| Per user | 2688 CPU cores, 3528 core-days booked, 6 TB memory, 30 TB-days booked, 6 GPUs, 14 GPU-days booked |
| Queue | 1000 jobs |
| Array | 1000 tasks |

If you genuinely need more, email `support@nesi.org.nz`.

## Filesystems (overview)

| Mount | Quota | Backed up | Use |
| --- | --- | --- | --- |
| `/home/<user>` | 20 GB | Yes (7 days) | Configs, source, virtualenvs (small). Don't run jobs here. |
| `/nesi/project/<code>` | 100 GB | Yes (7 days) | Persistent project data, code, large venvs. |
| `/nesi/nobackup/<code>` | 10 TB | No (3 wk snapshots only) | Scratch, raw data, job working directory. **Auto-cleaned at 90 days.** |
| Freezer (S3) | per allocation | Tape | Long-term cold storage. |

See `references/filesystems.md` for details.
