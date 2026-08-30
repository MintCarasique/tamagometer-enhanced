# Tamagometer Enhanced

Tamagometer Enhanced is an unofficial Windows utility for interacting with
Tamagotchi devices through a Flipper Zero. It combines the original
Tamagometer Connection 2024 infrared protocol with a simpler desktop interface
and Tamagotchi Friends BFF reward support over low-frequency RFID.

This project is maintained as an independent enhanced fork of Zach Resmer's
MIT-licensed Tamagometer research project. Upstream links are retained in the
Credits section for attribution; downloads, support, and current development
for this fork are hosted in this repository.

Current stable release: **2.0.0** (2026-08-29). See the complete
[`CHANGELOG.md`](CHANGELOG.md) for release history.

Desktop **3.0.0** is currently under development on the
`feature/pyside6-qml` branch. It introduces the new PySide6/Qt Quick interface
in staged slices while retaining the Tkinter UI as a hardware-tested fallback.

## Supported devices

| Device | Transport | Available operation | Status |
| --- | --- | --- | --- |
| Tamagotchi Connection v3 2024 re-release | Infrared | Send any of 181 gifts | Verified on hardware |
| Tamagotchi Friends | LF RFID | BFF BUMP: 60 jewelry outcomes and 200–1,000 Gotchi Points | Verified on hardware |
| Original Tamagotchi Connection V2 | Infrared | V1-compatible random game/gift fallback | Verified on hardware; experimental protocol |
| Original Tamagotchi Connection V3 | Infrared | `Others` random game/gift fallback | Verified on hardware; experimental protocol |

Tamagotchi Friends support currently covers the receiver side of **BFF BUMP**.
Exchange, Visit Bump, Mail, and Special modes are not implemented.

## Version 2.0

Version 2.0 makes the Flipper application fully hybrid: Connection 2024 gifts,
Friends rewards, and the original V2/V3 fallback can be started directly on the
Flipper, while the versioned Desktop CLI remains available. The standalone UI
includes categorized catalogs, favorites, recent items, repeat-last transfer,
item artwork, placement guidance, progress, cancellation, vibration feedback,
and diagnostic export.

The Desktop application provides guided first-run setup, automatic Flipper
discovery and reconnection, animated IR/LF placement instructions, real
progress, categories, favorites, recent history, Connection item sprites,
light/dark themes, inline notifications, repeat-last transfer, and one-file
diagnostic export.

The Flipper application also includes a passive Connection Sniffer for
recording original V1/V2/V3 infrared sessions as decoded bytes and raw timings.
The V2 `Version 1` / V3 `Others` fallback is hardware-verified but remains an
experimental protocol: the physical Tamagotchi randomly chooses a game or
gift, and games currently use the captured responder-win result.

Desktop 2.0 requires Tamagometer Enhanced Companion 2.0.0 or newer. Install
the `.exe` and `.fap` from the same release. Friends jewelry names remain
numbered until a complete ID-to-name mapping can be verified.

## Downloads

Ready-to-use builds are published on the
[GitHub Releases page](https://github.com/MintCarasique/tamagometer-enhanced/releases):

- [Download `TamagometerDesktop.exe`](https://github.com/MintCarasique/tamagometer-enhanced/releases/latest/download/TamagometerDesktop.exe)
- [Download `tamagometer_enhanced.fap`](https://github.com/MintCarasique/tamagometer-enhanced/releases/latest/download/tamagometer_enhanced.fap)

Each release also includes `SHA256SUMS.txt`. The FAP is built with the latest
official Flipper release SDK available when the release is created.

## Installation

1. Connect the Flipper Zero and open qFlipper.
2. Download `tamagometer_enhanced.fap` from the latest GitHub Release and copy
   it to `SD Card/apps/Tools`.
3. Close qFlipper so it releases the USB serial port.
4. On the Flipper, open **Apps → Tools → Tamagometer Enhanced** and leave it open.
5. Download and start `TamagometerDesktop.exe` from the same release.
6. Select the Flipper COM port and click **Connect**.

The likely Flipper port is selected automatically. After a successful manual
connection, unplugging and reconnecting the same Flipper triggers automatic
reconnection and another Companion compatibility check.

The enhanced companion replaces the original Catalog Companion for this
desktop application. It retains Connection infrared support and adds the
`friends` LF RFID command. Do not keep both Companion versions open at once,
because both register the same `tamagometer` USB CLI command.

## Sending a Connection 2024 gift

1. Select **Connection 2024 · IR**.
2. Choose a gift and click **Wait and send gift**.
3. On the Tamagotchi, choose **Connection → Present** and start the connection.
4. Align the infrared ports until the desktop confirms completion.

The physical Tamagotchi initiates this exchange because the initiator receives
the gift.

## Original Connection V2/V3 fallback

1. Select **Original V2/V3 · IR** and click **Start fallback**.
2. On an original V2 choose **Version 1**, or on an original V3 choose
   **Others**.
3. Start the connection and point the Tamagotchi IR window at the Flipper.
4. Keep both devices still until the activity and peer model are reported.

The Tamagotchi randomly chooses a game or gift. The current game response uses
the hardware-captured responder-win outcome; a concrete gift cannot be chosen
because the receiving Tamagotchi determines the displayed gift locally.

## Sending a Tamagotchi Friends BFF reward

1. Select **Friends · LF RFID**.
2. Choose jewelry or a Gotchi Point outcome.
3. On Tamagotchi Friends, open **BFF BUMP** and start a bump.
4. Hold the back of the Tamagotchi directly against the Flipper's LF RFID
   antenna.
5. Click **Send BFF reward** and keep the devices together while the progress
   indicator advances from 0/10 to 10/10 (about 12 seconds).

## Clone the repository

The Flipper companion is a Git submodule. Clone both repositories with:

```powershell
git clone --recurse-submodules https://github.com/MintCarasique/tamagometer-enhanced.git
cd tamagometer-enhanced
```

If the main repository was cloned without the submodule, initialize it with:

```powershell
git submodule sync --recursive
git submodule update --init --recursive
```

## Development

### Desktop application

The desktop source is in [`desktop/`](desktop/). It requires Python and
`pyserial`:

```powershell
cd desktop
python -m pip install -r requirements-dev.txt
python app.py
```

Run its protocol tests with:

```powershell
python -m unittest discover -s tests -v
```

Create the same Qt-only standalone Windows build used by GitHub Actions:

```powershell
python tools/build_desktop.py --mode onefile --dist-dir ../release --clean
```

During the 3.0 migration, `python app.py` starts the Qt interface and
`python app.py --tk` starts the retained Tkinter interface.
Release packaging intentionally starts from `qt_app.py`, so Tcl/Tk is not
included in the distributed executable. See
[`desktop/THIRD_PARTY_NOTICES.md`](desktop/THIRD_PARTY_NOTICES.md) for runtime
licenses and [`desktop/HARDWARE_SMOKE_TEST.md`](desktop/HARDWARE_SMOKE_TEST.md)
for the pre-release physical-device checklist.

### Flipper companion

The companion source is in the [`flipper/`](flipper/) submodule. Install
[uFBT](https://github.com/flipperdevices/flipperzero-ufbt), then run:

```powershell
cd flipper
ufbt
```

The generated application is written to `flipper/dist/tamagometer_enhanced.fap`.

### Continuous integration and releases

GitHub Actions runs the desktop tests and builds both binaries for pushes and
pull requests. Successful builds are available as temporary workflow artifacts.

Tags matching `v*` additionally create a GitHub Release containing the Windows
executable, Flipper application, checksums, and readable notes taken from the
matching version section in [`CHANGELOG.md`](CHANGELOG.md). Add that section
before pushing a release tag:

```powershell
$version = "2.0.1"
git tag -a "v$version" -m "Tamagometer Enhanced $version"
git push origin "v$version"
```

## Repository layout

```text
artifacts/              Information about downloading generated builds
desktop/                Modern Windows desktop application and tests
flipper/                Enhanced Companion Git submodule
pico/                   Original Raspberry Pi Pico bridge
web_interface_vue/      Original browser interface
Protocol.md             Connection protocol documentation
```

The original web application remains available at
[zacharesmer.github.io/tamagometer](https://zacharesmer.github.io/tamagometer/).

## Credits

- Connection support is derived from Zach Resmer's MIT-licensed
  [Tamagometer](https://github.com/zacharesmer/tamagometer) and
  [Flipper companion](https://github.com/zacharesmer/tamagometer-companion-flipper).
- Tamagotchi Friends packet data and LF RFID timings are based on Natalie
  Silvanovich's [Tamagotchi-Hack](https://github.com/natashenka/Tamagotchi-Hack)
  research and MrBlinky's published packet captures.

This project is unofficial and is not affiliated with Bandai or the
Tamagotchi brand. See [`LICENSE.md`](LICENSE.md) for licensing information.
