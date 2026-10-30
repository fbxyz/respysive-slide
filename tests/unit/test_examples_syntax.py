"""Code examples in docstrings and in the documentation must be valid Python.

Examples often use names defined elsewhere (a figure, a deck), so they are
compiled, not run. The live demos of the documentation are run by the
Sphinx build itself.
"""

import doctest
import importlib
import inspect
import pkgutil
import re
import textwrap
from pathlib import Path

import pytest

import respysive

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]
_PARSER = doctest.DocTestParser()


def _docstrings():
    for info in pkgutil.walk_packages(respysive.__path__, "respysive."):
        module = importlib.import_module(info.name)
        yield info.name, module.__doc__
        for name, obj in vars(module).items():
            if getattr(obj, "__module__", None) != info.name:
                continue
            yield f"{info.name}.{name}", obj.__doc__
            if inspect.isclass(obj):
                for attr, member in vars(obj).items():
                    member = getattr(member, "__func__", member)
                    if isinstance(member, property):
                        member = member.fget
                    yield f"{info.name}.{name}.{attr}", getattr(member, "__doc__", None)


def _literal_blocks(doc):
    """Indented blocks after a line ending with '::' (reST literal blocks)."""
    lines = doc.splitlines()
    for i, line in enumerate(lines):
        if not line.rstrip().endswith("::") or line.strip().startswith(".."):
            continue
        indent = len(line) - len(line.lstrip())
        block = []
        for following in lines[i + 1 :]:
            if following.strip() and len(following) - len(following.lstrip()) <= indent:
                break
            block.append(following)
        code = textwrap.dedent("\n".join(block)).strip()
        if code and not code.startswith(">>>"):
            yield code


def _docstring_examples():
    for name, doc in _docstrings():
        if not doc:
            continue
        doc = inspect.cleandoc(doc)
        source = "".join(example.source for example in _PARSER.get_examples(doc))
        if source:
            yield pytest.param(source, id=f"{name}:doctest")
        for k, code in enumerate(_literal_blocks(doc)):
            yield pytest.param(code, id=f"{name}:block{k}")


_CODE_BLOCK = re.compile(r"^(\s*)\.\. code-block:: python\s*\n\s*\n((?:\1   .*\n|\s*\n)+)", re.MULTILINE)


def _rst_examples():
    for path in sorted((ROOT / "docs").rglob("*.rst")):
        if {"_build", "_old", "gallery"} & set(path.relative_to(ROOT / "docs").parts):
            continue
        for k, match in enumerate(_CODE_BLOCK.finditer(path.read_text(encoding="utf-8"))):
            yield pytest.param(textwrap.dedent(match.group(2)), id=f"{path.relative_to(ROOT)}:{k}")


@pytest.mark.parametrize("source", list(_docstring_examples()))
def test_docstring_example_compiles(source):
    compile(source, "<docstring>", "exec")


@pytest.mark.parametrize("source", list(_rst_examples()))
def test_documentation_example_compiles(source):
    compile(source, "<rst>", "exec")
