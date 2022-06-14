from pathlib import Path
from typing import Optional
from leport.api import PkgBuildSteps, PkgInfo, sh, cwd, get_paths, ldconfig
from multiprocessing import cpu_count
import os


class Build(PkgBuildSteps):
    def on_init(self) -> None:
        self.pkg_src_dir = self.build_dir / f"{self.info.name}-{self.info.version}"

    def prepare(self, info: PkgInfo, build_dir: Path):
        sh("tar", "xvf", f"{self.info.name}-{self.info.version}.tar.xz")

    def depends(self, build_dir: Path):
        # fix later
        pass

    def build(self, build_dir: Path, dest_dir: Path):
        with cwd(self.pkg_src_dir):
            pkg_path_default = sh(
                "pkg-config", "--variable", "pc_path", "pkg-config", capture=True).stdout.strip()
            env = os.environ.copy()
            env["PKG_CONFIG_PATH"] = f"/usr/local/lib/pkgconfig:{pkg_path_default}"
            
            sh(
                "./configure", "--enable-static", "--enable-shared", "--prefix=/usr/local",
                )
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
