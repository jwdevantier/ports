from pathlib import Path
from typing import Optional
from leport.api import PkgBuildSteps, PkgInfo, sh, cwd, get_paths, require_programs
from multiprocessing import cpu_count
import os


class Build(PkgBuildSteps):
    def on_init(self) -> None:
        self.pkg_src_dir = self.build_dir / self.info.name

    def prepare(self, info: PkgInfo, build_dir: Path):
        pass

    def pkg_version(self, build_dir: Path) -> Optional[str]:
        with cwd(self.pkg_src_dir):
            commit_hash = sh("git", "rev-parse", "--short", "HEAD", capture=True).stdout.strip()
            # get tag(s) associated commit, if any (error otherwise)
            return sh("git", "describe", "--tags", "--abbrev=0", commit_hash, capture=True).stdout.strip()


    def depends(self, build_dir: Path):
        # skip for now, would require some sensing of libs required etc.
        require_programs(
            "cmake",
            "ninja",
            "make",
            "pkg-config",
            "gcc",
        )

    def build(self, build_dir: Path, dest_dir: Path):
        with cwd(self.pkg_src_dir):
            env = os.environ.copy()
            env["CMAKE_INSTALL_PREFIX"] = "/usr/local/"
            sh("make", f"-j{cpu_count()}", env=env)

    def check(self, build_dir: Path, dest_dir: Path):
        pass

    def install(self, build_dir: Path, dest_dir: Path):
        with cwd(self.pkg_src_dir):
            sh("make", f"DESTDIR={dest_dir}", "install")

        binpath = Path("usr/local/bin")
        for path, is_dir in get_paths(dest_dir, "**/*"):
            if is_dir:
                self.set_stat(path, user="root", group="root", mode="755")
            else:
                self.set_stat(
                    path,
                    user="root",
                    group="root",
                    mode="755" if binpath in path.parents else "644"
                )
