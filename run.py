import pathlib
import shutil

build_dir = pathlib.Path("build")
if not build_dir.is_dir():
    build_dir.mkdir()

src_dir = pathlib.Path("src")
public_dir = src_dir / "public"

shutil.copy(public_dir / "*", build_dir)
