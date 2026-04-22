from jinja2 import Environment, FileSystemLoader
from constraint import Problem, AllEqualConstraint, AllDifferentConstraint
import hashlib
from typing import NamedTuple, Dict, Any, Set, Tuple, List, Optional
from pathlib import Path
import functools

env = Environment(
    loader=FileSystemLoader("."),
    variable_start_string="[[[",
    variable_end_string="]]]",
)

_TEMPLATE_FILE_EXT = (".j2", ".jinja", ".jinja2")

class ComponentSpecification(NamedTuple):
    name: str
    compiler_hooks: Dict[str, str]
    platform_hooks: Dict[str, str]
    exclusive_section_allocation: Set[str]
    config_toggle: Optional[str]
    config_state: bool

class ArchitectureSpecification(NamedTuple):
    variables: Dict[str, Any]
    components: List[ComponentSpecification]
    compiler_base: Path
    platform_base: Path
    remapped_encodings: bool
    multiple_kernels: bool

def _build_ebpf_bit_patterns():
    return {
        "alu64_add_k": 7,
        "alu64_add_x": 15,
        "alu64_sub_k": 23,
        "alu64_sub_x": 31,
        "alu64_mul_k": 39,
        "alu64_mul_x": 47,
        "alu64_div_k": 55,
        "alu64_div_x": 63,
        "alu64_mod_k": 151,
        "alu64_mod_x": 159,
        "alu64_and_k": 87,
        "alu64_and_x": 95,
        "alu64_or_k": 71,
        "alu64_or_x": 79,
        "alu64_xor_k": 167,
        "alu64_xor_x": 175,
        "alu64_mov_k": 183,
        "alu64_mov_x": 191,
        "alu64_neg": 135,
        "alu64_lsh_k": 103,
        "alu64_lsh_x": 111,
        "alu64_rsh_k": 119,
        "alu64_rsh_x": 127,
        "alu64_arsh_k": 199,
        "alu64_arsh_x": 207,
        "ldx_mem_b": 113,
        "ldx_mem_h": 105,
        "ldx_mem_w": 97,
        "ldx_mem_dw": 121,
        "stx_mem_b": 115,
        "stx_mem_h": 107,
        "stx_mem_w": 99,
        "stx_mem_dw": 123,
        "st_mem_b": 114,
        "st_mem_h": 106,
        "st_mem_w": 98,
        "st_mem_dw": 122,
        "jmp_ja": 5,
        "jmp_jeq_k": 21,
        "jmp_jeq_x": 29,
        "jmp_jne_k": 85,
        "jmp_jne_x": 93,
        "jmp_jgt_k": 37,
        "jmp_jgt_x": 45,
        "jmp_jge_k": 53,
        "jmp_jge_x": 61,
        "jmp_jset_k": 69,
        "jmp_jset_x": 77,
        "jmp_jsgt_k": 101,
        "jmp_jsgt_x": 109,
        "jmp_jsge_k": 117,
        "jmp_jsge_x": 125,
        "jmp_jslt_k": 197,
        "jmp_jslt_x": 205,
        "jmp_jsle_k": 213,
        "jmp_jsle_x": 221,
        "jmp_call": 133,
        "jmp_exit": 149,
        "ldimm64": 24
    }

def _build_rsicv_bit_patterns():
    return {
        "opcode_alur":   "0110011",
        "opcode_opimm":  "0010011",
        "opcode_jal":    "1101111",
        "opcode_jalr":   "1100111",
        "opcode_lui":    "0110111",
        "opcode_auipc":  "0010111",
        "opcode_branch": "1100011",
        "opcode_store":  "0100011",
        "opcode_load":   "0000011",

        "funct3_add_sub": "000",
        "funct3_addi":    "000",
        "funct3_sll":     "001",
        "funct3_slt":     "010",
        "funct3_sltu":    "011",
        "funct3_xor":     "100",
        "funct3_srx":     "101",
        "funct3_or":      "110",
        "funct3_and":     "111",

        "funct7_rtype_base": "0000000",
        "funct7_add":        "0000000",
        "funct7_srl":        "0000000",
        "funct7_sub":        "0100000",
        "funct7_sra":        "0100000",

        "funct3_beq":  "000",
        "funct3_bne":  "001",
        "funct3_blt":  "100",
        "funct3_bge":  "101",
        "funct3_bltu": "110",
        "funct3_bgeu": "111",

        "funct3_sb": "000",
        "funct3_sh": "001",
        "funct3_sw": "010",

        "funct3_lb":  "000",
        "funct3_lh":  "001",
        "funct3_lw":  "010",
        "funct3_lbu": "100",
        "funct3_lhu": "101",

        "funct3_jalr": "000",
    }


def _build_constraints(constraints, variables):
    p = Problem()
    disjoint_names = {}
    
    p.addVariables(variables, range(len(variables)))
    
    common = set()
    group_keys = set()
    
    constraints = constraints or {}
    
    for overlap in constraints.get("overlaps", []):
        common = common.union(set(overlap))
        group_keys.add(overlap[0])
    
    for overlap in constraints.get("overlaps", []):
        decl = set(overlap).intersection(set(variables))
        p.addConstraint(AllEqualConstraint(), list(decl))
        others = group_keys.difference(decl)
        p.addConstraint(AllDifferentConstraint(), list([overlap[0]]) + list(others))
        
        for overlap2 in constraints.get("overlaps", []):
            if overlap == overlap2:
                continue
            
            p.addConstraint(AllDifferentConstraint(), list([overlap[0], overlap2[0]]))
    
    disjoint = set(variables).difference(common).union(group_keys)
    p.addConstraint(AllDifferentConstraint(), list(disjoint))

    for disjoint in constraints.get("disjoint", []):
        decl = set(disjoint).intersection(set(variables))
        p.addConstraint(AllDifferentConstraint(), list(decl))
        
        for d in decl:
            disjoint_names[d] = decl.difference(set([d]))
    
    solution = p.getSolution()
    
    if not solution:
        raise Exception("Could not solve synthesis variable constraints.")
    
    return solution, disjoint_names
    
def _create_bit_value(seed, name, bit_size, reserved):
    i = 0
    while True:
        bitfield_seed = f"{seed}-{name}-{i}"
        i += 1
        
        hashed = hashlib.sha256(bitfield_seed.encode())
        result = int(hashed.hexdigest(), 16) % (2 ** bit_size)
        
        bitcode = bin(result)[2:].zfill(bit_size)

        if bitcode not in reserved:
            return bitcode

def _create_int_value(seed, name, reserved, val_min, val_max):
    i = 0
    while True:
        bitfield_seed = f"{seed}-{name}-{i}"
        i += 1
        
        hashed = hashlib.sha256(bitfield_seed.encode())
        result = val_min + (int(hashed.hexdigest(), 16) % val_max)

        if result not in reserved:
            return result

    
def _build_bitfields(seed, fields, constraints):
    size_map = {x["name"]: x["bits"] for x in fields}
    
    p, disjoint_names = _build_constraints(constraints, list(size_map.keys()))

    val_mapping = {}
    
    result = {}
    
    name_list = list(size_map.keys())
    name_list.sort()
    
    for name in name_list:
        colour = p[name]

        if colour not in val_mapping:            
            block_list = []
            
            if name in disjoint_names:
                block_list = [result[n] for n in disjoint_names[name] if n in result]

            val_mapping[colour] = _create_bit_value(seed, name, size_map[name], block_list)

        result[name] = val_mapping[colour]
    
    return result


    
def _build_intfields(seed, fields, constraints):
    size_map = {x["name"]: (x["min_val"], x["max_val"]) for x in fields}
    
    p, disjoint_names = _build_constraints(constraints, list(size_map.keys()))

    val_mapping = {}
    
    result = {}
    
    name_list = list(size_map.keys())
    name_list.sort()
    
    for name in name_list:
        colour = p[name]

        if colour not in val_mapping:            
            block_list = []
            
            if name in disjoint_names:
                block_list = [result[n] for n in disjoint_names[name] if n in result]

            val_mapping[colour] = _create_int_value(seed, name, block_list, *size_map[name])

        result[name] = val_mapping[colour]
    
    return result

def is_synthesis_file(file):
    return file.suffix.lower() in _TEMPLATE_FILE_EXT

def load_hooks(database, config) -> Tuple[Dict[str, str], Set[str]]:
    alloc = set()
    r = {}

    for hook_name, hook_config in config.items():
        source = database / hook_name
        
        if hook_config.get("exclusive", False):
            alloc.add(hook_name)
        
        if source.exists():
            with open(source, "r") as f:
                r[hook_name] = f.read()

    return r, alloc

def load_component_specification(database, config) -> ComponentSpecification:
    name = config.get("name")
    key = config.get("key")
    config_toggle = config.get("config_toggle", {}).get("key", None)
    config_state = config.get("config_toggle", {}).get("state", True)
    
    source = Path(database) / key
    
    if not source.exists():
        raise Exception(f"Variation source directory does not exist in database: {source}")
    
    compiler_hooks: Dict[str, str] = {}
    platform_hooks: Dict[str, str] = {}
    exclusive_section_allocation: Set[str] = set()
    
    hooks = config.get("hooks")
    if not hooks:
        return ComponentSpecification(name, compiler_hooks, platform_hooks, exclusive_section_allocation)
    
    compiler_hooks, compiler_section_alloc = load_hooks(source / "compiler", hooks.get("compiler") or {})
    platform_hooks, platform_section_alloc = load_hooks(source / "platform", hooks.get("platform") or {})

    exclusive_section_allocation = compiler_section_alloc.union(platform_section_alloc)
    
    return ComponentSpecification(
        name,
        compiler_hooks,
        platform_hooks,
        exclusive_section_allocation,
        config_toggle,
        config_state
    )

def load_variations(working_directory, arch_spec) -> List[ComponentSpecification]:
    config = arch_spec.get("variations")
    
    source = working_directory / config.get("database")
    
    loaded = []
    for c in config.get("index", []):
        loaded.append(load_component_specification(source, c))
    
    return loaded

def synthesize_variation_configuration(seed, loaded: List[ComponentSpecification]) -> List[ComponentSpecification]:
    r = [l for l in loaded if l.name in ["Swap Operands", "Normal Operands"]]
    
    if len(r) != 2:
        raise Exception("Unexpected number of variations.")
    
    r = [r[int(seed) % len(r)]]
    return r

def validate_variation_selection(config, variations: List[ComponentSpecification]):    
    required = config.get("variations").get("required_sections")
    
    selected_sections = set()
    for v in variations:
        selected_sections = selected_sections.union(
            set(v.compiler_hooks.keys())
            .union(set(v.platform_hooks.keys()))
        )
        
    for r in required:
        if r not in selected_sections:
            raise ValueError(f"Required section {r} is missing. You must select a variation that covers this.")
        
    for v in variations:
        exclusive = set(v.exclusive_section_allocation)
        for o in variations:
            if o == v:
                continue
            
            other_allocation = set(o.compiler_hooks.keys()).union(set(o.platform_hooks.keys())).union(set(o.exclusive_section_allocation))
            
            overlap_exclusive = other_allocation.intersection(exclusive)
            if overlap_exclusive:
                raise ValueError(f"Variation {v.name} wants exclusive control of sections but it conflicts with variation {o.name}. Sections: {','.join(overlap_exclusive)}")

def synthesize_architecture(seed, working_directory, config, variations, remap_encodings, multiple_kernels) -> ArchitectureSpecification:
    vars = config.get("variables")

    bit_patterns = {}
    int_patterns = {}
    
    if "bitstrings" in vars:
        c = vars.get("bitstrings")
        bit_patterns = _build_bitfields(seed, c.get("declarations", []), c.get("constraints"))

    if "int" in vars:
        c = vars.get("int")
        int_patterns = _build_intfields(seed, c.get("declarations", []), c.get("constraints"))
    
    remapped_encodings = remap_encodings
    
    if not remap_encodings:
        bit_patterns |= _build_rsicv_bit_patterns()
        int_patterns |= _build_ebpf_bit_patterns()

    all_vars = int_patterns | bit_patterns
    
    compiler_base = working_directory / config.get("toolchain").get("compiler").get("build")
    platform_base = working_directory / config.get("toolchain").get("platform").get("build")
    
    return ArchitectureSpecification(all_vars, variations, compiler_base, platform_base, remapped_encodings, multiple_kernels)

def render_section(spec: ArchitectureSpecification, is_compiler_template, section_name):
    r = None
    for c in spec.components:
        hooks = c.compiler_hooks if is_compiler_template else c.platform_hooks
        
        section = hooks.get(section_name, None)
        
        if not section:
            continue
        
        t = env.from_string(section)
        rendered = t.render(**spec.variables)
        
        r = (r or "") + rendered + "\n\n"

    if r is None:
        return ""
        #raise Exception(f"Missing section that should have been available during synthesis: '{section_name}'")
    
    return r

def apply_synthesis(project_name, spec: ArchitectureSpecification, file):    
    with open(file, "r") as f:
        t = env.from_string(f.read())
        
        if file.resolve().is_relative_to(spec.compiler_base.resolve()):
            env.globals["render_section"] = functools.partial(render_section, spec, True)
        elif file.resolve().is_relative_to(spec.platform_base.resolve()):
            env.globals["render_section"] = functools.partial(render_section, spec, False)
        else:
            env.globals["render_section"] = None
        
        effective_vars = dict(spec.variables)
        effective_vars["project_name"] = project_name
        
        if spec.multiple_kernels:
            effective_vars["multiple_kernels"] = True
        else:
            effective_vars["multiple_kernels"] = False
        
        result = t.render(**effective_vars)
    
    with open(file.with_suffix(""), "w") as f:
        f.write(result)
    
    file.unlink()
