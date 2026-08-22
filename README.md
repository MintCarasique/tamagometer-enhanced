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

Ready-to-use builds are stored in [`artifacts/`](artifacts/):

- [`TamagometerDesktop.exe`](artifacts/TamagometerDesktop.exe) — Windows desktop application.
- [`TamagometerEnhanced.fap`](artifacts/TamagometerEnhanced.fap) — enhanced Flipper Zero companion.

The included FAP targets official Flipper firmware 1.4.3 / API 87.1. If a
future firmware version reports that the app is incompatible, rebuild the
companion with the current uFBT SDK.

## Installation

1. Connect the Flipper Zero and open qFlipper.
2. Copy `artifacts/TamagometerEnhanced.fap` to `SD Card/apps/Tools`.
3. Close qFlipper so it releases the USB serial port.
4. On the Flipper, open **Apps → Tools → Tamagometer Enhanced** and leave it open.
5. Start `artifacts/TamagometerDesktop.exe`.
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
python -m pip install -r requirements.txt
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

## Repository layout

```text
artifacts/              Ready-to-install Windows and Flipper builds
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
