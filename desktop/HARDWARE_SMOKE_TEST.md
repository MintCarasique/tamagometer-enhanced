# Desktop hardware smoke test

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
- Original Connection V4 (Initial Support): complete one `Others` fallback
  session using Companion 3.2.0 or newer; record the activity and visible gift.
- For each mode, deliberately cause one timeout/misalignment and confirm the
  inline recovery message, cancellation, and subsequent retry work.

Do not remove the `python app.py --tk` development fallback or call Desktop
hardware-verified until all applicable checks above pass on the packaged
build.

## 3.0.0 release validation

- Release candidate tested: `v3.0.0-rc.1`.
- Result reported on 2026-08-30: packaged Desktop and matching Flipper
  Companion operate successfully with physical Tamagotchi hardware.
- Automated release checks cover Linux tests/QML lint, Windows packaging and
  startup, executable size, FAP compilation, release notes, and checksums.

## 3.2.0 release validation

- On 2026-09-30, the user confirmed V4 gift receipt and tested the refactored
  Companion on physical V4 and V3 devices before approving the release.
- V4 is Initial Support in `Others` fallback only. Game winner semantics and
  desktop-driven V4 exchanges have not been independently validated.
- This does not claim a new full packaged-Desktop hardware smoke test.
