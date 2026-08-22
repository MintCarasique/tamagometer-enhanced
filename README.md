# Tamagometer Enhanced

Tamagometer Enhanced is an unofficial Windows utility for interacting with
Tamagotchi devices through a Flipper Zero. It combines the original
Tamagometer Connection 2024 infrared protocol with a simpler desktop interface
and Tamagotchi Friends BFF reward support over low-frequency RFID.

## Supported devices

| Device | Transport | Available operation | Status |
| --- | --- | --- | --- |
| Tamagotchi Connection v3 2024 re-release | Infrared | Send any of 181 gifts | Verified on hardware |
| Tamagotchi Friends | LF RFID | BFF BUMP: 60 jewelry outcomes and 200–1,000 Gotchi Points | Verified on hardware |

Tamagotchi Friends support currently covers the receiver side of **BFF BUMP**.
Exchange, Visit Bump, Mail, and Special modes are not implemented.

## Downloads

Ready-to-use builds are published on the
[GitHub Releases page](https://github.com/MintCarasique/tamagometer-enhanced/releases):

- [Download `TamagometerDesktop.exe`](https://github.com/MintCarasique/tamagometer-enhanced/releases/latest/download/TamagometerDesktop.exe)
- [Download `TamagometerEnhanced.fap`](https://github.com/MintCarasique/tamagometer-enhanced/releases/latest/download/TamagometerEnhanced.fap)

Each release also includes `SHA256SUMS.txt`. The FAP is built with the latest
official Flipper release SDK available when the release is created.

## Installation

1. Connect the Flipper Zero and open qFlipper.
2. Download `TamagometerEnhanced.fap` from the latest GitHub Release and copy
   it to `SD Card/apps/Tools`.
3. Close qFlipper so it releases the USB serial port.
4. On the Flipper, open **Apps → Tools → Tamagometer Enhanced** and leave it open.
5. Download and start `TamagometerDesktop.exe` from the same release.
6. Select the Flipper COM port and click **Connect**.

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

## Sending a Tamagotchi Friends BFF reward

1. Select **Friends · LF RFID**.
2. Choose jewelry or a Gotchi Point outcome.
3. On Tamagotchi Friends, open **BFF BUMP** and start a bump.
4. Hold the back of the Tamagotchi directly against the Flipper's LF RFID
   antenna.
5. Click **Send BFF reward** and keep the devices together until completion,
   which takes about 12 seconds.

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

Create a standalone Windows build with PyInstaller:

```powershell
pyinstaller --noconfirm --clean --onefile --windowed --name TamagometerDesktop app.py
```

### Flipper companion

The companion source is in the [`flipper/`](flipper/) submodule. Install
[uFBT](https://github.com/flipperdevices/flipperzero-ufbt), then run:

```powershell
cd flipper
ufbt
```

The generated application is written to `flipper/dist/tamagometer_companion.fap`.

### Continuous integration and releases

GitHub Actions runs the desktop tests and builds both binaries for pushes and
pull requests. Successful builds are available as temporary workflow artifacts.

Tags matching `v*` additionally create a GitHub Release containing the Windows
executable, Flipper application, generated release notes, and checksums:

```powershell
git tag v1.0.0
git push origin v1.0.0
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
