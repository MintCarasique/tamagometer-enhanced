# Changelog

This file records user-visible changes in Tamagometer Enhanced. Release notes
for a `vX.Y.Z` tag are taken from the matching `## [X.Y.Z]` section, so every
release must have a completed entry here before the tag is pushed.

## [3.2.1] - 2026-09-30

### Changed

- Redesigned Tamagotchi and Flipper placement illustrations with matching
  vector artwork in Desktop and compact monochrome silhouettes on Flipper.
- Desktop previews retain gift sprites and include IR/LF device placement;
  device artwork follows the app theme and respects reduced-motion settings.

### Fixed

- Flipper result screens separate readable outcomes from diagnostic counters
  and keep long text in a scrollable area above Menu/Repeat, preventing overlap.

## [3.2.0] - 2026-09-30

### Added

- **Initial Support for original Connection V4 / JinSei** in `Others` fallback, responding as
  V3 using a captured identity and the current session byte.
- V4 identification in standalone status, diagnostic reports, and Desktop
  transfer results. Desktop's original Connection selector now includes V4.
- Capture replay tests exercising the production C decoder and V4 reply bytes.

### Fixed

- Decode complete 24-byte V4 identities instead of truncating them to 20 bytes
  and incorrectly rejecting their checksum.
- Share frame decoding between the Connection Sniffer and fallback; malformed
  or unsupported frame lengths are rejected instead of decoded as shorter frames.

### Changed

- Separate original Connection exchange orchestration from the Connection 2024
  and Friends protocol code. Reuse one IR worker per exchange and share initial
  and retry acknowledgement handling without changing reply bytes or delays.
- Cache Qt catalog search metadata and sprite paths per mode, avoiding repeated
  file checks while searching or updating favorites and recently sent items.
- Share Companion runtime version and capabilities between CLI, About, and
  diagnostics. Add a verified local FAP build helper to avoid stale artifacts.

### Compatibility

- V4 requires the 3.2 Companion. V2/V3 identity profiles and replies are preserved.
- V4 gift receipt and the refactored V4/V3 build were tested on physical
  hardware. V4 remains Initial Support: game outcome semantics and exhaustive
  compatibility are not established. Native V4 mode and selectable V4 gifts
  are not implemented.

## [3.1.0] - 2026-09-05

### Changed

- Simplified Qt connection-state transitions and catalog role mapping, and
  expanded dense view-model methods for easier maintenance.
- Removed duplicate Qt catalog properties while preserving the existing QML
  interface and saved user data.
- Simplified Flipper transfer and sniffer worker shutdown through one shared
  lifecycle path.
- Split Flipper transfer-result rendering into focused helpers and made scene
  callback mappings explicit.
- Simplified standalone item-detail formatting without changing Connection
  2024, Friends, or original V2/V3 protocol behavior.

### Verified

- Passed all 53 Desktop tests, QML linting, and Python bytecode compilation.
- Built the Companion FAP successfully for Flipper target 7 and application
  API 87.1.

## [3.0.0] - 2026-08-30

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

### Verified

- Promoted the release candidate after successful testing with the packaged
  Desktop application, Flipper Companion, and physical Tamagotchi hardware.

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
