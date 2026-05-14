# Modules and software stack

Mahuika uses Lmod environment modules for the installed software stack. See `references/software/` for per-application detail.

## Core commands

| Command | What it does |
| --- | --- |
| `module load Python/3.11.6-foss-2023a` | Load a specific version. |
| `module load Python` | Load the current default version (may change over time, pin a version in scripts). |
| `module avail` | List currently available modules (with current loaded modules' compatibility considered). |
| `module spider <name>` | Fuzzy search across all modules including hidden dependencies. |
| `module spider Python/3.11.6-foss-2023a` | Show prerequisites and how to load that specific version. |
| `module list` | What you have loaded right now. |
| `module purge` | Unload everything (recommended at top of every batch script). |
| `module unload <name>` | Drop one module. |
| `module show <name>` | Show what env vars the module sets. |

Full reference: `man module` or <https://lmod.readthedocs.io/>.

## Module version names

Module names look like `Python/3.11.6-foss-2023a`. The version string after the first `/` splits as `<version>-<toolchain>`:

- `Python/3.11.6-foss-2023a`, Python 3.11.6 built with the `foss-2023a` toolchain (GCC + OpenMPI + OpenBLAS + FFTW etc.).
- `PnetCDF/1.9.0-intel-2020a`, built with Intel compilers.
- `CUDA/12.5.0`, no toolchain suffix; built with the `System` toolchain, compatible with everything.

## Toolchains

A toolchain is the (compiler, MPI, BLAS, FFTW, ...) bundle a module was compiled against. Mixing toolchains is unsafe.

Loading `foss-2023a` and `intel-2020a` modules together causes module reloads:

```out
The following have been reloaded with a version change:
  1) GCCcore/12.3.0 => GCCcore/9.2.0
  2) binutils/2.40-GCCcore-12.3.0 => binutils/2.32-GCCcore-9.2.0
  ...
```

Software may still launch but will eventually hit a library symbol error. **If you see "reloaded with a version change" warnings, stop and check toolchain compatibility.** Either stick to one toolchain, or ask support to build the package against the toolchain you need.

System-toolchain modules (no suffix, e.g. `binutils/2.32`, `CUDA/12.5.0`) work with any toolchain.

## Pinning versions

Always pin in batch scripts:

```bash
module purge
module load Python/3.11.6-foss-2023a       # not just "Python"
module load CUDA/12.5.0
```

Unpinned `module load Python` is fine for interactive exploration but will silently change behaviour when the default rolls forward.

## Looking up what's installed

- `module spider <partial-name>`, fuzzy.
- `module spider <exact-version>`, shows prerequisites you must load first.
- <https://docs.nesi.org.nz/Software/Available_Applications/>, full searchable list.

If a version you need is missing, email `support@nesi.org.nz`, they install on request.

## Installing software yourself

If the package isn't centrally installed (or needs custom build options), install into `/nesi/project/<code>/<appname>/` so it's shared with the project.

### Workflow

1. **Decide install location**

    ```bash
    mkdir -p /nesi/project/nesi99991/myapp
    cd /nesi/project/nesi99991/myapp
    ```

2. **Download source**

    ```bash
    git clone https://github.com/example/myapp.git src
    # or
    wget https://example.com/myapp-1.2.3.tar.gz
    tar -xf myapp-1.2.3.tar.gz
    ```

3. **Load build deps and a toolchain**

    ```bash
    module purge
    module load foss/2023a CMake
    ```

    Record which modules you loaded, runtime will need the same set.

4. **Configure / build**

    GNU autotools:

    ```bash
    ./configure --prefix=$PWD/install
    make -j 4
    make install
    ```

    CMake:

    ```bash
    mkdir build && cd build
    cmake .. -DCMAKE_INSTALL_PREFIX=$PWD/../install
    make -j 4 && make install
    ```

    Plain Makefile: just `make` (or `make all`).

5. **Use it**

    ```bash
    module load foss/2023a       # same toolchain you built against
    /nesi/project/nesi99991/myapp/install/bin/myapp
    ```

    Or add to `PATH` in `~/.bash_profile`:

    ```bash
    echo 'export PATH=$PATH:/nesi/project/nesi99991/myapp/install/bin' >> ~/.bash_profile
    ```

### Linking against EasyBuild libraries

When you load a module, EasyBuild sets `$EBROOT<NAME>` to its install prefix (uppercase, no special chars). Use these for `-I`, `-L`:

```bash
module load FFTW
gcc myprog.c -I$EBROOTFFTW/include -L$EBROOTFFTW/lib -lfftw3
```

Library link order matters: if A depends on B, write `-lA -lB`.

## Language-specific package management

Per-language conventions (full detail in `references/software/<lang>.md`):

- **Python**: `module load Python/<version>-foss-<year>`; install user packages with `pip install --user <pkg>` or a venv in `/nesi/project`. See `software/python.md`. For uv, see `software/uv.md`.
- **R**: `module load R/<version>`; `install.packages()` goes to `~/R/...`. See `software/r.md`.
- **Julia**: `module load Julia`; packages go in `~/.julia`. See `software/julia.md`.
- **MATLAB**: support packages installable via `matlab.addons.install`. See `software/matlab.md`.
- **conda / mamba**: use `Miniforge3` module; put env in `/nesi/project/<code>/envs/` (home is too small). See `software/miniforge3.md`.

## Common build problems

- **Unresolved symbols** mentioning `omp`/`mp_`: missing OpenMP link flag (`-fopenmp` GNU, `-qopenmp` Intel).
- **Many C++-looking names**: missing `-lstdc++` for static links.
- **Trailing `_` or `__`**: Fortran name-mangling mismatch (`-fno-underscoring`, `-fsecond-underscore`, Intel equivalents).
- **`Illegal preprocessor directive`** in Fortran: add `-cpp` (gfortran) to enable preprocessing.
