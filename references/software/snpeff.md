# snpEff

Variant annotation and functional effect prediction tool.

## Loading

```bash
module spider snpEff
module load snpEff/5.0-Java-11.0.4      # example
```

The jar is at `$EBROOTSNPEFF/snpEff.jar`.

## One-off configuration

snpEff's default `data.dir` is not writable from the installed module. Copy the config to project space and point it at a writable data directory:

```bash
module load snpEff/<version>
cp $EBROOTSNPEFF/snpEff.config /nesi/project/nesi99991/my_snpEff.config
```

Edit line 17 of `my_snpEff.config` from `data.dir = ./data/` to e.g.:

```
data.dir = /nesi/project/nesi99991/snpEff_data/
```

Then pass `-c <path-to-config>` on every run.

## Example Slurm script

```sl
#!/bin/bash -e
#SBATCH --account   nesi99991
#SBATCH --job-name  snpeff
#SBATCH --time      00:20:00
#SBATCH --mem       4G
#SBATCH --output    %x_%j.out

module purge
module load snpEff/<version>

java -jar $EBROOTSNPEFF/snpEff.jar \
    -c /nesi/project/nesi99991/my_snpEff.config \
    <other flags>
```

## Upstream

- <https://pcingola.github.io/SnpEff/>
