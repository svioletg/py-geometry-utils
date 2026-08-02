# ruff: noqa: T201

import ast
import re
import sys
from argparse import ArgumentParser
from collections.abc import Iterable, Iterator
from itertools import chain
from pathlib import Path
from typing import Literal, TypedDict

PATH_EXCLUDE: tuple[Path, ...] = (
    Path('.venv'),
    Path('docs'),
    Path('tests'),
)

DUNDER_REGEX: re.Pattern = re.compile(r'^__(\w+)__$')
IGNORE_REGEX: re.Pattern = re.compile(r'# testcheck: ignore\b')

class FileContentDict(TypedDict):  # noqa: D101
    raw: str
    lines: list[str]

class FunctionFinder(ast.NodeVisitor):  # noqa: D101
    current_class: ast.ClassDef | None = None
    functions: dict[ast.ClassDef | None, list[ast.FunctionDef]]

    def __init__(self) -> None:
        self.current_class = None
        self.functions: dict[ast.ClassDef | None, list[ast.FunctionDef]] = {
            None: [],
        }

        super().__init__()

    @classmethod
    def from_file(cls, fp: str | Path) -> dict[ast.ClassDef | None, list[ast.FunctionDef]]:
        """Returns a dictionary of function names to ``ast.FunctionDef`` found in the contents of ``fp``."""
        return cls.from_str(Path(fp).read_text('utf-8'))

    @classmethod
    def from_str(cls, s: str) -> dict[ast.ClassDef | None, list[ast.FunctionDef]]:
        """Returns a dictionary of function names to ``ast.FunctionDef`` found in ``s``."""
        tree = ast.parse(s)
        inst = cls()
        inst.visit(tree)

        return inst.functions

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: D102
        self.current_class = node
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: D102
        cls = self.current_class
        if cls not in self.functions:
            self.functions[cls] = []
        self.functions[cls].append(node)

def _assemble_deco_name(node: ast.expr) -> str:
    def _dive(node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return f'{_assemble_deco_name(node.value)}.{node.attr}'

        # ast.expr covers lots of types but this library doesn't use anything but Name and Attribute decorators
        raise TypeError(f'Unsupported type for _assemble_deco_name: {node!r}')

    return _dive(node)

def has_decorators(func: ast.FunctionDef, names: str | Iterable[str], *, mode: Literal['any', 'all'] = 'any') -> bool:
    """Checks whether ``func`` has any decorators matching a name in ``names`` applied to it.

    Attribute
    """
    if isinstance(names, str):
        names = (names,)

    match mode:
        case 'any':
            method = any
        case 'all':
            method = all
        case _:
            raise ValueError(f'Unexpected value for mode: {mode!r}')

    return method(
        _assemble_deco_name(deco) in names
        for deco in func.decorator_list
        if isinstance(deco, ast.Attribute | ast.Name)
    )

def make_test_name(func: str, *, cls: str = '') -> str:
    prefix: str = ''

    if func[0] == '_':
        prefix = 'priv'
        if bool(DUNDER_REGEX.match(func)):
            prefix = 'mag'
        func = func.strip('_')

    return 'test_' + '_'.join(
        part for part in (cls.lower(), prefix, func) if part
    )

def make_test_def(func: ast.FunctionDef, *, cls: str = '') -> str:
    is_classmethod: bool = False
    if cls:
        is_classmethod = has_decorators(func, 'classmethod')
    is_property: bool = has_decorators(func, 'property')

    arg_defaults: dict[str, object] = {
        arg.arg:default.value if isinstance(default, ast.Constant) else '...'
        for arg, default in zip(func.args.args[-len(func.args.defaults):], func.args.defaults, strict=False)
    }

    argstr: str = ', '.join(
        f'{arg.arg}={arg_defaults[arg.arg]}' if arg.arg in arg_defaults else arg.arg
        for arg in chain(func.args.posonlyargs, func.args.args, func.args.kwonlyargs)
        if arg.arg not in ['cls', 'self']
    )

    return f"""
def {make_test_name(func.name, cls=cls)}() -> None:
    assert {(cls + ('.' if is_classmethod else '().')) if cls else ''}{func.name}{'' if is_property else f'({argstr})'}
""".strip()

def main() -> int:  # noqa: C901
    if next(Path.cwd().glob('pyproject.toml'), None) is None:
        print(f'Error: tests.{Path(__file__).stem} must be run at the project root')
        return 1

    parser = ArgumentParser()
    parser.add_argument('targets', type=Path, nargs='+',
        help='Directories or files to check. Directories are searched recursively.')
    parser.add_argument('--gen', '-g', action='store_true',
        help='Generate missing test definitions.')

    args = parser.parse_args()
    targets: list[Path] = args.targets
    gen_tests: bool = args.gen

    target_files: Iterator[Path] = chain(
        *(fd.rglob('*.py') for fd in [fp for fp in targets if fp.is_dir()]),
        (fp for fp in targets if fp.is_file()),
    )

    functions: dict[Path, dict[ast.ClassDef | None, list[ast.FunctionDef]]] = {}
    file_content: dict[Path, FileContentDict] = {}

    for fp in target_files:
        if any(fp.is_relative_to(exclude) for exclude in PATH_EXCLUDE):
            continue
        if fp.suffix != '.py':
            continue

        file_content[fp] = {
            'raw': (content := fp.read_text('utf-8')),
            'lines': content.splitlines(),
        }
        functions[fp] = FunctionFinder.from_str(content)

    tests_found: dict[Path, list[str]] = {
        # Assumption made that no tests are defined in classes
        fp:[fn.name for fn in FunctionFinder.from_file(fp)[None]]
        for fp in Path('tests/').glob('test_*.py')
    }
    new_tests: dict[Path, list[str]] = {}

    for fp, kv in functions.items():
        test_path = Path('tests', f'test_{fp.parent.stem}.py' if fp.stem == '__init__' else f'test_{fp.stem}.py')
        new_tests[test_path] = []
        for cls, fns in kv.items():
            if cls:
                pre_def_line, def_line = file_content[fp]['lines'][cls.lineno - 2:cls.lineno]

                if IGNORE_REGEX.search(def_line) or IGNORE_REGEX.search(pre_def_line):
                    continue

            cls_name = cls.name if cls else ''
            for fn in fns:
                pre_def_line, def_line = file_content[fp]['lines'][fn.lineno - 2:fn.lineno]

                if IGNORE_REGEX.search(def_line) or IGNORE_REGEX.search(pre_def_line):
                    continue
                if has_decorators(fn, ('overload', f'{fn.name}.setter')):
                    continue

                test_name = make_test_name(fn.name, cls=cls_name)
                if test_name not in tests_found[test_path]:
                    print(f'{fp}:{fn.lineno}: no test for {cls_name or '<mod>'}.{fn.name}'
                        + f' (expected at {test_path.with_suffix('')}.{test_name})')
                    new_tests[test_path].append(make_test_def(fn, cls=cls_name))
        if not new_tests[test_path]:
            del new_tests[test_path]

    if gen_tests:
        for test_path, tests in new_tests.items():
            print(f'Writing {len(tests)} new test(s) to: {test_path}')
            with open(test_path, 'a', encoding='utf-8') as f:
                f.write('\n' + '\n\n'.join(tests).strip() + '\n')

    if new_tests:
        return 1

    print('No tests missing!')
    return 0

if __name__ == '__main__':
    sys.exit(main())
