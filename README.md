# Tamagometer Desktop

A simple Windows utility for sending gifts to a **Tamagotchi Connection v3
2024 re-release (20th Anniversary)** through a Flipper Zero.

## Requirements

1. Install **Tamagometer Companion** from the Flipper App Catalog.
2. Open Companion on the Flipper and connect it with a data-capable USB cable.
3. Close qFlipper, Flipper Lab, and any other application using the COM port.
4. Run `TamagometerDesktop.exe`. For a source launch, install the dependencies
   with `python -m pip install -r requirements.txt`, then run `app.py`.

## Sending a gift

1. Select the COM port and click **Connect**.
2. Find and select a gift.
3. Click **Wait for Tamagotchi and send**.
4. On the Tamagotchi, select **Connection → Present**, start the connection,
   and align the IR ports.

The physical Tamagotchi must initiate the exchange because the initiator
receives the gift. The desktop application waits and acts as the other device.

## Compatibility

The protocol and starter conversation are derived from the MIT-licensed
[zacharesmer/tamagometer](https://github.com/zacharesmer/tamagometer) project.
Compatibility with other Connection generations is not claimed. This project
is unofficial and is not affiliated with Bandai.
