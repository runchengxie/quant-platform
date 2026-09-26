# Rust Build Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the optional `quant-platform` Rust microstructure wheel reproducibly build with a pinned compiler and locked Maturin command in local development and CI.

**Architecture:** Keep the root Python package independent of Rust. Pin the crate compiler in a repository-level rustup file, install the same toolchain in the Rust CI job, and run Maturin from the root project's locked development environment. Build and install the wheel only in the existing optional Rust CI job, then use the existing Python/Rust parity suite.

**Tech Stack:** Rust 1.98.1, Cargo lockfile, PyO3, Maturin, uv, GitHub Actions, pytest.

**Spec:** Approved design, phase two, as scoped by `docs/development/microstructure-rust.md` and the exact decisions restated here.

## Global Constraints

- Pin Rust to `1.98.1`, the version recorded for the current benchmark.
- Keep `packages/microstructure/rust/Cargo.lock` committed and use `cargo check --locked`.
- Add `maturin>=1,<2` to the root `dev` dependency group and resolve its exact version in `uv.lock`.
- Preserve Python as the default backend and behavior reference; Rust remains an optional wheel.
- Keep wheel files and benchmark outputs outside the repository.
- Use only synthetic data in CI and keep public platform code strategy independent.
- Do not change deployment installation or runtime selection behavior.

## Review Focus

- Rust formatting and clippy components must be available from the pinned toolchain used in CI.
- The Maturin executable must come from the locked `uv` environment instead of the floating `uvx` download.
- The optional Rust job must still install the built wheel before setting `TICKNET_REQUIRE_RUST=1`.
- A regular source install without the wheel must continue using the Python backend.
- The documented commands must leave build output under `/tmp` and must not introduce generated files into Git.

---

### Task 1: Pin the project Rust toolchain in local development and CI

**Files:**
- Create: `rust-toolchain.toml`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- rustup toolchain channel: `1.98.1`.
- Required components: `rustfmt`, `clippy`.
- CI Rust job uses `dtolnay/rust-toolchain@1.98.1` and prints the active compiler version.

- [ ] **Step 1: Record the current toolchain baseline**

Run `rustc --version` and `cargo --version` in the task worktree. Confirm the local toolchain is `1.98.1` and the crate's existing lockfile is present. Record the current CI action's floating `stable` selection before editing.

- [ ] **Step 2: Add the rustup project pin**

Create `rust-toolchain.toml` with `channel = "1.98.1"`, `profile = "minimal"`, and components `rustfmt` and `clippy`. Replace the Rust job's `dtolnay/rust-toolchain@stable` step with `dtolnay/rust-toolchain@1.98.1` and the same two components. Add a `rustc --version` log step before Cargo checks.

- [ ] **Step 3: Verify local tool selection and Rust checks**

Run:

```bash
rustup show active-toolchain
rustc --version
cargo fmt --check --manifest-path packages/microstructure/rust/Cargo.toml
cargo check --locked --manifest-path packages/microstructure/rust/Cargo.toml
git diff --check
```

Expected: active toolchain and `rustc` show `1.98.1`; formatting and locked check exit 0.

- [ ] **Step 4: Commit the toolchain pin**

```bash
git add rust-toolchain.toml .github/workflows/ci.yml
git commit -m "build: pin microstructure Rust toolchain"
```

### Task 2: Lock Maturin and use it for the optional wheel build

**Files:**
- Modify: `pyproject.toml` (`[dependency-groups].dev`)
- Modify: `uv.lock`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Root development dependency: `maturin>=1,<2` resolved in `uv.lock`.
- CI build command: `uv run --locked maturin build --release -m packages/microstructure/rust/Cargo.toml --out /tmp/microstructure-wheels`.
- Existing install target and parity command remain `.venv` and `TICKNET_REQUIRE_RUST=1 .venv/bin/pytest tests/microstructure -q`.

- [ ] **Step 1: Add Maturin to the dev dependency group and refresh the lock**

Add `maturin>=1,<2` to `[dependency-groups].dev`, then run `uv lock`. Confirm `uv.lock` records the exact resolved Maturin version and `uv lock --check` succeeds.

- [ ] **Step 2: Replace the floating CI tool invocation**

In `.github/workflows/ci.yml`, replace `uvx --from maturin maturin build ...` with the command defined above. Keep the wheel output under `/tmp/microstructure-wheels`, install the generated wheel into `.venv`, and preserve the required Rust parity test command.

- [ ] **Step 3: Verify locked build and parity locally**

Run:

```bash
uv sync --locked --all-groups --extra dev --extra microstructure
uv run --locked maturin --version
uv run --locked maturin build --release -m packages/microstructure/rust/Cargo.toml --out /tmp/microstructure-wheels
uv pip install --python .venv/bin/python /tmp/microstructure-wheels/*.whl
TICKNET_REQUIRE_RUST=1 .venv/bin/pytest tests/microstructure -q
```

Expected: locked sync and build exit 0; the installed wheel passes the full microstructure suite with Rust required.

- [ ] **Step 4: Commit the locked wheel build**

```bash
git add pyproject.toml uv.lock .github/workflows/ci.yml
git commit -m "build: lock maturin for rust wheel builds"
```

### Task 3: Update the Rust development guide

**Files:**
- Modify: `docs/development/microstructure-rust.md`

**Interfaces:**
- Documented setup uses `uv sync --locked --all-groups --extra microstructure`.
- Documented build uses `uv run --locked maturin build` and outputs to `/tmp/microstructure-wheels`.
- Existing Python default, optional wheel install, `abi3`, boundary types, parity suite, and benchmark interpretation remain documented.

- [ ] **Step 1: Update local build and verification commands**

Replace the `uvx --from maturin` invocation with the locked command. Explain that `rust-toolchain.toml` selects Rust 1.98.1 and the dev dependency group supplies the locked Maturin executable. Preserve the requirement to install the separate wheel explicitly when selecting `backend="rust"`.

- [ ] **Step 2: Run documentation and build checks**

Run:

```bash
git diff --check
python scripts/check_minimal_install.py
cargo fmt --check --manifest-path packages/microstructure/rust/Cargo.toml
cargo check --locked --manifest-path packages/microstructure/rust/Cargo.toml
uv run --locked maturin build --release -m packages/microstructure/rust/Cargo.toml --out /tmp/microstructure-wheels
uv pip install --python .venv/bin/python /tmp/microstructure-wheels/*.whl
TICKNET_REQUIRE_RUST=1 .venv/bin/pytest tests/microstructure -q
```

Expected: all commands exit 0; `git status --short` contains only intended source changes and no wheel artifacts.

- [ ] **Step 3: Commit the development guide update**

```bash
git add docs/development/microstructure-rust.md
git commit -m "docs: document locked Rust wheel build"
```

## Plan Self-Review

- **Spec coverage:** Covers the Rust toolchain pin, Maturin lock, identical local/CI wheel build, optional installation, parity verification, development docs, and repository artifact boundary. Rust kernel migration criteria remain guidance for future work, not part of this build-contract PR.
- **Step scan:** Each task has a concrete file list, command, expected result, and commit boundary.
- **Type consistency:** All build commands use the same manifest path, output path, and environment installation target.
- **Review focus:** Rust component availability, locked Maturin invocation, wheel-before-parity order, Python-only fallback, and out-of-repository outputs are checked by the listed commands and CI job.
- **Proportion:** The plan changes only toolchain configuration, one development dependency, the existing Rust CI job, and its guide.
