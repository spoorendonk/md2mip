"""md2mip — compile Markdown/LaTeX MIP models into standalone Python solver scripts."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("md2mip")
except PackageNotFoundError:
    __version__ = "0.0.0"
