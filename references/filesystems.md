# Filesystems and storage

Mahuika compute nodes, login nodes, and OnDemand all see the same filesystems. Check your quota anytime with:

```bash
storage_quota
```

(Cached for ~1 hour.)

## Filesystem summary

| Filesystem | Default quota | Snapshots | Speed | Retention |
| --- | --- | --- | --- | --- |
| `/home/<user>` | 20 GB | Daily, kept 7 days | Fast | 180 days after you leave all active projects |
| `/nesi/project/<code>` | 100 GB (110 GB hard) | Daily, kept 7 days | Fast | 90 days after project's last HPC allocation |
| `/nesi/nobackup/<code>` | 10 TB (12 TB hard) | Weekly Fri 06:00, kept 3 weeks | Fast | Files untouched 90 days are auto-deleted |
| Freezer | per allocation |, | Slow (tape) | 180 days after Freezer allocation ends |

Each filesystem is accessible via native mount, SCP, and Globus (Freezer uses S3).

## `/home`

For user-specific config, source, dotfiles, and small virtual environments. **Do not run jobs from `/home`.** Snapshots daily. No cleaning while your account is active in some project.

## `/nesi/project`

Persistent project storage. Reference data, shared code, conda/uv environments that don't fit in `/home`. Daily snapshots, no cleaning policy.

- Owned by `root`, group is the project group.
- Set up with ACLs so other project members have read/write/execute and support staff have read/execute.
- `setgid` bit is set so new files inherit the project group.
- Read/write performance improves with larger files, `tar` up archives of many small files.

Quota covers both disk space and inode count. Adjustments via support request.

## `/nesi/nobackup` (scratch)

Working space for compute jobs. Datasets in active use, intermediate outputs, job temp files. Not backed up beyond 3 weekly snapshots.

### Auto-cleaning

Files matching **all** of these are deleted:

- Created over 90 days ago,
- Not accessed or modified for 90 days,
- Listed by `nn_doomed_list` two weeks earlier.

Process:

- Fortnightly indexing identifies candidates (GUFI scans run weekend).
- Email notification 2 weeks before deletion (76 days).
- Deletion at 90 days.

Do **not** `touch` files to dodge cleaning, it's a shared resource. After file deletion, any empty **child** directories are also removed; empty **parent** directories and broken symlinks are left in place but still count against the project's inode quota.

### Checking what's scheduled for deletion

```bash
nn_doomed_list --project nesi99991                       # 40-line summary
nn_doomed_list --project nesi99991 --unlimited           # everything
nn_doomed_list --project nesi99991 --limited 100         # control length
nn_doomed_list --project nesi99991 --cycle last          # what was deleted last cycle
```

If you've already deleted listed files, they'll still show until GUFI re-indexes the following weekend.

Full text list:

```bash
gunzip -c /search/autocleaner/filelists/current/nesi99991.gz > to_delete.txt

# Find specific files by keyword
zgrep KEYWORD /search/autocleaner/filelists/current/nesi99991.gz > matches.txt

# Size sorted smallest-to-largest
gunzip -c /search/autocleaner/filelists/current/nesi99991.gz | xargs -d '\n' du -sh | sort -h

# Total size
gunzip -c /search/autocleaner/filelists/current/nesi99991.gz | xargs -d '\n' ls -l | awk '{s+=$5} END {print s/1024/1024/1024 " GB"}'
```

### What to do with expiring data

- Move to `/nesi/project` (request extra quota if needed).
- Compress: `gzip`, `bzip2`, `xz`.
- Move to Freezer (long-term tape).
- Move off Mahuika to institutional storage.

### Deleting your auto-clean candidates yourself

```bash
# T = 90 minus days until next cleanup (e.g. 8 days away - T=82)
find /nesi/nobackup/nesi99991 -type f -atime +82 -ctime +82 -delete
```

### `nn_doomed_list` errors

- `file list not found`, you're on `login01`/`login02`. Switch to `login03` (`ssh login03`).
- `PermissionError`, you don't belong to that project.

## Freezer

Tape-backed S3 storage for cold data (datasets used quarterly or less). Files dwell on disk for hours/days, then move to tape; a catalogue stays on disk for browsing. Accessed via `s3cmd`. Apply for an allocation via `my.nesi.org.nz` or `support@nesi.org.nz`. Designed for relatively large files, not many small files.

## `/opt/nesi/models` (shared LLM cache)

Read-only cache of popular open-weight LLMs in GGUF format. Use this instead of downloading the same model into your `/home` or `/nesi/project` quota. Available families: Llama 3.1, DeepSeek-R1, Qwen3, Qwen2.5, Gemma 3. Confirm exact paths with `ls /opt/nesi/models/gguf/`.

Indicative size-to-GPU mapping:

| Size class | Example | Minimum GPU flags |
| --- | --- | --- |
| 7-8B (quantised) | `/opt/nesi/models/gguf/llama3.1/llama3.1-8b.gguf` | `--gpus-per-node=l4:1` |
| 14B (quantised) | `/opt/nesi/models/gguf/qwen3/qwen3-14b.gguf` | `--gpus-per-node=l4:1` |
| 27-32B (quantised) | `/opt/nesi/models/gguf/gemma3/gemma3-27b.gguf` | `--partition=genoa --gpus-per-node=a100:1` |
| 70B (quantised) | `/opt/nesi/models/gguf/llama3.1/llama3.1-70b.gguf` | `--partition=milan --gpus-per-node=a100:1` |

L4 GPUs have no FP64; fine for quantised inference but unsuitable for training or any FP64-dependent workflow. Request additions to the cache via `support@nesi.org.nz`. Most natural to consume via `references/software/ollama.md`.

## Snapshots and recovery

Snapshots are taken daily on `/home` and `/nesi/project` (kept 7 days), and weekly on `/nesi/nobackup` (kept 3 weeks). If you accidentally delete a file, contact support, they can restore from snapshots. Beyond that, recovery is best-effort.

## Permissions and sharing

POSIX permissions supplemented with ACLs. Group membership: your private user group, one group per active project, all-users groups, license groups. Check with `groups`.

### Home

Default: owner full, group/world none. No ACLs.

### Project and nobackup

Both top-level dirs owned by `root`, group = project group, `setgid` bit set. New files inherit project group + standard ACL:

- Owner: read/write/execute, can modify ACL.
- Project group members: read/write/execute, cannot modify ACL.
- Support team: read/execute.

`setgid` only applies to **new** files in the directory. Files copied or moved with `cp -p` / `mv` keep their original owner/group. Recursive ACL changes on existing trees trigger backups of every touched file, slow and storage-heavy; do it once, early.

### Read-only access groups

For wider projects, request a read-only group via support. Members can be added/removed without recursive ACL edits.

### Files visible to you but unreadable

Likely an ACL or group mismatch. Check with `getfacl <path>` and `ls -lan`.

## Where to put what

| Read pattern | Write pattern | Put it on |
| --- | --- | --- |
| Often | Often (at least every 2 months) | `/nesi/nobackup/<code>` (copy key outputs to `project`) |
| Often | Seldom | `/nesi/project/<code>` |
| Seldom | Seldom | Freezer or off-cluster |

Workflow:

1. Run jobs in `/nesi/nobackup` and per-job `$TMPDIR`.
2. Move keep-forever outputs to `/nesi/project`.
3. Move cold archives to Freezer.
4. Move publication-final data off Mahuika.

## Quick sanity checks

```bash
storage_quota                              # current usage
df -h /home /nesi/project /nesi/nobackup   # filesystem free space (approximate)
du -sh /nesi/nobackup/$USER/*              # what's eating my scratch
groups                                     # what project groups I'm in
getfacl /nesi/project/nesi99991            # who can read/write this dir
```
