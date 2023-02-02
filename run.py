import os
import pathlib
from distutils.dir_util import copy_tree

from pydom_parser.ast_transformer import transpile_file

build_dir = pathlib.Path("build")
if not build_dir.is_dir():
    build_dir.mkdir()

src_dir = pathlib.Path("src")
public_dir = src_dir / "public"

copy_tree(str(public_dir), str(build_dir))

for file in os.listdir("src"):
    if file.endswith(".pyx"):
        transpile_file(src_dir / file, build_dir / file[:-1])
