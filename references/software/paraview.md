# ParaView

Scientific visualisation tool with a parallel server (`pvserver`) and a local GUI client. On Mahuika, run `pvserver` on a compute node, tunnel the port, connect from your laptop's ParaView GUI.

## Loading

```bash
module spider ParaView
module load ParaView/<version>
```

The server version must match your local client version exactly.

## Client-server workflow

1. Allocate a session and start the server (interactive Slurm or batch):

   ```bash
   module load ParaView/<version>
   pvserver
   # prints: Connection URL: cs://<host>:11111
   ```

2. Open an SSH tunnel from your laptop:

   ```bash
   ssh mahuika -L 11111:<host>:11111
   ```

3. In the local ParaView GUI: File > Connect > Add Server > Client/Server, host `localhost`, port `11111`. Connect.

## Parallel rendering

CPU rendering uses OpenSWR and OSPRay. Both default to one thread. Before launching `pvserver` (or the GUI) request more cores:

```bash
export KNOB_MAX_WORKER_THREADS=${SLURM_CPUS_PER_TASK}
export OSPRAY_THREADS=${SLURM_CPUS_PER_TASK}
```

`pvserver` also supports MPI:

```sl
#!/bin/bash -e
#SBATCH --account     nesi99991
#SBATCH --job-name    pvserver
#SBATCH --time        02:00:00
#SBATCH --ntasks      8
#SBATCH --mem-per-cpu 4G

module load ParaView/<version>
srun pvserver
```

## Upstream

- <https://www.paraview.org/>
