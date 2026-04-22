FROM python:3.10-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl

# Create a non-root user (like devcontainers do)
RUN groupadd --gid 1000 vscode \
    && useradd --uid 1000 --gid 1000 -m vscode -s /bin/bash

# Install uv for the non-root user
USER vscode
ENV HOME=/home/vscode

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="${HOME}/.cargo/bin:${PATH}"

user root
RUN curl -L "https://github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases/download/v15.2.0-1/xpack-riscv-none-elf-gcc-15.2.0-1-linux-x64.tar.gz" \
      -o /tmp/riscv-none-elf-gcc.tar.gz && \
    mkdir -p /opt/riscv32 && \
    tar -xzf /tmp/riscv-none-elf-gcc.tar.gz -C /opt/riscv32 --strip-components=1 && \
    rm /tmp/riscv-none-elf-gcc.tar.gz

ENV RISCV_GNU_TOOLCHAIN_INSTALL_PREFIX=/opt/riscv32
ENV PATH="${RISCV_GNU_TOOLCHAIN_INSTALL_PREFIX}/bin:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    verilator \
    make \
    g++ \
    libncurses5-dev libncursesw5-dev \
    procps \
    && rm -rf /var/lib/apt/lists/*


# Some developer tools...
RUN apt-get update && apt-get install -y --no-install-recommends \
    git

#RUN echo "deb http://deb.debian.org/debian unstable main" > /etc/apt/sources.list.d/sid.list

#RUN apt-get update && \
#    apt-get install -y -t unstable radare2 && \
#    apt-get install -y clang libzmq3-dev xxd yq

RUN apt-get update && apt-get install -y clang libzmq3-dev xxd yq

RUN pip install shiv

#RUN apt-get update && apt-get install -y lld-21 binutils-bpf
RUN apt-get update && apt-get install -y binutils-bpf

RUN apt-get update && apt-get install -y --no-install-recommends \
    clang libzmq3-dev xxd yq \
    git make gcc pkg-config libc6-dev ca-certificates curl xz-utils patch \
    && rm -rf /var/lib/apt/lists/*

RUN curl -Ls https://github.com/radareorg/radare2/releases/download/6.1.2/radare2-6.1.2.tar.xz \
    | tar -xJ -C /tmp && \
    cd /tmp/radare2-6.1.2 && \
    sys/install.sh --without-pull && \
    rm -rf /tmp/radare2-6.1.2

RUN apt-get update && apt-get install -y gdb gcc-bpf
user vscode

workdir /workspaces