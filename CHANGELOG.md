# Changelog

This file records user-visible changes in Tamagometer Enhanced. Release notes
for a `vX.Y.Z` tag are taken from the matching `## [X.Y.Z]` section, so every
release must have a completed entry here before the tag is pushed.

## [3.0.0-rc.1] - 2026-08-30

### Changed

- Began the staged Desktop presentation migration from Tkinter/ttk to PySide6
  and Qt Quick/QML while retaining the working protocol and transfer layers.
- Added a responsive Qt shell and catalog model as an architectural preview;
  the Tk interface remains available as a development fallback during parity
  work.
- Connected the Qt interface to the existing asynchronous Companion handshake
  and transfer controller for Connection 2024, Friends, and original V2/V3,
  including progress, cancellation, repeat-last transfer, and friendly errors.
- Rebuilt first-run setup with explicit close, skip, retry, and successful
  completion states plus a permanent Run setup again action.
- Added Qt settings, safe auto-connect controls, About information, and a
  privacy-conscious diagnostics drawer with Copy and Export.
- Added compact, medium, and wide responsive layouts, keyboard navigation,
  global shortcuts, accessible control metadata, visible focus, and a persisted
  reduced-motion preference.
- Added a Qt-only release entry point and reproducible one-file packaging that
  omits the retained Tk UI and uses the smaller PySide6 Essentials runtime.
- Added packaged-application startup and size checks to GitHub Actions, QML
  linting, third-party notices, and a physical-device release checklist.

### Fixed

- Unknown standalone COM ports are no longer silently selected as a Flipper;
  automatic selection now requires Flipper identity or a remembered port.
- Normalized mislabeled catalog images to real PNG files and added signature
  and decodeability regression tests.
- Made Qt controls follow the in-app palette instead of inheriting a conflicting
  Windows light/dark style, including readable button labels, dropdowns,
  progress bars, and scrollbars in both themes.
- Increased the default window to the wide layout and reduced unnecessary
  catalog height so the main workflow no longer starts vertically scrolled.
- Replaced font glyphs used as controls with consistently drawn UI icons and
  reserved a dedicated catalog gutter so its scrollbar cannot cover favorite
  actions.
- Removed scrolling from Settings, corrected switch state styling, restored a
  recognizable gear icon, and added visible dropdown borders in both themes.
- Made the catalog and transfer cards fill the available row at equal heights
  while keeping the final visible catalog row entirely inside its container.
- Standardized buttons, text inputs, and dropdowns on the same 40-pixel control
  height, including all three header actions.
- Rebuilt Transfer as one mode-independent slot layout so preview, title,
  metadata, instructions, progress, status, and action controls keep identical
  geometry for Connection, Friends, and original V2/V3.
- Made diagnostic export resolve local file URLs correctly on both Windows and
  Linux build agents.
- Split the main QML screen and transfer card into focused reusable components,
  and separated serial polling, connection results, and transfer events in the
  Qt view model without changing the protocol layer.
- Removed brittle tests that asserted source-code structure or duplicated the
  executable build checks already performed by the release workflow.

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
