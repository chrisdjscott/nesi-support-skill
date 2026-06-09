"""NeSI HPC support skill package.

`SKILL.md` and `references/` are force-included at the package root at build
time, so a `SkillsCapability` discovers the skill at depth 0.
"""

from importlib.resources import files


def skill_dir():
    """Directory of this installed skill package.

    Exposed via the `vdsai.skills.nesi` entry point so a host agent discovers
    the skill without naming this package in its own code. The host coerces the
    returned `Traversable` to a `pathlib.Path`.
    """
    return files("nesi_hpc_skill")
