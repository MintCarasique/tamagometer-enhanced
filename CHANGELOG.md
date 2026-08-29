# Changelog

This file records user-visible changes in Tamagometer Enhanced. Release notes
for a `vX.Y.Z` tag are taken from the matching `## [X.Y.Z]` section, so every
release must have a completed entry here before the tag is pushed.

## [2.0.0] - 2026-08-29

### Added

- A hybrid Flipper Zero application that can send Connection 2024 gifts and
  Tamagotchi Friends rewards without a computer while retaining the Desktop
  Companion CLI.
- Categorized on-device catalogs, favorites, recently sent items, repeat-last
  transfer, item artwork, placement guidance, progress, cancellation,
  vibration feedback, and diagnostic export.
- A passive legacy Connection IR sniffer that saves decoded packets, checksum
  results, and raw timings for protocol research.
- An original Connection V2 `Version 1` / V3 `Others` compatibility fallback,
  available both on Flipper and in the Desktop application.
- First-run Desktop setup, automatic Flipper discovery and reconnection,
  light/dark themes, inline notifications, animated placement guidance,
  categories, favorites, recent history, repeat-last transfer, and one-file
  diagnostic export.

### Fixed

- Corrected the standalone transfer screen layout for the Flipper Zero's
  128×64 display.
- Replaced the legacy response path with a timing-safe low-level IR transmitter
  so original V2 and V3 devices receive replies inside their response window.

### Compatibility

- Verified Connection 2024 gift sending and Friends BFF rewards on hardware.
- Verified the compatibility fallback with an original Connection V2 and V3.
- Desktop 2.0 requires Tamagometer Enhanced Companion 2.0.0 or newer; install
  the `.exe` and `.fap` from the same release.

## [1.2.0] - 2026-08-22

### Added

- Guided first-run setup and automatic Flipper connection.
- Animated IR/LF placement instructions, real transfer progress, categories,
  favorites, recent history, item sprites, light/dark themes, inline
  notifications, repeat-last transfer, and diagnostic export.

### Changed

- Adopted the conventional `tamagometer_enhanced.fap` release filename while
  retaining the readable application name in Flipper metadata.

## [1.1.0] - 2026-08-22

### Added

- A versioned Desktop/Companion capability handshake.
- Automatic serial-port selection and reconnection.
- Structured transfer stages and Friends broadcast progress.

### Changed

- Successful transfers now use non-blocking in-window notifications.
- Project documentation now clearly distinguishes this enhanced fork from the
  original Tamagometer project.

## [1.0.0] - 2026-08-22

### Added

- Tamagotchi Friends BFF BUMP reward support over LF RFID.
- A modern Windows Desktop utility for Connection 2024 gifts and Friends
  rewards.
- Automated Desktop tests and `.exe`/`.fap` builds with binaries published in
  GitHub Releases rather than committed to Git history.
