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
6. Add user-visible changes to the next version section in `CHANGELOG.md`.

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

## Releases

Release tags use the form `vX.Y.Z`. Before pushing a tag:

1. Set the Desktop and Companion versions to the stable `X.Y.Z` value.
2. Add a `## [X.Y.Z] - YYYY-MM-DD` section to `CHANGELOG.md` with concise,
   user-facing `Added`, `Changed`, `Fixed`, and `Compatibility` entries as
   applicable.
3. Update the Flipper submodule's `CHANGELOG.md` when the Companion changed.
4. Run the Desktop tests and build the FAP.

The release workflow extracts the matching root changelog section verbatim.
It intentionally does not publish an automatically generated list of commits.

The repository includes compact PowerShell helpers for the routine workflow:

```powershell
# Run tests, QML lint, and compileall with output shown only on failure.
.\tools\check.ps1

# Squash a completed feature branch into main, verify it, push it, and remove
# the local and remote feature branch.
.\tools\squash-feature.ps1 -Branch feature/example -Message "Add example feature"

# Validate metadata, create the tag, wait for Actions, and verify all assets.
.\tools\release.ps1 -Version 3.1.0
```

Use `tools/commit.ps1` when a checked commit is useful without a merge. It
requires either explicit `-Paths` or `-All`, so unrelated files are never staged
implicitly. Feature branches are squash-merged to keep `main` concise.

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
