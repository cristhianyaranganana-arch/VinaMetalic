# Installation

VinaMetalic is a C++11 project. The only external dependency is Boost (≥ 1.65)
with the `system`, `thread`, `serialization`, `filesystem` and
`program_options` libraries.

## Linux

Tested on Ubuntu 22.04 with GCC 11.4 and Boost 1.74.

    sudo apt-get install build-essential cmake libboost-all-dev
    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
    cmake --build build -j
    ctest --test-dir build --output-on-failure

The executables are `build/vina` and `build/vina_split`. The binary reports its
version as `VinaMetalic v1.0.0 (fork of AutoDock Vina 1.2.7)`.

If Boost is installed in a non-standard location, pass
`-DBOOST_ROOT=/path/to/boost` to CMake.

By default the build links Boost **statically** so the resulting binaries are
portable between machines (audit finding #12). On platforms that only provide
shared Boost libraries, disable it:

    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DUSE_STATIC_BOOST=OFF

## macOS

Tested in CI on macOS 14 (Apple Silicon) with the Homebrew Boost:

    brew install boost cmake
    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DUSE_STATIC_BOOST=OFF
    cmake --build build --parallel
    ctest --test-dir build --output-on-failure

## Windows

A local build on Windows is possible with Visual Studio, CMake and a full Boost
installation, but it is **not officially supported in this release** and no
prebuilt Windows binary is provided. The CI workflow builds and tests
**Linux x86-64 and macOS ARM64** and releases **Linux x86-64 assets**; a
macOS release asset and a prebuilt Windows binary are planned.

If you want to experiment on Windows, install the Boost libraries your compiler
can find and run:

    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
    cmake --build build --config Release -j
    ctest --test-dir build -C Release --output-on-failure

## Tests

    ctest --test-dir build --output-on-failure

- `metal_gradient`: finite-difference check of the analytic metal gradients.
- `cn_detection`: runs `--score_only` on the two bundled examples and checks
  the automatically adjusted CN target.

The byte-identical regression suite (no-metal receptor and receptor with an
unparametrized Na⁺) needs an unmodified AutoDock Vina 1.2.7 binary. Either
run the scripts directly:

    tests/test_regression_no_metal.sh    build/vina /path/to/vina_original_1.2.7
    tests/test_regression_na_receptor.sh build/vina /path/to/vina_original_1.2.7

or register them in CTest:

    cmake -S . -B build -DVINA_REGRESSION_TEST=ON -DVINA_127_BIN=/path/to/vina_original_1.2.7
    cmake --build build && ctest --test-dir build --output-on-failure

## Runtime data

All metal parameters are compiled into the binary. The files under
`data/ad4_reference/` are shipped for traceability and manual inspection; they
are not read at runtime. Overrides can be supplied with `--metal_params`; see
`docs/USAGE.md`.

## Building release assets

`scripts/package_release.py` assembles the Linux platform archive and the
examples archive from a build directory:

    python3 scripts/package_release.py \
        --build-dir build --platform Linux-x64 --version 1.0

It writes `dist/VinaMetalic-v1.0-Linux-x64.tar.gz`,
`dist/VinaMetalic-v1.0-Linux-x64.zip` and `dist/VinaMetalic-v1.0-Examples.zip`, and
prints their SHA-256 hashes. The archives contain the executables, examples,
documentation, parameter data and license files; source code is distributed
through the repository.
