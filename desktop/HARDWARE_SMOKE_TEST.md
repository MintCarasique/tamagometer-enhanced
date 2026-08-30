# Desktop 3.0 hardware smoke test

Complete this checklist on the exact Windows `.exe` and Flipper `.fap` intended
for release. Record the release tag or commit, SHA-256 checksums, Windows
version, Flipper firmware version, Companion version, and physical Tamagotchi
models used.

## Clean-machine startup

- Start `TamagometerDesktop.exe` on a supported Windows machine without Python,
  PySide6, or Qt installed.
- Confirm the main window, catalog sprites, Settings, About, onboarding, and
  diagnostics drawer load without warnings or missing controls.
- Check light and dark themes at 100%, 150%, and 200% display scaling.
- Resize down to the documented 720×620 minimum and verify that every action is
  reachable using scrolling and the keyboard.

## Companion and connection

- Install the matching `tamagometer_enhanced.fap`, open it on the Flipper, and
  confirm the Desktop capability/version handshake.
- Verify automatic discovery, manual connection, disconnect, USB unplug/replug,
  automatic reconnection, and cancellation during an active operation.
- Export a diagnostics report and confirm it contains useful versions and
  events but no unintended personal data.

## Physical transfers

- Connection 2024: send at least one gift, then use **Repeat last transfer**.
- Tamagotchi Friends: send one jewelry outcome and one Gotchi Points outcome;
  confirm progress reaches all 10 repetitions.
- Original Connection V2: complete one `Version 1` fallback session.
- Original Connection V3: complete one `Others` fallback session.
- For each mode, deliberately cause one timeout/misalignment and confirm the
  inline recovery message, cancellation, and subsequent retry work.

Do not remove the `python app.py --tk` development fallback or call Desktop
3.0 hardware-verified until all applicable checks above pass on the packaged
build.

## 3.0.0 release validation

- Release candidate tested: `v3.0.0-rc.1`.
- Result reported on 2026-08-30: packaged Desktop and matching Flipper
  Companion operate successfully with physical Tamagotchi hardware.
- Automated release checks cover Linux tests/QML lint, Windows packaging and
  startup, executable size, FAP compilation, release notes, and checksums.
