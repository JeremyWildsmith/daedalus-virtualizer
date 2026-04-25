# Index of Testing / Verification / Validation Artifacts

### Verification and Validation - Artifacts produced to verify and validate success criteria

| Path | Description |
|---|---|
| `./testing/foundry/*.json` | Individual Foundry synthesized test archetype definitions which are tested and verified to produce test logs showing synthesis stability. |
| `./testing/foundry/logs/*.log` | Test logs produced when testing the Foundry synthesized security toolchains through the `dacpu-test` command. |
| `./testing/labyrinth/*.json` | Equivalent synthesized test manifests for the Labyrinth archetype. Verifies the second archetype, Labyrinth. |
| `./testing/labyrinth/logs/*.log` | Runtime logs for Labyrinth toolchain tests, produced with `dacpu-test`. |
| `./testing/labyrinth/logs/tea.log` | Benchmark or execution log for the TEA encryption workload under Labyrinth. The full test suite is not completed; the purpose is to demonstrate that Labyrinth is capable of completing the TEA verification tests, although it takes significant time to complete. |

---

### A User Example - Key Verification System - Artifacts for User Manual / How-to for Daedalus

| Path | Description |
|---|---|
| `./testing/demo/main.demo.c` | Demonstration host-side application source code used in the User Manual key verification example. Represents the unsecured application partition. |
| `./testing/demo/main.demo.enclave.c` | Protected enclave-side source code for the key verification demo. Represents secured user logic executing inside the synthesized enclave. |

---

### Metrics of Compiled Artifacts & Analysis of Resulting Binary - Artifacts for qualitative success metrics

| Path | Description |
|---|---|
| `./testing/analysis/foundry_unprotected.asm` | Baseline disassembly of firmware without protection layers enabled. Useful control sample for comparison against remapped or encrypted builds. |
| `./testing/analysis/foundry_unprotected_firmware.bin` | Raw baseline firmware image for Foundry with minimal protections enabled. |
| `./testing/analysis/foundry_remapped_opcodes.asm` | Disassembly demonstrating opcode remapping variation. Shows ISA divergence from normal RISC-V semantics. |
| `./testing/analysis/foundry_instructions_encrypted.asm` | Artifact showing encrypted instruction disassembly. |
| `./testing/analysis/foundry_instructions_encrypted_firmware.bin` | Protected firmware binary with instruction encryption enabled. |
| `./testing/analysis/foundry_firmware_encrypted_ram.bin` | Protected Foundry firmware output demonstrating memory encryption. |
| `./testing/analysis/labyrinth_unprotected.asm` | Baseline disassembly for Labyrinth software virtualization layer without added protections. |
| `./testing/analysis/labyrinth_unprotected_firmware.binvm.ebp` | Labyrinth firmware dump with memory encryption disabled, used to establish a baseline for testing with encryption enabled. |
| `./testing/analysis/labyrinth_remapped_opcodes.asm` | Artifact demonstrating eBPF opcode remapping within Labyrinth. |
| `./testing/analysis/labyrinth_instructions_encrypted.asm` | Disassembly listing with instruction encryption enabled. |
| `./testing/analysis/labyrinth_instructions_encrypted_firmware.binvm.ebp` | Protected Labyrinth firmware output demonstrating memory encryption. |
| `./testing/analysis/perf.data` | Linux perf sampling data used to identify process threads simulating the Verilator RTL logic. |
| `./testing/analysis/trace.dat` | trace-cmd / KernelShark scheduler trace showing concurrent Daedalus kernel execution. |
| `./testing/analysis/secure_app_encoder.c` | Source file of an enclave implementation used to demonstrate the consequence of encrypting and not encrypting secure-enclave memory. |
| `./testing/analysis/core.5817` | Memory dump of a Foundry archetype secure enclave with the memory encryption feature disabled. |
| `./testing/analysis/core.6905` | Memory dump of a Foundry archetype secure enclave demonstrating the property of memory encryption. |
