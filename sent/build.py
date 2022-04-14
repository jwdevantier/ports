from pathlib import Path
from typing import Optional
from leport.api import PkgBuildSteps, PkgInfo, sh, cwd


class Build(PkgBuildSteps):
    def on_init(self) -> None:
        self.pkg_src_dir = self.build_dir / f"{self.info.name}"

    def prepare(self, info: PkgInfo, build_dir: Path):
        pass

    def pkg_version(self, build_dir: Path) -> Optional[str]:
        with cwd(self.pkg_src_dir):
            out = sh("git", "rev-parse", "--short", "HEAD", capture=True)
            return out.stdout.strip()

    def depends(self, build_dir: Path):
        # skip for now, would require some sensing of libs required etc.
        pass

    def build(self, build_dir: Path, dest_dir: Path):
        with cwd(self.pkg_src_dir):
            sh("make")

    def check(self, build_dir: Path, dest_dir: Path):
        pass

    def install(self, build_dir: Path, dest_dir: Path):
        with cwd(self.pkg_src_dir):
            sh("make", f"DESTDIR={dest_dir}", "install")

