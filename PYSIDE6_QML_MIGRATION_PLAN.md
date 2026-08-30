# PySide6 + QML Migration Plan

## Purpose

This document is a handoff for the agent implementing the Tamagometer Enhanced
Desktop UI migration from Tkinter/ttk to PySide6 with Qt Quick/QML.

The migration should modernize the presentation layer without rewriting the
working Tamagotchi protocols, serial transport, transfer state machine, catalogs,
or persistence model. The existing Tkinter application must remain usable until
the new UI reaches feature parity.

No protocol behavior should change as part of this migration unless a separate,
explicitly scoped defect requires it.

## Current state

The desktop application is located in `desktop/` and starts from
`desktop/app.py`. The released presentation layer consists mainly of:

- `desktop/tamagometer_desktop/qt/application.py` — Qt application startup;
- `desktop/tamagometer_desktop/qt/app_view_model.py` — GUI-thread state and
  service adapter;
- `desktop/tamagometer_desktop/qt/catalog_model.py` — filterable QML catalog;
- `desktop/tamagometer_desktop/qt/qml/` — responsive screens, dialogs, themes,
  and reusable controls.

The previous Tk presentation remains in `window.py`, `onboarding.py`,
`alignment.py`, and `theme.py`, and is available explicitly through
`python app.py --tk` for development comparison.

The reusable application and protocol layer consists mainly of:

- `desktop/tamagometer_desktop/transfer.py` — background transfer controller;
- `desktop/tamagometer_desktop/modes.py` — supported modes and catalogs;
- `desktop/tamagometer_desktop/catalog.py` — categories, favorites, recent keys,
  and sprite mapping;
- `desktop/tamagometer_desktop/settings.py` — persistent settings;
- `desktop/tamagometer_desktop/diagnostics.py` — diagnostic report generation;
- `desktop/flipper_serial.py` — serial discovery, handshake, and Flipper commands;
- `desktop/transfer_status.py` — structured transfer states;
- `desktop/tamagometer_core.py` and `desktop/friends_core.py` — protocol data and
  encoding.

The protocol, serial, catalog, settings, and Qt workflows have automated tests
under `desktop/tests/`. Preserve behavior-focused coverage and avoid tests that
only pin implementation details already exercised by the release build.

## Implementation status — 3.0.0 released

The migration was completed on `feature/pyside6-qml` and released as 3.0.0.
The delivered implementation includes:

- the 38-test baseline is preserved and Qt-facing tests are additive;
- inherited WebP-content files are normalized to real PNG and validated for
  signatures and decodeability;
- unknown standalone COM ports are no longer silently auto-selected;
- `app.py` starts the responsive PySide6/QML application by default;
- `app.py --tk` retains the complete Tkinter hardware workflow;
- the QML catalog supports categories, favorites, recent ordering, explicit
  favorite controls, and name/category/decimal/hex search;
- Original V2/V3 renders a purpose-built single-action explanation instead of
  a fake catalog.

Phase 2 is now implemented in the Qt UI: Companion connection runs outside the
GUI thread, `QTimer` drains connection and transfer queues on the GUI thread,
and Connection 2024, Friends, and original V2/V3 expose start, progress,
cancellation, completion, repeat, and disconnect/error states. These paths have
automated simulated coverage. The UI and packaging phases are complete, and
the packaged release candidate passed physical-hardware validation before the
final `3.0.0` release.

Phase 3 is implemented: onboarding persists distinct skipped and completed
states, closing it does not record either outcome, setup can be reopened from
Settings, and successful completion requires a verified Companion connection.
Settings exposes the documented auto-connect policy and About information.
Diagnostics is a separate privacy-conscious drawer with Copy and Export;
friendly notices keep raw technical exceptions behind its details action.

Phase 4 is implemented with width-based compact, medium, and wide breakpoints.
The header reflows at compact widths, the main workflow stacks while remaining
scrollable, and automated QML tests exercise 720, 900, and 1280 pixel widths
without losing selection or theme state. Catalog cards support keyboard
selection and an explicit `F` favorite shortcut; primary controls expose
accessible names and focus. Global shortcuts cover Settings, Diagnostics,
Repeat, and cancellation, and a persisted reduced-motion preference is exposed
for nonessential animation.

Phase 5 packaging is implemented for CI and local release builds. A Qt-only
entry point prevents Tcl/Tk from entering the release executable, dependencies
use the pinned PySide6 Essentials wheel instead of the full Addons bundle, and
one-file PyInstaller packaging is the selected release format. One-folder and
Nuitka/pyside6-deploy expectations were evaluated; the former is useful for
library replacement and troubleshooting, while the latter remains an optional
future optimization rather than a release-toolchain change during migration.
CI lints QML, launches the packaged executable offscreen, enforces a size
guardrail, and attaches third-party notices. Clean-machine and physical-device
validation is tracked in `desktop/HARDWARE_SMOKE_TEST.md`. The Tk fallback is
retained as a source-only development and comparison path.

Before the RC, the QML shell was decomposed into header, connection, catalog,
legacy, transfer-summary, and transfer-action components. The Qt view model now
keeps periodic port polling and queue-specific event handling separate from the
timer slot. Redundant source-structure tests were removed; protocol and visible
UI behavior coverage remains in place.

## UX defects the migration must address

The new UI must not reproduce these verified issues from the Tkinter version:

1. At the declared minimum size of 900x760, the connection help is clipped and
   the diagnostics content disappears. The new layout must be responsive and
   scroll when necessary.
2. A disabled primary transfer button currently looks actionable. Disabled,
   busy, disconnected, and ready states must be visually distinct and include a
   textual explanation.
3. Diagnostics permanently consumes main-window space but is often collapsed by
   the layout. Move it into a drawer, expandable section, or separate page/dialog.
4. Closing or skipping first-run setup currently marks onboarding complete, and
   reopening it requires deleting the settings file. Add a permanent "Run setup
   again" action and distinguish close, skip, and successful completion.
5. Raw serial exceptions can appear in user-facing notices. Present a friendly
   error summary and keep technical details in diagnostics.
6. The current auto-detection may attempt to connect to an unrelated sole COM
   port. Do not silently auto-connect unless Flipper identity or a remembered
   verified port provides sufficient confidence.
7. Search only matches item name and category. The new catalog must also support
   visible decimal/hexadecimal IDs.
8. Double-clicking a row toggles favorite status, which is unexpected. Use an
   explicit favorite control.
9. Empty Favorites, Recently sent, and search results need useful empty states.
10. The single-action Original V2/V3 mode should not render a fake catalog table.
11. A large part of the current sprite set is WebP content stored with a `.png`
    extension. Fix or normalize the assets before relying on them in QML. Add an
    asset validation test that checks file signatures and decodeability.

## Recommended technology

- Python and PySide6 for the application runtime;
- Qt Quick and Qt Quick Controls for the interface;
- QML modules and reusable QML components rather than dynamically constructed
  view trees in Python;
- a Python ViewModel layer based on `QObject`, `Property`, `Signal`, and `Slot`;
- `QAbstractListModel` for the gift/reward catalog;
- `QSettings` is optional. Prefer retaining the existing JSON `SettingsStore`
  initially to avoid an unnecessary settings migration;
- `pyside6-deploy`/Nuitka for the release build, evaluated against the existing
  PyInstaller release workflow before removing PyInstaller.

Do not introduce React, an embedded HTTP server, a browser frontend, or a Rust
sidecar as part of this migration.

## Target architecture

```text
desktop/
  app.py                         # application entry point; selects the Qt UI
  tamagometer_core.py            # retained
  friends_core.py                # retained
  flipper_serial.py              # retained, with scoped discovery fixes
  transfer_status.py             # retained
  tamagometer_desktop/
    transfer.py                  # retained; remove Tk assumptions if found
    modes.py                     # retained
    catalog.py                   # retained
    settings.py                  # retained initially
    diagnostics.py               # retained
    qt/
      __init__.py
      application.py             # QGuiApplication/QQmlApplicationEngine startup
      app_view_model.py          # global mode, connection, notices, theme
      catalog_model.py           # QAbstractListModel catalog adapter
      transfer_view_model.py     # transfer progress and actions
      onboarding_view_model.py   # setup workflow
      image_provider.py          # optional normalized sprite provider
      qml/
        Main.qml
        pages/
          ConnectionPage.qml
          FriendsPage.qml
          LegacyPage.qml
          SettingsPage.qml
        components/
          AppShell.qml
          ConnectionCard.qml
          DeviceModeTabs.qml
          CatalogGrid.qml
          CatalogList.qml
          CatalogItem.qml
          TransferPanel.qml
          AlignmentGuide.qml
          DiagnosticsDrawer.qml
          EmptyState.qml
          InlineNotice.qml
          StatusBadge.qml
        dialogs/
          OnboardingDialog.qml
          ErrorDetailsDialog.qml
        theme/
          Theme.qml
          qmldir
```

The exact split may change, but business logic must live in Python services and
view models, while layout, visuals, transitions, and responsive behavior live in
QML.

## State and threading rules

The current `TransferController` emits `AppEvent` objects into a `queue.Queue`.
Do not update QML-bound properties directly from a worker thread.

Choose one of these safe adapters:

1. Preferred initial approach: keep `TransferController` unchanged and use a
   short `QTimer` in the Qt ViewModel to drain its event queue on the GUI thread.
2. Later cleanup: replace queue polling with Qt signals emitted through a
   dedicated QObject bridge whose delivery is queued to the GUI thread.

All QML-visible state changes must occur on the Qt GUI thread. Serial work and
long-running transfers must remain off the GUI thread. Window close must cancel
an active transfer and close the serial connection cleanly.

Expose explicit, testable state instead of deriving presentation rules in QML:

- `connectionState`: disconnected, detecting, connecting, connected,
  reconnecting, incompatible, error;
- `transferState`: idle, preparing, waiting, sending, verifying, completed,
  cancelled, failed, disconnected;
- `canStartTransfer`, `canRepeatTransfer`, `canCancelTransfer`;
- `primaryActionLabel` and `primaryActionHint`;
- `notice` containing severity, friendly summary, and optional technical detail;
- selected device mode, selected catalog item, category, query, favorites, and
  recent items.

## Proposed information architecture

### App shell

- Compact title/header, connection status, theme control, and Help/Settings.
- Device-mode tabs immediately below the header.
- Main content changes by mode rather than forcing every mode into one table.
- Diagnostics opens from the status/error area or Settings and does not occupy
  permanent workspace.

### Connection 2024 and Friends

- Left/main area: searchable and filterable catalog, preferably a responsive
  card grid with a list-view fallback for narrow windows.
- Right/secondary area: selected item, physical alignment guide, ordered steps,
  transfer progress, and primary action.
- On narrow windows, stack the transfer panel below the catalog and preserve all
  content with scrolling.

### Original V2/V3

- No item table, category selector, favorite action, or fake item ID.
- Show protocol limitations, the physical placement guide, current stage, and a
  single `Start fallback` action.

### Errors and completion

- Recoverable errors remain visible until dismissed or resolved.
- Error messages state what happened, what the user should do, and where to find
  technical details.
- Successful transfers produce a persistent completion summary with item name,
  mode, timestamp, and `Repeat` action.

## Migration phases

### Phase 0 — Baseline and guardrails

1. Run and record the existing unit-test baseline.
2. Document current release packaging, command-line entry point, application
   version source, and asset inclusion rules.
3. Add tests for asset signatures/decodeability.
4. Normalize mislabeled WebP/PNG sprites or introduce a deterministic conversion
   step that produces real PNG assets for the packaged application.
5. Add a focused test for COM-port confidence so an unknown sole port is not
   silently treated as a Flipper.

Exit criteria:

- all existing tests pass;
- every catalog preview intended for use in the new UI decodes successfully;
- the expected Flipper detection policy is covered by tests.

### Phase 1 — Qt skeleton and ViewModels

1. Add PySide6 to development/runtime dependencies.
2. Create `QGuiApplication` and `QQmlApplicationEngine` startup.
3. Implement ViewModels around the existing SettingsStore, mode catalog,
   FlipperConnection, and TransferController.
4. Implement `QAbstractListModel` roles for at least:
   `itemId`, `displayId`, `name`, `category`, `favorite`, `recent`, and
   `spriteUrl`.
5. Add Qt tests for model filtering, selection retention, favorites, and state
   transitions. Prefer headless/offscreen execution in CI where possible.
6. Keep the Tk entry point available behind an explicit development switch until
   feature parity is reached.

Exit criteria:

- the QML shell starts without hardware;
- mode switching and catalog filtering work;
- no serial or protocol module imports Tkinter;
- the Qt event loop remains responsive while simulating transfer events.

### Phase 2 — Main workflows

Implement the three complete workflows in this order:

1. Connection 2024 gift transfer;
2. Friends BFF reward transfer, including 0/10 through 10/10 progress;
3. Original V2/V3 fallback.

For every workflow implement:

- disconnected, connecting, ready, busy, completed, cancelled, failed, and
  disconnected-mid-transfer states;
- physical placement guide;
- user-facing recovery instructions;
- cancel and repeat behavior where applicable;
- favorites and recent-history updates only after confirmed success.

Exit criteria:

- behavior matches current transfer tests;
- simulated success, cancellation, timeout, incompatible Companion, and USB
  disconnect are manually verified;
- the primary action never appears enabled when it cannot run.

### Phase 3 — Onboarding, diagnostics, and settings

1. Rebuild onboarding as a QML dialog/page with Back, Continue, retry, explicit
   Skip, and successful completion states.
2. Add `Run setup again` to Settings/Help.
3. Add an auto-connect preference and explain its behavior.
4. Move diagnostics into a drawer/page/dialog with Copy and Export actions.
5. Separate friendly error summaries from technical exception details.
6. Add About information, version, Companion requirement, and links/instructions
   already present in the README.

Exit criteria:

- closing onboarding does not falsely record success;
- setup can always be reopened through the UI;
- diagnostics remain reachable at every supported window size;
- exported reports retain the current privacy-conscious behavior.

### Phase 4 — Responsive design and accessibility

1. Define compact, medium, and wide layout breakpoints based on available width,
   not OS or display identity.
2. Verify 100%, 125%, 150%, and 200% Windows scaling.
3. Ensure every workflow is usable at the supported minimum window size without
   clipped or unreachable content.
4. Add keyboard navigation, logical tab order, visible focus, Enter/Space
   activation, Escape behavior, and accessible names/descriptions.
5. Avoid conveying state only through color. Include text and/or icons.
6. Respect reduced-motion expectations by making nonessential animations subtle
   and optional.
7. Verify light and dark themes, contrast, long error text, and translated or
   expanded strings.

Exit criteria:

- no horizontal clipping in supported layouts;
- all primary workflows can be completed without a mouse;
- screen-reader/UI Automation inspection exposes meaningful names and states;
- theme switching does not recreate the application or lose selection.

### Phase 5 — Packaging and cutover

1. Prototype both one-folder and single-executable deployment expectations with
   `pyside6-deploy`/Nuitka. Do not assume the current PyInstaller flags translate
   directly.
2. Verify inclusion of QML modules, Qt Quick Controls, platform plugins, image
   formats, fonts/icons, and catalog sprites.
3. Test on a clean supported Windows machine without a development Python or Qt
   installation.
4. Confirm startup time, binary size, antivirus false-positive risk, code-signing
   compatibility, and GitHub Actions support.
5. Update `desktop/README.md`, root `README.md`, development requirements, build
   commands, and release workflow.
6. Remove the Tkinter UI only after Qt feature parity, packaging verification,
   and hardware smoke testing.

Exit criteria:

- packaged build starts on a clean Windows system;
- QML and all assets load from the package;
- Connection, Friends, and Legacy modes receive hardware smoke tests;
- the release artifact and Companion version requirements remain clear.

## Testing strategy

Retain the existing protocol tests and add these layers:

1. Pure ViewModel tests without loading QML.
2. `QAbstractListModel` tests for roles, filtering, IDs, favorites, recent order,
   empty states, and selection.
3. Transfer adapter tests that feed `AppEvent` objects and assert Qt-visible
   properties and action availability.
4. QML component smoke tests for loading errors and required object contracts.
5. Screenshot or image-comparison tests for a small number of stable states:
   disconnected, ready, active transfer, error, completion, empty catalog, and
   onboarding.
6. Manual Windows checks at multiple DPI values and window sizes.
7. Packaged-build smoke tests on CI or a clean VM.

Do not make screenshot tests excessively sensitive to minor font rasterization.
Prefer geometry, visibility, state, and coarse image assertions.

## Definition of done

The migration is complete only when:

- all existing unit tests and new Qt tests pass;
- all three device modes reach functional parity;
- the interface remains usable at the documented minimum size and common Windows
  scaling values;
- no user-facing workflow depends on the diagnostics log being permanently
  visible;
- all intended catalog images render;
- connection and transfer failures provide actionable messages;
- onboarding can be reopened and does not record completion accidentally;
- keyboard navigation and visible focus cover every primary action;
- a packaged Windows build works without Python or Qt installed separately;
- the Qt build is verified with physical Flipper/Tamagotchi hardware before the
  Tkinter implementation is removed.

## Implementation cautions

- Do not call blocking serial methods from the Qt GUI thread.
- Do not allow QML to contain protocol constants or construct Flipper commands.
- Do not duplicate catalogs in QML; expose the existing Python data through a
  model.
- Do not migrate settings format and UI framework simultaneously unless a clear
  requirement demands it.
- Do not delete the Tkinter implementation early. Keep a temporary fallback for
  behavioral comparison and hardware verification.
- QML resource paths behave differently in source and packaged builds. Validate
  both early instead of postponing resource packaging until the end.
- Qt licensing and third-party notices must be reviewed before release.
- Avoid a visual redesign that obscures protocol timing and physical placement
  instructions. Reliability and state clarity take precedence over animation.

## Suggested first implementation slice

The safest first pull request should contain only:

1. dependency and Qt application bootstrap;
2. a read-only QML shell with header, theme, mode tabs, and responsive layout;
3. a Python catalog `QAbstractListModel` with search/category filtering;
4. decoded/validated catalog sprites;
5. tests for QML startup and catalog behavior;
6. no removal of Tkinter and no change to live transfer behavior.

This slice provides an architectural proof before serial connection and transfer
controls are moved into the new event loop.
