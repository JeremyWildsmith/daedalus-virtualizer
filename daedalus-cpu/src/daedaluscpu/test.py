from time import sleep
import questionary
import sys
from argparse import ArgumentParser

from pathlib import Path
import yaml
from slugify import slugify
import re
import random
import shutil
from contextlib import contextmanager
from tempfile import TemporaryDirectory, mkdtemp
from typing import NamedTuple, List
from .common import PROJECT_CONFIG_FILE
import subprocess
from rich.console import Console
import json
import time
import contextlib
from platformdirs import user_data_dir

from argparse import ArgumentParser
from pathlib import Path
from importlib.resources import files, as_file
import subprocess
import pexpect
import os
from rich.progress import Progress
from .gen import create_project, load_project_config

console = Console()

class TestResult(NamedTuple):
    name: str
    category: str
    passed: bool
    skipped: bool
    runtime_seconds: float

@contextmanager
def working_directory(path: Path | None, keep: bool, allow_overwrite: bool):
    if path is None:
        r = Path(mkdtemp())
        yield r
        if not keep:    
            shutil.rmtree(r, ignore_errors=True)
    else:
        p = Path(path)

        try:
            p.mkdir(parents=True, exist_ok=allow_overwrite)
        except FileExistsError as e:
            print(f"Error, test workspace directory already exists.", file=sys.stderr)
            exit(1)

        yield p
    

@contextlib.contextmanager
def create_temp_project(templates: Path, config_source: Path):
    if not config_source:
        yield None
        return
    
    if not templates:
        print("Error, to test a configuration file you must specify the templates path with --templates", file=sys.stderr)
        exit(1)

    original_cwd = os.getcwd()
    
    with TemporaryDirectory() as tmp_dir:
        console.print(f"[cyan]Generating the test project in directory...")
        proj_dir = create_project(
            load_project_config(config_source),
            templates,
            Path(tmp_dir)
        )
        
        console.print(f"[cyan]Project generated: {proj_dir}")
        os.chdir(proj_dir)
        try:
            yield tmp_dir
        finally:
            os.chdir(original_cwd)

    
class ProjectConfig(NamedTuple):
    compiler_build_dir: Path
    compiler_invoke_bin: Path
    isa: Path
    
    platform_build_dir: Path
    platform_libs: List[Path]
    
    skip_tests: List[str]

def build_target_toolchain(cfg, workdir):

    with console.status("[bold cyan]Building the compiler..."):
        result = subprocess.run(
            ["make"],
            cwd=cfg.compiler_build_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            console.print(f"[red]{result.stderr}[/red]")
            console.print("[red]✖ Compiler build failed. See stderr or try manually building yourself.[/red]")
            exit(1)
        
        if not cfg.compiler_invoke_bin.exists():
            console.print(f"[red]✖ Missing the compiler output binary artifact: {cfg.compiler_invoke_bin}[/red]")
            exit(1)

    console.print("[green]✔ Compiler build successful[/green]")
    
    with console.status("[bold cyan]Building the enclave platform..."):
        result = subprocess.run(
            ["make"],
            cwd=cfg.platform_build_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            console.print(f"[red]{result.stderr}[/red]")
            print("Failed to build the compiler. See stderr.")
            exit(1)
        
        for artifact in cfg.platform_libs:
            if not artifact.exists():
                console.print(f"[red]✖ Missing the platform output build artifact: {artifact}[/red]")
                exit(1)
    
    console.print("[green]✔ Platform build successful[/green]")

def test_message_passing(bin_path, input_output_data):
    p = pexpect.spawn(str(bin_path), encoding="utf-8", timeout=None)
    p.setecho(False)
    p.linesep = "\n"

    p.expect(r"input ready")
    p.readline()
    
    with Progress() as progress:
        task = progress.add_task(f"[bold cyan]Running test '{bin_path.stem}'", total=len(input_output_data))

        for t in input_output_data:
            input, output = t["input"], t["output"]
            p.sendline(input)
            
            line = p.readline().strip()
            if line.strip() != output.strip():
                raise AssertionError(f"'{line.strip()}' != '{output.strip()}'")
            
            progress.update(task, advance=1)

    p.close()

def setup_test_directory(cfg, workdir):
    build_target_toolchain(cfg, workdir)
    
    with console.status("[bold cyan]Configuring test project layout..."):
        toolchain_dir = workdir / "toolchain"
        
        toolchain_dir.mkdir(exist_ok=True)
        
        shutil.copy2(cfg.compiler_invoke_bin, toolchain_dir / cfg.compiler_invoke_bin.name)
        
        for a in cfg.platform_libs:
            shutil.copy2(a, toolchain_dir / a.name)

        # Setup test case files.
        test_case_dir = workdir / "test_cases"
        compile_fail_dir = workdir / "test_fail_compile"
        compile_pass_dir = workdir / "test_pass_compile"
        test_message_passing = workdir / "test_message_passing"
        
        test_case_dir.mkdir(exist_ok=True)
        compile_fail_dir.mkdir(exist_ok=True)
        compile_pass_dir.mkdir(exist_ok=True)
        test_message_passing.mkdir(exist_ok=True)
        
        with as_file(files("daedaluscpu.data") / "test_cases") as src_path:
            for i in src_path.iterdir():
                if any([i.name.startswith(x) for x in cfg.skip_tests]):
                    console.print(f"[cyan]Skipping setup for test per project configuration: {i.name}")
                    continue
                
                target = test_case_dir / i.name
                
                if i.is_dir():
                    shutil.copytree(i, target, dirs_exist_ok=True)
                else:
                    shutil.copy2(i, target)

        with as_file(files("daedaluscpu.data") / "test_fail_compile") as src_path:
            for i in src_path.iterdir():
                if any([i.name.startswith(x) for x in cfg.skip_tests]):
                    console.print(f"[cyan]Skipping setup for test per project configuration: {i.name}")
                    continue
                
                target = compile_fail_dir / i.name
                
                if i.is_dir():
                    shutil.copytree(i, target, dirs_exist_ok=True)
                else:
                    shutil.copy2(i, target)
        

        with as_file(files("daedaluscpu.data") / "test_pass_compile") as src_path:
            for i in src_path.iterdir():
                if any([i.name.startswith(x) for x in cfg.skip_tests]):
                    console.print(f"[cyan]Skipping setup for test per project configuration: {i.name}")
                    continue
                
                target = compile_pass_dir / i.name
                
                if i.is_dir():
                    shutil.copytree(i, target, dirs_exist_ok=True)
                else:
                    shutil.copy2(i, target)

        with as_file(files("daedaluscpu.data") / "test_message_passing") as src_path:
            for i in src_path.iterdir():
                if any([i.name.startswith(x) for x in cfg.skip_tests]):
                    console.print(f"[cyan]Skipping setup for test per project configuration: {i.name}")
                    continue
                
                target = test_message_passing / i.name
                
                if i.is_dir():
                    shutil.copytree(i, target, dirs_exist_ok=True)
                else:
                    shutil.copy2(i, target)

        console.print("[green]✔ Prepared test cases[/green]")
        
        with as_file(files("daedaluscpu.data") / "test_support") as src_path:
            for i in src_path.iterdir():
                target = workdir / i.name
                
                if i.is_dir():
                    shutil.copytree(i, target, dirs_exist_ok=True)
                else:
                    shutil.copy2(i, target)
        
        console.print("[green]✔ Prepared harness / support files[/green]")
        
    with console.status("[bold cyan]Building the test suite..."):
        result = subprocess.run(
            ["make"],
            cwd=workdir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            console.print(f"[red]{result.stderr}[/red]")
            console.print("[red]✖ Test-suite build failed. See stderr or try manually building yourself.[/red]")
            exit(1)

def has_fail_assertion(text_dump):
    lines = [x.strip() for x in text_dump.split("\n") if x.strip()]
    
    if len(lines) < 2:
        return False
    
    return lines[-2:] == ["TEST_FAIL", "!!!TEST_END!!!"]

def execute_test_case(enclave_bin, host_bin, runtime_constraint):
    if not enclave_bin.exists() or not host_bin.exists():
        raise AssertionError("Either host bin or enclave bin is missing.")
    
    start = time.perf_counter()
    result_enclave = subprocess.run(
        [enclave_bin],
        capture_output=True,
        check=True,
        text=True
    )
    enclave_runtime = time.perf_counter() - start

    if result_enclave.returncode != 0:
        raise AssertionError("Enclave bin returned with non-zero exit code.")
    
    if has_fail_assertion(result_enclave.stdout):
        raise AssertionError("Enclave bin made a fail assertion.")

    result_host = subprocess.run(
        [enclave_bin],
        capture_output=True,
        check=True,
        text=True
    )
    
    if result_host.returncode != 0:
        raise AssertionError("Host bin returned with non-zero exit code.")
    
    if has_fail_assertion(result_host.stdout):
        raise AssertionError("Host bin made a fail assertion.")
    
    if result_host.stderr.strip() != result_enclave.stderr.strip():
        raise AssertionError("Host and enclave bin produced stderr output that did not match")
    
    if result_host.stdout.strip() != result_enclave.stdout.strip():
        raise AssertionError("Host and enclave bin produced stderr output that did not match")
    
    
    if runtime_constraint and enclave_runtime > runtime_constraint:
        raise AssertionError(f"Enclave binary performance missed runtime constraint. Actual {enclave_runtime}s vs Expected {runtime_constraint}")

    return False

def run_execute_test_cases(workdir, filter, skip):
    test_sources = workdir / "test_cases"
    enclave_cases = workdir / "enclave_bin"
    host_cases = workdir / "host_bin"
    runtime = test_sources / "runtime.json"
    
    test_cases = [t for t in test_sources.iterdir() if t.is_file() and t.name.lower().endswith(".c")]
    
    console.print(f"\n[bold black]Discovered {len(test_cases)} test cases in \"execute and assert\" category.")
    console.print(f"Starting testing now...")

    results = []
    
    try:
        with open(runtime, "r") as f:
            runtime_constraint = json.load(f)
    except FileNotFoundError:
        runtime_constraint = {}
        console.print("[bold red] No runtime constraint file found. Will not test runtime constraints.")

    if filter:
        test_cases.sort(key=lambda e: 1 if filter in e.stem else 0)

    for i in range(len(test_cases)):
        t = test_cases[i]
        with console.status(f"[bold cyan] Running test case {i + 1}/{len(test_cases)}: {t.stem}"):
            if (filter and filter not in t.stem) or (skip and any([s in t.stem for s in skip])):
                console.print(f"[bold][dim]Test case {t.stem} was skipped: did not match filter.")
                results.append(TestResult(t.stem, "execute and assert", False, True, 0))
                continue
            
            host_bin = host_cases / t.stem
            enclave_bin = enclave_cases / t.stem
            
            start_time = time.perf_counter()
            try:
                execute_test_case(enclave_bin, host_bin, runtime_constraint[t.stem] if t.stem in runtime_constraint else None)
                console.print(f"[bold green]Test case '{t.stem}' passed!")
                results.append(TestResult(t.stem, "execute and assert", True, False, time.perf_counter() - start_time))
            except AssertionError as e:
                console.print(f"[bold red]Test case '{t.stem}' failed: {e}")
                results.append(TestResult(t.stem, "execute and assert", False, False, time.perf_counter() - start_time))

    return results


def run_messagepassing_test_cases(workdir, filter):
    test_sources = workdir / "test_message_passing"
    bin_files = workdir / "test_message_passing_bin"

    test_cases = [t for t in test_sources.iterdir() if t.is_file() and t.name.lower().endswith(".c")]
    
    console.print(f"\n[bold black]Discovered {len(test_cases)} test cases in \"message passing\" category.")
    console.print(f"Starting testing now...")
    
    
    try:
        with open(test_sources / "messages.json", "r") as f:
            messages = json.load(f)
    except:
        console.print(f"[red bold]✖ Could not load errors.json file. Skipping fail compile tests.")
        return

    results = []

    if filter:
        test_cases.sort(key=lambda e: 1 if filter in e.stem else 0)


    for i in range(len(test_cases)):
        t = test_cases[i]

        if filter and filter not in t.stem:
            console.print(f"[bold][dim]Test case {t.stem} was skipped: did not match filter.")
            results.append(TestResult(t.stem, "message passing", False, True, 0))
            continue
        
        start_time = time.perf_counter()
        try:
            if t.stem not in messages:
                raise AssertionError("Missing messages.json entry.")

            test_message_passing(bin_files / t.stem, messages[t.stem])
            console.print(f"[bold green]Test case '{t.stem}' passed!")
            results.append(TestResult(t.stem, "message passing", True, False, time.perf_counter() - start_time))

        except AssertionError as e:
            console.print(f"[bold red]Test case '{t.stem}' failed: {e}")
            results.append(TestResult(t.stem, "message passing", False, False, time.perf_counter() - start_time))

    return results


def compile_test_case(compiler, source_file, test_fail):
    compile_result = subprocess.run(
        [compiler, source_file, "--mock"],
        capture_output=True,
        text=True
    )
    
    net_result = (compile_result.stdout + compile_result.stderr).lower()
    
    if compile_result.returncode == 0 and test_fail:
        raise AssertionError(f"Actual Output: {net_result}\nCompile was successful when it should have failed.")
    elif compile_result.returncode != 0 and not test_fail:
        raise AssertionError(f"{compile_result.stderr}\nActual Output: {net_result}\nCompile was successful when it should have failed.")

def run_compile_test_cases(compiler, workdir, filter, test_fail):
    if test_fail:
        test_sources = workdir / "test_fail_compile"
    else:
        test_sources = workdir / "test_pass_compile"
    
    test_cases = [t for t in test_sources.iterdir() if t.is_file() and t.name.lower().endswith(".c")]
    
    category_name = f"{'fail' if test_fail else 'pass'} compile"
    
    console.print(f"\n[bold black]Discovered {len(test_cases)} test cases in \"{category_name}\" category.")
    console.print(f"Starting testing now...")

    if filter:
        test_cases.sort(key=lambda e: 1 if filter in e.stem else 0)

    results = []

    for i in range(len(test_cases)):
        t = test_cases[i]
        with console.status(f"[bold cyan]Running test case {i + 1}/{len(test_cases)}: {t.stem}"):
            if filter and filter not in t.stem:
                console.print(f"[bold][dim]Test case {t.stem} was skipped: did not match filter.")
                
                results.append(TestResult(t.stem, category_name, False, True, 0))
                continue
            
            start_time = time.perf_counter()
    
            try:
                compile_test_case(compiler, t, test_fail)
                console.print(f"[bold green]Test case '{t.stem}' passed!")
                
                results.append(TestResult(t.stem, category_name, True, False, time.perf_counter() - start_time))
            except AssertionError as e:
                console.print(f"[bold red]Test case '{t.stem}' failed: {e}")
                results.append(TestResult(t.stem, category_name, False, False, time.perf_counter() - start_time))

    return results

def run_test_cases(compiler, workdir, filter, skip):
    results = run_execute_test_cases(workdir, filter, skip)
    results += run_compile_test_cases(compiler, workdir, filter, True)
    results += run_compile_test_cases(compiler, workdir, filter, False)
    results += run_messagepassing_test_cases(workdir, filter)

    return results

def load_config() -> ProjectConfig:
    try:
        with open(PROJECT_CONFIG_FILE, "r") as f:
            cfg = yaml.safe_load(f)
            
            skip_tests = []
            
            if "skip_tests" in cfg["toolchain"]:
                skip_tests = cfg["toolchain"]["skip_tests"]
            
            return ProjectConfig(
                compiler_build_dir=Path(cfg["toolchain"]["compiler"]["build"]),
                compiler_invoke_bin=Path(cfg["toolchain"]["compiler"]["invoke"]),
                isa=Path(cfg["toolchain"]["isa"]),
                platform_build_dir=Path(cfg["toolchain"]["platform"]["build"]),
                platform_libs=[Path(p) for p in cfg["toolchain"]["platform"]["lib"]],
                skip_tests=skip_tests
            )
    except FileNotFoundError:
        print(f"Could not locate project directory. Please ensure you are in a daedalus project directory with a '{PROJECT_CONFIG_FILE}' file.", file=sys.stderr)
        exit(1)

def print_test_summary(results: List[TestResult]):
    num_skipped = len([x for x in results if x.skipped])
    num_fail = len([x for x in results if not x.skipped and not x.passed])
    num_pass = len([x for x in results if not x.skipped and x.passed])

    if num_fail == 0:
        result = f"[green]✔ All {num_pass} tests passed."
        
        if num_skipped > 0:
            result += f" Skipped {num_skipped} test cases."
        
        console.print(result)
    else:
        console.print(f"[red bold]✖ One or more test cases failed. Only {num_pass} / {num_fail + num_pass} tests passed with {num_skipped} tests skipped.")


def generate_test_report(dest: Path, results: List[TestResult]):
    dest.mkdir(exist_ok=True, parents=True)
    
    coverage = dest / "coverage.csv"
    
    with open(coverage, "w") as f:
        f.write("source, category, passed, has_coverage\n")
        
        for t in results:
            coverage = "true"
            if t.skipped:
                continue
            
            if t.category == "compile fail":
                coverage = "true" if not t.passed else "false"
            else:
                coverage = "true" if t.passed else "false"
        
            f.write(f"{t.name}.c, {t.category}, {'true' if t.passed else 'false'}, {coverage}\n")
    
    
    runtime = dest / "runtime.csv"
    with open(runtime, "w") as f:
        f.write("source, category, passed, runtime_secs\n")
        
        for t in results:
            if t.skipped:
                continue
            
            f.write(f"{t.name}.c, {t.passed}, {t.runtime_seconds:.2f}\n")     

def main():
    p = ArgumentParser(description="A utility to run a set of standard test suite against a Daedalus generated architecture.")
    p.add_argument("--test-dir", help="Where to setup and perform the automated tests. Defaults to a temporary directory that is discarded after testing.")
    p.add_argument("--keep-temp", action="store_true", help="When using a temp directory (ie test-dir is not specified), tells the tool to keep the temp directory after exit.")
    p.add_argument("--overwrite", action="store_true", help="Allow for overwriting if the test working directory already exists.")
    p.add_argument("--filter", help="A name filter to apply to test cases", default=None)
    p.add_argument("--skip", nargs="*", help="A skip list to apply to test cases", default=None)
    p.add_argument("--report", help="Output directory where reporting metrics are placed", default=None)
    p.add_argument("--setup-only", help="Only setup & build test directory & dependencies, do not run any tests.", default=False, action="store_true")
    p.add_argument("--test-config", help="Test a configuration file.", default=None, type=Path)
    args = p.parse_args()
    
    templates_path = Path(user_data_dir("daedalus", "jeremy-wildsmith"))
    os.makedirs(templates_path, exist_ok=True)

    with create_temp_project(templates_path, args.test_config):
        cfg = load_config()

        with working_directory(args.test_dir, args.keep_temp, args.overwrite) as workdir:
            console.print(f"Preparing and running test cases in working directory: {workdir}")
            setup_test_directory(cfg, workdir)
            
            if args.setup_only:
                console.print(f"[green]Test directory has been created and setup for use: {workdir}")
                return
            
            results = run_test_cases(cfg.compiler_invoke_bin, workdir, args.filter, args.skip)
            
            print_test_summary(results)
            
            if args.report:
                generate_test_report(Path(args.report), results)

if __name__ == "__main__":
    main()