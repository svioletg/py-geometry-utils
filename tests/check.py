# ruff: noqa: T201

import ast
import re
import sys
from argparse import ArgumentParser
from collections.abc import Iterable, Iterator
from itertools import chain
from pathlib import Path
from typing import Literal, cast

PATH_EXCLUDE: tuple[Path, ...] = (
    Path('.venv'),
    Path('docs'),
    Path('tests'),
)

DUNDER_REGEX: re.Pattern = re.compile(r'^__(\w+)__$')

class FunctionFinder(ast.NodeVisitor):  # noqa: D101
    current_class: ast.ClassDef | None = None
    functions: dict[str, list[ast.FunctionDef]]

    def __init__(self) -> None:
        self.current_class = None
        self.functions: dict[str, list[ast.FunctionDef]] = {
            '': [],
        }

        super().__init__()

    @classmethod
    def from_file(cls, fp: str | Path) -> dict[str, list[ast.FunctionDef]]:  # noqa: D102
        tree = ast.parse(Path(fp).read_text('utf-8'))
        inst = cls()
        inst.visit(tree)

        return inst.functions

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: D102
        self.current_class = node
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: D102
        if self.current_class:
            cls_name = self.current_class.name
            if cls_name not in self.functions:
                self.functions[cls_name] = []
            self.functions[cls_name].append(node)
        else:
            self.functions[''].append(node)

def has_decorators(func: ast.FunctionDef, names: str | Iterable[str], *, mode: Literal['any', 'all'] = 'any') -> bool:
    if isinstance(names, str):
        names = (names,)

    match mode:
        case 'any':
            method = any
        case 'all':
            method = all
        case _:
            raise ValueError(f'Unexpected value for mode: {mode!r}')

    return method(cast('ast.Name', deco).id in names for deco in func.decorator_list)

def make_test_name(func: str, *, cls: str = '') -> str:
    magic = bool(DUNDER_REGEX.match(func))

    return 'test_' + '_'.join(
        part for part in (cls.lower(), 'mag' if magic else '', DUNDER_REGEX.sub('\\1', func)) if part
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

    functions: dict[Path, dict[str, list[ast.FunctionDef]]] = {}

    for fp in target_files:
        if any(fp.is_relative_to(exclude) for exclude in PATH_EXCLUDE):
            continue
        if fp.suffix != '.py':
            continue

        functions[fp] = FunctionFinder.from_file(fp)

    tests_found: dict[Path, list[str]] = {
        fp:[fn.name for fn in FunctionFinder.from_file(fp)['']]
        for fp in Path('tests/').glob('test_*.py')
    }
    new_tests: dict[Path, list[str]] = {}

    for fp, kv in functions.items():
        test_path = Path('tests', f'test_{fp.parent.stem}.py' if fp.stem == '__init__' else f'test_{fp.stem}.py')
        new_tests[test_path] = []
        for cls, fns in kv.items():
            for fn in fns:
                if any(cast('ast.Name', deco).id == 'overload' for deco in fn.decorator_list):
                    # If the body is just ... it's probably an overload
                    continue
                test_name = make_test_name(fn.name, cls=cls)
                if test_name not in tests_found[test_path]:
                    print(f'{fp}:{fn.lineno}: no test for {cls or '<mod>'}.{fn.name}'
                        + f' (expected at {test_path.with_suffix('')}.{test_name})')
                    new_tests[test_path].append(make_test_def(fn, cls=cls))
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
