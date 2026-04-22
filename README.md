# Daedalus

Daedalus is a toolchain to develop applications using the code virtualization based code obfuscation pattern and it works by generating security toolchains which consist of a compiler portion and interpreter portion, each with various variations injected into them for each generation. The generated toolchain is a co-synthesized pair, the compiler portion of the generates code and the interpreter portion executes it.


The core idea behind Daedalus, and what makes it an interesting application of code-virtualization based obfuscation is that it extrapolates the idea of code obfuscation by virtualization beyond a software interpreter and as close to a hardware interpreter core as possible while being constrainted in a software system. Daedalus achieves this by leveraging the Verilator hardware description language simulation tool. 

---

## How It Works

Daedalus synthesizes a **security toolchain** for each project. This toolchain consists of:

- A compiler that translates protected C code into a generated private ISA / schema
- A runtime interpreter that executes that schema
- A secure enclave platform realized through simulated RTL hardware using Verilator
- A message passing layer allowing protected and unprotected code to communicate

From the perspective of a user (developer), you develop your application as two discrete sub-applications which communicate via message passing. One portion executes in a regular environment and does not suffer any performance penalty, while the other portion executes in the highly constrainted secure enclave where it trades performance off for security.

Daedalus' toolchain synthesis pipelines makes every attempt to work such that no two generated security-toolchains are alike. Different synthesis seeds and feature selections can produce unique execution platforms, opcode layouts, encryption keys, compiler code generation semantics, and behavioral variations.

---

## Daedalus User Model

Daedalus applications are generally split into three parts:

1. Unprotected Application Code  
   Normal host-side code such as UI, networking, file handling, or user interaction.

2. Protected Application Code  
   Security-sensitive logic compiled into the Daedalus enclave.

3. Daedalus Simulation Server  
   Bridges communication between the host application and the secure enclave.

This allows developers to keep performance-sensitive or ordinary code native, while isolating only critical algorithms inside the protected environment.

Example use cases:

- DRM or license enforcement
- Anti-tamper routines
- Proprietary algorithms

---

## Security Features

Depending on archetype and configuration, Daedalus can synthesize toolchains with features such as:

- Randomized instruction encodings
- Instruction encryption
- Memory encryption
- Memory layout scrambling
- Operand remapping / semantic variation
- Concurrent execution of the virtualized core (i.e the RTL Simulation of the secure encalve core is partitioned and executed concurrently on multiple system cores.)
- Multi-layer virtualization (Labyrinth Archetype)

These features are intended to increase the effort required for static analysis and reverse engineering.

---

## Included Archetypes

### Foundry

A modified RISC-V based secure enclave implemented in Verilog and compiled through Verilator.

### Labyrinth

Built over Foundry, Labyrinth adds an additional software virtualization layer using a protected eBPF-style VM. This creates multiple layers of code virtualization. It also allow for another layer of instruction encryption to become available.

---

## Quick Start - Docker

```bash
git clone https://github.com/JeremyWildsmith/daedalus-virtualizer.git
cd daedalus-virtualizer
docker build . --tag daedalus
docker run --rm -it daedalus
```

Once inside the container:

```bash
# Create a user project
dacpu-init
cd ./<project-name>
make
#execute the generated binary image
cd ./bin/<project-name>
```

---

## Creating a Project

Use the project wizard:

```bash
dacpu-init
```

This interactive setup allows you to configure your Daedalus project and security toolchain.

After generation:

```bash
cd my-project
dacpu-test
make
```

---

## Example Use Case

Consider a scenario where a software vendor wants to protect their license verification logic. Instead of shipping the verification routine directly in native code, the algorithm is placed inside the Daedalus secure enclave. The user interface and normal application logic remain native, while only the verification logic executes inside the protected environment.

You can experiment with this use case, by following the guide below:
1. Create a new Daedalus project with a security toolchain using the command `dacpu-init`
2. Navigate into the template `main.c` file created for the template. Replace it with a simple validation CLI interface. Notice how the key validation logic is deferred to the Daedalus secure enclave:
```
#include <daedalus.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>
#include <stdio.h>

void read_line(struct daedalus_ctx* ctx, char* buffer, int buffer_len) {
    int i;
    for(i = 0; i < buffer_len - 1;) {
        uint8_t c;
        int n = read_enclave(ctx, &c, 1);
        if(n > 0) {
            if(c == '\n') break;
            else buffer[i++] = c;
        }
    }
    buffer[i] = 0;
}

int main() {
    char name[256];
    char key[256];
    char buffer[256];
    struct daedalus_ctx* ctx = create_enclave_session();

    printf("Welcome to the Key Verification System... System is starting up...\n");
    sleep(3);

    printf("Enter your name: ");
    fgets(name, sizeof(name) - 1, stdin);
    write_enclave(ctx, (uint8_t*)&name, strlen(name));
    printf("Enter your product key: ");
    fgets(key, sizeof(key) - 1, stdin);
    write_enclave(ctx, (uint8_t*)&key, strlen(key));

    printf("Please wait while validate your key...\n");

    read_line(ctx, buffer, sizeof(buffer));
    printf("\n");

    if(strcmp(buffer, "VALID") == 0) {
        name[strlen(name) - 1] = 0;
        key[strlen(key) - 1] = 0;
        printf("You have captured the flag! FLAG={'%s', %s}", name, key);
    } else {
        printf("Sorry, that isn't the right product key. Try again :)\n");
    }
    return 0;
}
```
3. Navigate into the secure enclave portion, and implement the key validation logic:
```
#include "firmware.h"

void read_str(unsigned char* buf, int max_read, unsigned char stopchar)
{
    int i;
    for(i = 0; i < max_read - 1; i++) {
        while(!firmware_read(&buf[i]))
            continue;
        
        if(!buf[i] || buf[i] == stopchar)
            break;
    }

    buf[i] = 0;
}

void print_str(const char *p)
{
	while (*p != 0)
		firmware_write(*(p++));
}

unsigned long build_key(char* key) {
    unsigned long hash = 5381;
    int c;

    while ((c = *key++)) {
        hash = ((hash << 5) + hash) + c;
    }

    return hash;
}

//We source this from: https://en.wikipedia.org/wiki/Linear_congruential_generator
unsigned int lcg_step(unsigned int current) {
    return current * 1664525u + 1013904223u;
}

//For "Jeremy Wildsmith" the key should be: 8p63qr85-mdo7m7s7-g705q34b-q54vs76h
int compare_key(char* key, unsigned long key_hash) {
    int ki = 0;

    if(!key[ki])
        return 0;

    for(int w = 0;; w++) {
        for(int i = 0; i < 8; i++) {
            if(!key[ki])
                return 0;

            int lower = key_hash % 3 ? 48 : 97;
            int upper_r = key_hash % 3 ? 57 : 122;
            
            char d = lower + (key_hash % (upper_r - lower + 1));

            if(key[ki++] != d)
                return 0;

            key_hash = lcg_step(key_hash);
        }

        if(w < 3) {
            if(key[ki++] != '-')
                return 0;
        } else {
            break;
        }
    }
    
    if(key[ki])
        return 0;

    return 1;
}

void main() {
    char name[256];
    char key[256];
	
	for(;;) {
	    read_str(name, sizeof(name), '\n');
	    read_str(key, sizeof(key), '\n');
        unsigned long hash = build_key(name);

        //To prevent bruteforcing, lets add a busy loop.
        for(int i = 0; i < 1000; i++) {
            name[i % 10] = name[(i + 1) % 10] * name[(i + 2) % 10];
        }

	    if(compare_key(key, hash))
            print_str("VALID\n");
        else
            print_str("NOT_VALID\n");
	}
}
```
4. Use the make command to generate the secure binary. Invoke the binary in ./bin/secure-app, see if you can capture the flag without looking at the source code :)

## License

MIT License (See LICENSE and LICENSE-3RD-PARTY)

## Author

Jeremy Wildsmith  
BCIT COMP 8047 Major Project
