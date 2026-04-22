from .synthesis import ComponentSpecification, is_synthesis_file, apply_synthesis, validate_variation_selection, synthesize_architecture, synthesize_variation_configuration, load_variations
import questionary
import sys
from argparse import ArgumentParser
import os

from pathlib import Path
import yaml
from slugify import slugify
import re
import random
import shutil

from typing import NamedTuple, List
from .common import PROJECT_CONFIG_FILE


from rich.console import Console, Group
from rich.table import Table
from rich.text import Text

from rich.progress import Progress
from pydantic import TypeAdapter
from platformdirs import user_data_dir

console = Console()

TEMPLATE_CONFIG_FILE = 'dacpu-template.yaml'

class ProjectConfiguration(NamedTuple):
    name: str
    seed: int
    architecture_name: str
    architecture_id: str
    components: List[str]
    variations: List[ComponentSpecification]
    remap_isa_encodings: bool
    multiple_kernels: bool


class ArchetypeTemplate(NamedTuple):
    name: str
    description: str
    cost: int
    path: Path

def initialize_project(src, dest) -> List[Path]:
    jinja_files = []
    
    files = [p for p in src.rglob("*") if p.is_file()]
    total = len(files)
    
    if dest.exists():
        print("Error, the project directory already exists. Aborting project creation.", file=sys.stderr)
        exit(1)
        
    with Progress() as progress:
        task = progress.add_task("Preparing project", total=total)
        
        for file in files:
            relative = file.relative_to(src)
            target = dest / relative
            target.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(file, target)
            
            if is_synthesis_file(file):
                jinja_files.append(target)

            progress.update(task, advance=1)
    
    return jinja_files


def emplace_template(project_name, architecture, template_files):
    # Now apply synthesis results...
    with Progress() as progress:
        task = progress.add_task("Applying synthesis template parameters...", total=len(template_files))
        
        for f in template_files:
            progress.update(task, advance=1)
            apply_synthesis(project_name, architecture, f)

def select_variations(seed, source, arch_spec_config, enabled_components, use_defaults):    
    variations = load_variations(source, arch_spec_config)
    
    def build_component_config_variations():
        r = []
        for v in variations:
            if not v.config_toggle:
                continue
            
            if (v.config_toggle in enabled_components) == v.config_state:
                r.append(v)
        
        return r
    
    randomize_variations = use_defaults or questionary.confirm("Do you want variations randomized? (Reccomended)").ask()
    
    if randomize_variations:
        variation_config = synthesize_variation_configuration(seed, variations)
        variation_config += build_component_config_variations()
    else:
        available_options = [x.name for x in variations if not x.config_toggle]

        console.print("[cyan]Note that some variations are required and some are not compatible with others.")
        console.print("[cyan]For details please refer to the template config file.")
        
        while True:
            try:
                selected_variations = questionary.checkbox(
                    "Select Variations to Apply", choices=available_options
                ).ask()
                
                variation_config = [v for v in variations if v.name in selected_variations] #[v for v in variations if v.name in selected_variations]
                variation_config += build_component_config_variations()
                validate_variation_selection(arch_spec_config, variation_config)
                break
            except ValueError as e:
                console.print(f"[bold red]Invalid variation selection: {e}")
    
    return variation_config
    
    
"""
def configure_architecture(seed, arch_spec_config, dest, use_defaults):
    variations = load_variations(dest, arch_spec_config)
    
    randomize_variations = use_defaults or questionary.confirm("Do you want variations randomized? (Reccomended)").ask()
    remap_encodings = use_defaults or questionary.confirm("Do you want instruction encodings randomized? (Reccomended)").ask()
    
    if randomize_variations:
        variation_config = synthesize_variation_configuration(seed, variations)
    else:
        available_options = [x.name for x in variations]

        console.print("[cyan]Note that some variations are required and some are not compatible with others.")
        console.print("[cyan]For details please refer to the template config file.")
        
        while True:
            try:
                selected_variations = questionary.checkbox(
                    "Select Variations to Apply", choices=available_options
                ).ask()
                
                variation_config = [v for v in variations if v.name in selected_variations]
                validate_variation_selection(arch_spec_config, variation_config)
                break
            except ValueError as e:
                console.print(f"[bold red]Invalid variation selection: {e}")
    
    return synthesize_architecture(seed, dest, arch_spec_config, variation_config, remap_encodings)
"""

def create_project(config: ProjectConfiguration, template_directory: Path, destination_directory: Path) -> Path:
    architecture_yaml = template_directory / config.architecture_id / TEMPLATE_CONFIG_FILE

    with open(architecture_yaml, "r") as f:
        arch_spec_config = yaml.safe_load(f)
    
    source_dir = architecture_yaml.parent
    dest_dir = destination_directory.resolve() / slugify(config.name)

    template_files = initialize_project(source_dir, dest_dir)

    architecture = synthesize_architecture(
        config.seed,
        dest_dir,
        arch_spec_config,
        config.variations,
        config.remap_isa_encodings,
        config.multiple_kernels
    )

    emplace_template(config.name, architecture, template_files)
    
    print("Setting up project configuration...")
    old_config = dest_dir / architecture_yaml.name
    
    old_config.unlink()
    
    with architecture_yaml.open("r", encoding="utf-8") as f:
        toolchain = yaml.safe_load(f).get("toolchain")
    
    project_config = {
        "name": config.name,
        "architecture": config.architecture_name,
        "seed": config.seed,
        "components": config.components,
        "toolchain": toolchain
    }
    
    config_path = dest_dir / PROJECT_CONFIG_FILE
    
    with config_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            project_config,
            f,
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
        )
    
    print_summary(config)
    
    console.print("All done! Project is ready.")
    
    return dest_dir

def print_summary(config: ProjectConfiguration):    
    print()
    
    table = Table(title="Project Configuration")
        
    architecture_variations = [x.name for x in config.variations]
    component_render = [Text(f"- {t}") for t in (config.components or ["No Features Selected"])]
    variation_render = [Text(f"- {t}") for t in (architecture_variations or ["No Variations Selected"])]
    table.add_column("Field")
    table.add_column("Selection")
    table.add_row("Project Name", config.name)
    table.add_row("Generation Seed", str(config.seed))
    table.add_row("Architecture", config.architecture_name)
    table.add_row("ISA Recoding", "Yes" if config.remap_isa_encodings else "No")
    table.add_row("Multiple Kernels", "Yes" if config.multiple_kernels else "No")
    table.add_section()
    table.add_row("Features", Group(*component_render))
    table.add_section()
    table.add_row("Variations", Group(*variation_render))
    
    console.print(table)
    print()

def find_templates(templates_dir):
    root_path = Path(templates_dir)

    result = []

    for f, _, files in os.walk(root_path, followlinks=True):
        f = Path(f)
        if TEMPLATE_CONFIG_FILE in files:
            with open(f / TEMPLATE_CONFIG_FILE, 'r') as file:
                config = yaml.safe_load(file)
                name = config.get('architecture', {}).get("name", None)
                desc = config.get('architecture', {}).get("description", None)
                cost = config.get('architecture', {}).get("cost", 0)
                
                if not name:
                    print(f"Skipping template {f}; yaml file is missing an architecture/name field.", file=sys.stderr)
                    continue
                
                result.append(ArchetypeTemplate(name, desc, cost, f))
                
    return result


def creation_wizard(args, templates_path) -> ProjectConfiguration:    
    templates = find_templates(templates_path)
    
    if not templates:
        print(f"Error, could not find any templates to work with. Try installing some into the directory {templates_path}", file=sys.stderr)
        exit(1)

    seed = str(random.randint(1, 9999999999))
    templates.sort(key=lambda x: x.cost)
    selected_architecture_name = templates[0].name
    
    multiple_kernels = False
    
    if not args.use_defaults:
        project_name = slugify(questionary.text(
            "Enter your project name:",
            validate=lambda x: len(slugify(x)) > 0,
            default="secure-app"
        ).ask())
        
        seed = questionary.text(
            "Enter a generation seed:",
            validate=lambda x: x.isdigit() and len(x) < 15,
            default=seed
        ).ask()
        
        selected_architecture_name = questionary.select(
            "Which architecture do you want to use?",
            choices=[questionary.Choice(x.name, description=x.description) for x in templates],
            show_description=True
        ).ask()
        
        
        multiple_kernels = questionary.confirm("Do you want to use multiple execution kernels?", default=False).ask()

    selected_architecture_dir = next(filter(lambda x: x.name == selected_architecture_name, templates)).path
    selected_architecture_yaml = selected_architecture_dir / TEMPLATE_CONFIG_FILE
    
    with open(selected_architecture_yaml, 'r') as f:
        architecture_config = yaml.safe_load(f)
    
    remap_encodings = args.use_defaults or questionary.confirm("Do you want instruction encodings randomized? (Reccomended)").ask()
    
    enabled_components = []
    
    if not args.use_defaults:            
            possible_components = [questionary.Choice(w.get("name"), checked=w.get("default", False)) for w in architecture_config.get("components", []) if "name" in w]
            
            console.print("[bold cyan] Reccomended features are selected by default. Additional features may enhance security at the cost of performance.")
            enabled_components = questionary.checkbox(
                "Select Enabled Features", choices=possible_components
            ).ask()
            
    variations = select_variations(seed, selected_architecture_dir, architecture_config, enabled_components, args.use_defaults)

    return ProjectConfiguration(
        name=project_name,
        seed=int(seed),
        architecture_name=selected_architecture_name,
        architecture_id=selected_architecture_dir.name,
        components=enabled_components,
        variations=variations,
        remap_isa_encodings=remap_encodings,
        multiple_kernels=multiple_kernels
    )

def load_project_config(path: Path) -> ProjectConfiguration:
    adapter = TypeAdapter(ProjectConfiguration)
    with open(path, "r") as f:
        return adapter.validate_json(f.read())

def main():
    p = ArgumentParser()
    p.add_argument("--use-defaults", action="store_true")
    p.add_argument("--save-config", type=str)
    p.add_argument("--load-config", type=str)
    
    templates_path = Path(user_data_dir("daedalus", "jeremy-wildsmith"))
    os.makedirs(templates_path, exist_ok=True)
    
    args = p.parse_args()

    if args.load_config:
        config = load_project_config(args.load_config)
    else:
        config = creation_wizard(args, templates_path)
    
    if args.save_config: 
        adapter = TypeAdapter(ProjectConfiguration)      
        with open(args.save_config, "wb") as f:
            f.write(adapter.dump_json(config))
    else:
        destination_directory = create_project(config, templates_path, Path())
            
        console.print(f"[cyan bold]Next step, please test your synthesized secure enclave:[/cyan bold]")
        console.print(f"  cd {destination_directory} && dacpu-test")

if __name__ == "__main__":
    main()