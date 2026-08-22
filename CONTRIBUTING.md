# Contributing to Tamagometer Enhanced

Thank you for helping improve Tamagometer Enhanced. This repository is an
independent fork of the MIT-licensed upstream Tamagometer project. Contributions
should preserve upstream copyright notices and clearly document the source of
protocol data, captures, or third-party code.

## Before submitting a change

1. Create a branch from the current `main` branch.
2. Keep unrelated changes in separate commits.
3. Do not commit generated `.exe` or `.fap` files; GitHub Actions builds them.
4. Never include private device identifiers, serial logs containing personal
   data, or copyrighted ROM contents.
5. Describe any hardware used for validation, including the Tamagotchi model
   and Flipper firmware version.

## Desktop application

The supported user interface is in `desktop/`. Install its development
dependencies and run the test suite with:

```powershell
cd desktop
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

Changes to the serial protocol should include tests for fragmented input, CLI
noise, timeouts, cancellation, and disconnection where applicable. Changes to
Friends packet constants must remain consistent with the Companion C source.

## Flipper Companion

The enhanced Companion is maintained in the `flipper/` submodule. Build it with
[uFBT](https://github.com/flipperdevices/flipperzero-ufbt):

```powershell
cd flipper
ufbt
```

Desktop and Companion CLI changes must remain versioned through `tamagometer
info`. Update both sides together when adding a capability.

## Legacy web and Pico code

`web_interface_vue/` and `pico/` are inherited research tools from upstream and
are retained for protocol study. The Windows desktop and enhanced Flipper
Companion are the actively supported path in this fork. If a contribution
changes legacy behavior, explain whether it remains compatible with upstream
hardware and message formats.

## Protocol research

Document reproducible observations in `Protocol.md` or tests. Clearly separate
captured facts from hypotheses, and include enough context for another person
to repeat the experiment without distributing proprietary firmware or ROMs.

## Upstream attribution

This fork is based on Zach Resmer's MIT-licensed
[Tamagometer](https://github.com/zacharesmer/tamagometer) and
[Flipper Companion](https://github.com/zacharesmer/tamagometer-companion-flipper).
Those links are provided as source attribution, not as support channels for this
fork. Please use this repository's GitHub issues and pull requests for enhanced
project contributions.
