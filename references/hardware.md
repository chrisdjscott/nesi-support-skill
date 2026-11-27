# Mahuika hardware

## Compute nodes

Jobs land on a node matching the requested CPU:memory ratio. Asking for 2 GB/core puts you on a 2 GB/core node (or a higher-ratio node if those are full). You always get the memory you requested. Installed memory is a few percent above what Slurm schedules (a 512 GB node offers ~480 GB), so a job requesting exactly the nominal ratio across every core will not fit. `sinfo -o '%n %m'` shows exact schedulable figures.

### Milan partition (`--partition=milan`)

2× AMD EPYC 7713 (Milan) per node, 8 chiplets × 8 cores = 128 cores. A100 80 GB nodes have 1× EPYC 7713P (64 cores); A100 40 GB nodes have 2× EPYC 7413 (48 cores).

| Memory | Per-core | GPU | Nodes |
| --- | --- | --- | --- |
| 512 GB | 4 GB | none | 55 |
| 1024 GB | 8 GB | none | 8 |
| 512 GB | 8 GB | 4× NVIDIA HGX A100 80 GB | 4 |
| 512 GB | 10 GB | 3× NVIDIA A100 PCIe 40 GB | 3 |

<!-- LOCAL-NOTE start: a100-40gb-node-count | agent-authored clarification, preserve across reconciles (see AGENTS.md "Local notes and corrections") -->
There are 3 A100 40 GB nodes (`mg17` to `mg19`, feature `a100_40gb`), as confirmed by `sinfo` on 2026-11-27 and upstream `slurm-limits.json`. Upstream `Hardware.md` says 2.
<!-- LOCAL-NOTE end -->

### Genoa partition (`--partition=genoa`)

2× AMD EPYC 9634 (Genoa) per node, 12 chiplets × 7 cores = 168 cores.

| Memory | Per-core | GPU | Nodes |
| --- | --- | --- | --- |
| 384 GB | 2 GB | none | 44 |
| 768 GB | 4 GB | 2× NVIDIA RTX PRO 6000 96 GB | 4 |
| 1536 GB | 8 GB | none | 8 |
| 1536 GB | 8 GB | 2× NVIDIA H100 NVL 94 GB | 4 |
| 1536 GB | 8 GB | 4× NVIDIA L4 24 GB | 4 |
| 768 GB | 9 GB | none (1× EPYC, 84 cores) | 4 |

<!-- LOCAL-NOTE start: genoa-single-socket-nodes | agent-authored clarification, preserve across reconciles (see AGENTS.md "Local notes and corrections") -->
Genoa also has 4 single-socket CPU nodes (`l13` to `l16`, features `big,nogpu`): 84 cores, one NUMA domain, about 717 GB schedulable, as confirmed by `sinfo` on 2026-11-27 and upstream `slurm-limits.json`. Upstream `Hardware.md` does not list them.
<!-- LOCAL-NOTE end -->

### Hugemem partition (`--partition=hugemem`)

Intel Xeon Gold (Cascade Lake) nodes for very large shared-memory jobs. Jobs never land here automatically, you must request the partition explicitly. The architecture differs from milan/genoa, expect to recompile.

| CPUs | Cores | Memory | Nodes |
| --- | --- | --- | --- |
| 2× Xeon Gold 6230 | 40 | 1.5 TB | 2 |
| 4× Xeon Gold 6238M | 88 | 6 TB | 1 |

Specifying `--partition` is often unnecessary; the scheduler picks based on what you request. Pin it only when you need a specific architecture, a GPU type, or hugemem.

## GPUs

Request with `--gpus-per-node=<type>:<count>`. Type strings are lower-case: `a100`, `pro_6000`, `h100`, `l4`.

| Type | VRAM | Per node | Partition | Notes |
| --- | --- | --- | --- | --- |
| A100 SXM4 | 80 GB | 4 | `milan` | NVLink between all 4. Only 4-GPU-per-node option. |
| A100 PCIe | 40 GB | 3 | `milan` | No NVLink, GPUs talk over PCIe. |
| RTX PRO 6000 (Blackwell) | 96 GB | 2 | `genoa` | Slow fp64. No TF32 tensor speedup, gains come from BF16/FP8/FP4. |
| H100 NVL | 94 GB | 2 | `genoa` | 600 GB/s NVLink between the pair. Best fp64. |
| L4 | 24 GB | 4 | `genoa` | Slow fp64, 24 GB limit. Best perf/watt for inference and teaching. |

L4 and RTX PRO 6000 are poor at double precision (fp64); anything depending on it (some molecular dynamics, some solvers) needs A100 or H100 NVL. Rough workload fit: fp64 HPC prefers H100 NVL then A100; molecular dynamics prefers RTX PRO 6000, then H100 NVL, then A100; 2-GPU communication-bound work prefers H100 NVL (NVLink); 4-GPU tightly-coupled work only fits A100 80 GB on milan; single-GPU fine-tuning and large-model inference prefer RTX PRO 6000 or H100 NVL.

An `a100` request can land on either A100 type. Add `--constraint=a100_80gb` if you need 80 GB VRAM or NVLink (`a100_40gb` selects the PCIe nodes).

If you omit the GPU type (`--gpus-per-node=1`), you may land on any available GPU including unsuitable ones.

`CUDA_VISIBLE_DEVICES` is set automatically, it lists the *indices* of allocated GPUs, not a count.

GPUDirect RDMA is not enabled and GPU nodes are split across two InfiniBand switches, so keep GPU jobs within a single node.

## Limits

Hard limits applied per job and per user. See `references/slurm.md#hard-limits`.

| Scope | Limit |
| --- | --- |
| Per job | 10 nodes, 21 node-days, 21 days walltime |
| Per user | 2688 CPU cores, 3528 core-days booked, 6 TB memory, 31.5 TB-days booked, 6 GPUs, 14 GPU-days booked |
| Queue | 1000 jobs |
| Array | 1000 tasks |
| Debug QoS | 1 job, 15 min, 2 nodes, 168 cores, 512 GB, 2 GPUs |

If you genuinely need more, email `support@nesi.org.nz`.

Each Slurm "socket" on Mahuika is a NUMA domain (8 per Genoa/Milan CPU node). See `references/parallel-computing.md#numa-domains`.

## Filesystems (overview)

| Mount | Quota | Backed up | Use |
| --- | --- | --- | --- |
| `/home/<user>` | 20 GB | Yes (7 days) | Configs, source, virtualenvs (small). Don't run jobs here. |
| `/nesi/project/<code>` | 100 GB | Yes (7 days) | Persistent project data, code, large venvs. |
| `/nesi/nobackup/<code>` | 2 TB | No (3 wk snapshots only) | Scratch, raw data, job working directory. **Auto-cleaned at 90 days.** |
| Freezer (S3) | per allocation | Tape | Long-term cold storage. |

See `references/filesystems.md` for details.
