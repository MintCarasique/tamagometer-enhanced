# Tamagometer Desktop

A focused Windows utility for interacting with Tamagotchi devices through a
Flipper Zero. The interface supports three distinct protocols:

- **Tamagotchi Connection v3 2024 re-release** — send any of 181 gifts over IR.
- **Tamagotchi Friends** — choose one of 60 jewelry outcomes or a 200–1,000
  Gotchi Point reward for BFF BUMP over low-frequency RFID.
- **Original Connection V2/V3** — run the hardware-verified `Version 1` /
  `Others` random game-or-gift compatibility fallback over IR.

The app is unofficial and is not affiliated with Bandai.

## Desktop 2.0 UI

The current development version adds first-run setup and automatic connection,
an animated IR/LF placement guide, light and dark themes, inline notifications,
real transfer progress, categories, favorites, recently sent items, **Repeat
last transfer**, single-file diagnostic export, and original V2/V3 fallback.

Connection item previews reuse the sprites already present in the upstream
Tamagometer web interface. The upstream set provides a usable image for 171 of
181 catalog entries; the remaining items show a text fallback.

Friends jewelry remains numbered `#01–60`.
[Published protocol research](https://natashenka.ca/emulating-the-tamagotchi-friends-nfc/)
confirms that outcome bytes 0–59 follow the collection-screen order, but the
available [public jewelry table](https://tamagotchi.fandom.com/wiki/Jewelry)
does not contain a complete, verified set of all 60 names and images. The
desktop therefore avoids presenting a guessed mapping.

## Install the enhanced Flipper companion

Friends does not use infrared, so the original Tamagometer Companion from the
Flipper Catalog is not sufficient. Download
[`tamagometer_enhanced.fap`](https://github.com/MintCarasique/tamagometer-enhanced/releases/latest/download/tamagometer_enhanced.fap)
from the latest GitHub Release:

1. Connect the Flipper and open qFlipper.
2. Copy the `.fap` to `SD Card/apps/Tools`.
3. Disconnect or close qFlipper.
4. On the Flipper, open **Apps → Tools → Tamagometer Enhanced** and leave it open.
5. Connect the Flipper by USB in Tamagometer Desktop.

The enhanced companion retains Connection IR support, so it replaces the
Catalog version for both modes. Release FAPs are built with the latest official
Flipper release SDK available at build time.

Desktop 2.0 performs a capability handshake during connection and requires the
matching Tamagometer Enhanced Companion 2.0.0 or newer. It automatically picks
a likely Flipper COM port and reconnects when a previously connected Flipper
returns after a USB interruption.

## Connection 2024 gifts

1. Select **Connection 2024 · IR** and connect the COM port.
2. Choose a gift and click **Wait and send gift**.
3. On the Tamagotchi, select **Connection → Present** and start the connection.
4. Align the IR ports until the exchange completes.

The physical Tamagotchi initiates the exchange because the initiator receives
the gift.

## Original Connection V2/V3 fallback

1. Select **Original V2/V3 · IR** and connect the COM port.
2. Click **Start fallback**.
3. On V2 choose **Version 1**, or on V3 choose **Others**, and start the
   connection.
4. Align the IR ports until the Desktop reports the random activity and peer.

Games currently use the captured responder-win result. Gifts are chosen by the
receiving Tamagotchi rather than selected by the Desktop.

## Tamagotchi Friends BFF rewards

1. Select **Friends · LF RFID** and connect the COM port.
2. Choose jewelry or a Gotchi Point outcome.
3. On Tamagotchi Friends, open **BFF BUMP** and start a bump.
4. Hold the back of the Tamagotchi directly against the Flipper's LF RFID
   antenna, then click **Send BFF reward**. Keep the devices together while the
   progress indicator advances through all 10 repetitions (about 12 seconds).

Friends support emulates the documented receiver side of BFF BUMP. It does not
claim support for Exchange, Visit Bump, Mail, or Special modes.

The BFF reward flow has been verified successfully with a physical Tamagotchi
Friends and Flipper Zero.

## Run from source

Install Python 3 and the dependency, then run:

```powershell
python -m pip install -r requirements.txt
python app.py
```

Run the protocol tests with:

```powershell
python -m unittest discover -s tests -v
```

The Flipper source is in the repository's [`flipper/`](../flipper/) submodule and builds with
[uFBT](https://github.com/flipperdevices/flipperzero-ufbt).

## Desktop architecture

`app.py` is intentionally limited to application startup. The desktop package
is split by responsibility:

- `tamagometer_desktop/window.py` — Tk window and UI event handling;
- `tamagometer_desktop/theme.py` — colors and ttk styles;
- `tamagometer_desktop/modes.py` — supported modes and item catalogs;
- `tamagometer_desktop/settings.py` — configuration persistence;
- `tamagometer_desktop/transfer.py` — background transfer orchestration.
- `tamagometer_desktop/catalog.py` — categories, favorites keys, and sprite mapping;
- `tamagometer_desktop/alignment.py` — animated IR/LF placement guide;
- `tamagometer_desktop/onboarding.py` — first-run setup;
- `tamagometer_desktop/diagnostics.py` — privacy-conscious report export.

Protocol encoding and serial transport remain isolated in `tamagometer_core.py`,
`friends_core.py`, `flipper_serial.py`, and the shared structured states in
`transfer_status.py`.

## Protocol sources

Connection support is derived from Zach Resmer's MIT-licensed
[Tamagometer](https://github.com/zacharesmer/tamagometer). Friends packet data
and LF RFID timings are based on Natalie Silvanovich's
[Tamagotchi-Hack](https://github.com/natashenka/Tamagotchi-Hack) research and
MrBlinky's published Tamagotchi Friends packet captures.
