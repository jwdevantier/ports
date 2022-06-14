from pathlib import Path
from typing import Optional
from leport.api import PkgBuildSteps, PkgInfo, sh, cwd, get_paths, ldconfig, require_programs
from multiprocessing import cpu_count


class Build(PkgBuildSteps):
    def on_init(self) -> None:
        name = self.info.name.lstrip("lib")
        self.pkg_src_dir = self.build_dir / f"{name}-{self.info.version}"

    def prepare(self, info: PkgInfo, build_dir: Path):
        sh("tar", "xvf", f"talloc-{self.info.version}.tar.gz")

    def depends(self, build_dir: Path):
        require_programs(
            "gcc",
            "git",
            "waf",  # build
            "python3", # build
        )
        # python distutils package

    def build(self, build_dir: Path, dest_dir: Path):
        with cwd(self.pkg_src_dir):
            sh("./configure", "--disable-python", "--prefix=/usr/local")
            sh("make", f"-j{cpu_count()}")

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
