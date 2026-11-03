---
title: "开发教程"
linkTitle: "开发教程"
description: "你可以使用 envd 快速搭建开发环境，它会自动创建 Docker 容器并安装所有依赖项。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/developers/development.md"
aliases:
  - "/developers/development/"
icon: fa-solid fa-hammer
---

## 搭建开发环境 {#set-up-development-environment}

你可以使用 [`envd`](https://github.com/tensorchord/envd) 轻松搭建开发环境，它会自动创建一个 Docker 容器并为你安装所有依赖项：

```sh
pip install envd
git clone https://github.com/tensorchord/pgvecto.rs.git
cd pgvecto.rs
envd up
```

或者，你也可以按照以下步骤手动搭建开发环境：

1. 安装基础依赖项：

```sh
sudo apt install -y \
    bison \
    build-essential \
    ccache \
    flex \
    gcc \
    git \
    gnupg \
    libreadline-dev \
    libssl-dev \
    libxml2-dev \
    libxml2-utils \
    libxslt-dev \
    lsb-release \
    pkg-config \
    tzdata \
    xsltproc \
    zlib1g-dev
```

2. 安装 `clang-16`（不支持其他版本的 `clang`）：

```sh
sudo sh -c 'echo "deb http://apt.llvm.org/$(lsb_release -cs)/ llvm-toolchain-$(lsb_release -cs)-16 main" >> /etc/apt/sources.list'
wget --quiet -O - https://apt.llvm.org/llvm-snapshot.gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install -y --no-install-recommends clang-16
```

3. 安装 Rust（请勿使用系统包管理器安装 `rustc`）：

```sh
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

4. 克隆代码仓库：

```sh
git clone https://github.com/tensorchord/pgvecto.rs.git
cd pgvecto.rs
```

5. 安装 `cargo-pgrx`：

```sh
cargo install cargo-pgrx --version $(grep -o 'pgrx = { version = "=[^"]*' Cargo.toml | cut -d = -f 4)
cargo pgrx init
```

`cargo-pgrx` 是开发 PostgreSQL 扩展的得力工具，你可以通过 https://docs.rs/crate/cargo-pgrx/latest 阅读其文档。

### 交叉编译 {#cross-compilation}

假设你需要在 `x86_64` 宿主机环境下为 `aarch64` 目标架构编译二进制文件和 Schema，可以按照以下步骤操作：

1. 安装交叉编译工具链：

```sh
sudo apt install crossbuild-essential-arm64
sudo apt install qemu-user-static
```

设置环境变量：

```sh
LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/aarch64-linux-gnu/lib:/usr/aarch64-linux-gnu/lib64"
```

在 `~/.cargo/config.toml` 文件末尾添加以下配置，为 Rust 配置模拟器、链接器和 sysroot：

```toml
[target.aarch64-unknown-linux-gnu]
runner = ["qemu-aarch64-static", "-L", "/usr/aarch64-linux-gnu"]
linker = "aarch64-linux-gnu-gcc"

[env]
BINDGEN_EXTRA_CLANG_ARGS_aarch64_unknown_linux_gnu = "-isystem /usr/aarch64-linux-gnu/include/ -ccc-gcc-name aarch64-linux-gnu-gcc"
```

2. 生成目标架构上的 PostgreSQL 头文件。该步骤可通过 `cargo-pgrx` 完成，同时你也可以直接利用仓库中 `vendor/pgrx_config` 和 `vendor/pgrx_binding` 目录下的文件。详情请参阅 `pgrx` 的官方文档。

<a id="Debug"></a>
## 调试 {#debug}

即使在 Release 模式下，编译生成的二进制文件中也包含了调试信息（Debug Info），因此你随时可以使用 `gdb` 进行调试。

对于 Debug 构建，当后台工作进程（Background Worker）中的线程发生 panic 时会打印调用栈（backtrace），但会话进程（Session Process）报错时默认不打印。对于 Release 构建，默认不打印任何 backtrace。但如果你将环境变量 `RUST_BACKTRACE` 设置为 `1`，则会打印所有 backtrace。建议在调试 Release 构建时使用命令 `RUST_BACKTRACE=1 cargo pgrx run --release`。
