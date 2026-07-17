# Software catalogue (per-application reference index)

One file per centrally-installed application. Load the specific file when the user asks about that package.

Always check installed versions with `module spider <name>` on Mahuika, these pages reference example version strings but the actual default updates over time.

## Chemistry, molecular dynamics, quantum

| Package | File | Use |
| --- | --- | --- |
| CP2K | `cp2k.md` | ab initio MD, DFT |
| Gaussian | `gaussian.md` | quantum chemistry (licence-restricted) |
| GROMACS | `gromacs.md` | classical MD, biomolecules |
| LAMMPS | `lammps.md` | classical MD, materials |
| Molpro | `molpro.md` | quantum chemistry |
| NWChem | `nwchem.md` | quantum chemistry |
| ORCA | `orca.md` | quantum chemistry |
| VASP | `vasp.md` | DFT, plane-wave (licence-restricted) |

## Bioinformatics, structural biology, genomics

| Package | File | Use |
| --- | --- | --- |
| AlphaFold | `alphafold.md` | protein structure prediction |
| BLAST | `blast.md` | sequence alignment |
| BRAKER | `braker.md` | gene annotation pipeline |
| Clair3 | `clair3.md` | small-variant calling |
| Dorado | `dorado.md` | Nanopore basecaller (GPU) |
| fastStructure | `faststructure.md` | population genetics |
| FreeSurfer | `freesurfer.md` | MRI cortical reconstruction |
| GATK | `gatk.md` | variant calling toolkit |
| ipyrad | `ipyrad.md` | RAD-seq |
| MAKER | `maker.md` | genome annotation |
| ont-guppy-gpu | `ont-guppy-gpu.md` | Nanopore basecaller (legacy GPU) |
| RAxML | `raxml.md` | phylogenetics |
| Relion | `relion.md` | cryo-EM single-particle analysis |
| snakemake | `snakemake.md` | workflow manager |
| snpEff | `snpeff.md` | variant annotation |
| Supernova | `supernova.md` | 10x Genomics linked-read assembly |
| Trinity | `trinity.md` | de novo transcriptome assembly |
| VirSorter | `virsorter.md` | viral sequence detection |

## Machine learning / deep learning

| Package | File | Use |
| --- | --- | --- |
| Lambda_Stack | `lambda_stack.md` | DL toolchain bundle |
| ollama | `ollama.md` | local LLM serving |
| TensorFlow | `tensorflow.md` | TF/Keras on CPU or GPU |

## CFD, FEA, engineering simulation

| Package | File | Use |
| --- | --- | --- |
| ABAQUS | `abaqus.md` | FEA (licence-restricted) |
| ANSYS | `ansys.md` | multiphysics (licence-restricted) |
| COMSOL | `comsol.md` | multiphysics (licence-restricted) |
| Delft3D | `delft3d.md` | coastal/estuarine modelling |
| FDS | `fds.md` | fire dynamics simulator |
| OpenFOAM | `openfoam.md` | CFD |
| OpenSees | `opensees.md` | structural earthquake engineering |
| ParaView | `paraview.md` | visualisation |
| TUFLOW | `tuflow.md` | flood/hydraulics modelling (licence-restricted) |

## Climate, weather, geophysics

| Package | File | Use |
| --- | --- | --- |
| CESM | `cesm.md` | Community Earth System Model |
| WRF | `wrf.md` | Weather Research & Forecasting |

## Languages and core tooling

| Package | File | Use |
| --- | --- | --- |
| Apptainer | `apptainer.md` | containers (also `references/containers.md`) |
| Cylc | `cylc.md` | workflow engine |
| FlexiBLAS | `flexiblas.md` | runtime-switchable BLAS |
| GUFI | `gufi.md` | filesystem indexer (powers `nn_doomed_list`) |
| Java | `java.md` | JVM |
| Julia | `julia.md` | language + package install |
| MATLAB | `matlab.md` | MATLAB on Mahuika |
| Miniforge3 | `miniforge3.md` | conda/mamba env management |
| Nextflow | `nextflow.md` | workflow manager |
| Python | `python.md` | Python + venv + MPI/multiprocessing |
| R | `r.md` | R + package install |
| uv | `uv.md` | Python project/env manager |

## Profiling and debugging tools

| Package | File | Use |
| --- | --- | --- |
| VTune | `vtune.md` | Intel performance profiler |

(Skipped: index/templating placeholder pages, expired/retired packages.)

## How to use this catalogue

1. When the user names a package, open the matching file from this list.
2. Each per-package page contains: load command, minimal Slurm template, GPU template (where supported), package-specific gotchas, link to upstream docs.
3. For toolchain/version selection across the stack, see `references/modules.md`.
4. Always confirm the installed version with `module spider <name>` before pinning in a script.
