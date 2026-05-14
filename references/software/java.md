# Java

JVM and `java` runtime on Mahuika. The system Java may be outdated; always load a module for the version you need.

## Loading

```bash
module spider Java
module load Java/11.0.4       # example
```

## Slurm template

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      java-job
#SBATCH --time          01:00:00
#SBATCH --cpus-per-task 8
#SBATCH --mem           4G

module purge
module load Java/11.0.4

# If your application calls java indirectly, also export _JAVA_OPTIONS
export _JAVA_OPTIONS=-Djava.io.tmpdir=${TMPDIR}

java -Xmx3g -Djava.io.tmpdir=${TMPDIR} -jar /path/to/foo.jar
```

## Memory (-Xmx)

Set `-Xmx` to roughly 75% of `--mem`. The remainder covers stack, metaspace, JIT, and native allocations. Example: `--mem=32G` then `-Xmx24g`.

If the application invokes `java` indirectly (wrapper scripts), set the same options via the environment:

```bash
export _JAVA_OPTIONS=-Djava.io.tmpdir=${TMPDIR}
```

## Temporary files

Java defaults `java.io.tmpdir` to `/tmp`, which is small and shared. Always redirect to `$TMPDIR` (Slurm-managed, cleaned at job end):

```bash
java -Djava.io.tmpdir=$TMPDIR ...
```

Or set `_JAVA_OPTIONS` as above.

## Upstream

- <https://www.java.com/>
- <https://openjdk.org/>
