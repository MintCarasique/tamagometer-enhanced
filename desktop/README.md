# Tamagometer Desktop

A focused Windows utility for interacting with Tamagotchi devices through a
Flipper Zero. The interface supports two distinct protocols:

- **Tamagotchi Connection v3 2024 re-release** — send any of 181 gifts over IR.
- **Tamagotchi Friends** — choose one of 60 jewelry outcomes or a 200–1,000
  Gotchi Point reward for BFF BUMP over low-frequency RFID.

The app is unofficial and is not affiliated with Bandai.

## Install the enhanced Flipper companion

Friends does not use infrared, so the original Tamagometer Companion from the
Flipper Catalog is not sufficient. Install the bundled
[`tamagometer_enhanced.fap`](flipper/dist/tamagometer_enhanced.fap):

1. Connect the Flipper and open qFlipper.
2. Copy the `.fap` to `SD Card/apps/Tools`.
3. Disconnect or close qFlipper.
4. On the Flipper, open **Apps → Tools → Tamagometer Enhanced** and leave it open.
5. Connect the Flipper by USB in Tamagometer Desktop.

The enhanced companion retains Connection IR support, so it replaces the
Catalog version for both modes. It was built for official Flipper firmware
1.4.3 / API 87.1; rebuild it after a future firmware update if Flipper reports
that the app is incompatible.

## Connection 2024 gifts

1. Select **Connection 2024 · IR** and connect the COM port.
2. Choose a gift and click **Wait and send gift**.
3. On the Tamagotchi, select **Connection → Present** and start the connection.
4. Align the IR ports until the exchange completes.

The physical Tamagotchi initiates the exchange because the initiator receives
the gift.

## Tamagotchi Friends BFF rewards

1. Select **Friends · LF RFID** and connect the COM port.
2. Choose jewelry or a Gotchi Point outcome.
3. On Tamagotchi Friends, open **BFF BUMP** and start a bump.
4. Hold the back of the Tamagotchi directly against the Flipper's LF RFID
   antenna, then click **Send BFF reward**. Keep the devices together until the
   desktop confirms completion (about 12 seconds).

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

The Flipper source is in [`flipper/`](flipper/) and builds with
[uFBT](https://github.com/flipperdevices/flipperzero-ufbt).

## Protocol sources

Connection support is derived from Zach Resmer's MIT-licensed
[Tamagometer](https://github.com/zacharesmer/tamagometer). Friends packet data
and LF RFID timings are based on Natalie Silvanovich's
[Tamagotchi-Hack](https://github.com/natashenka/Tamagotchi-Hack) research and
MrBlinky's published Tamagotchi Friends packet captures.
