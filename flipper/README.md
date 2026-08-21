# Tamagometer Enhanced Companion

This Flipper Zero app exposes the `tamagometer` USB CLI command used by the
desktop utility. It supports both Connection 2024 infrared exchanges and the
low-frequency RFID BFF response used by Tamagotchi Friends.

Build with [uFBT](https://github.com/flipperdevices/flipperzero-ufbt):

```powershell
ufbt
```

Copy the resulting `.fap` to `apps/Tools` on the Flipper SD card and keep the
app open while using Tamagometer Desktop. Remove or close the original Catalog
Companion first, because both apps register the same CLI command.
