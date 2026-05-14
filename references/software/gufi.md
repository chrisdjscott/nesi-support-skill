# GUFI

Grand Unified File Index. Provides fast `find` and `du` equivalents over a pre-built index of the NeSI filesystems. The index is regenerated weekly, so files created or moved after the last index run will not appear.

## Restrictions

- Only works on `login03`. Check with `hostname`, and `ssh login03` if needed.
- Paths must be absolute and use `/nesi/home` (not `/home`). Relative paths and `.` / `~` do not work.

Valid path roots:

- `/nesi/home/$USER/...`
- `/nesi/project/nesi99991/...`
- `/nesi/nobackup/nesi99991/...`

## Loading

```bash
module load gufi
```

## gufi_find

Same flags as `find`, but pass the full indexed path:

```bash
gufi_find /nesi/nobackup/nesi99991 -name foo.dat
gufi_find /nesi/home/$USER -type f -printf '%s %p\n' 2>/dev/null | sort -nr | head -n 1
```

## gufi_du

Same flags as `du`:

```bash
gufi_du -s /nesi/home/$USER
gufi_du -s /nesi/project/nesi99991
gufi_du --inodes -s /nesi/nobackup/nesi99991/baz    # count files
```

## Troubleshooting

- "Could not get realpath of ...: No such file or directory" usually means the path is not yet indexed (wait until end of the week). Fall back to `find` or `du`.
- "Error: Skipping directory ...: Permission denied" means GUFI cannot read the path, often because you lack project membership or the path is not in the index.
- Tab-completion is known to sometimes drop the SSH session on `login03`. Avoid `<TAB>` after `gufi_find` / `gufi_du`.

## Upstream

- <https://github.com/mar-file-system/GUFI>
