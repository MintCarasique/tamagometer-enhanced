# Tamagometer Enhanced

This fork adds a modern Windows desktop application and support for
**Tamagotchi Friends BFF BUMP** through the Flipper Zero's LF RFID hardware,
while retaining the original Tamagotchi Connection 2024 infrared features.

- Desktop source and tests: [`desktop/`](desktop/)
- Enhanced Flipper companion source: [`flipper/`](flipper/)
- Ready-to-install Windows and Flipper builds: [`artifacts/`](artifacts/)

Friends support has been verified successfully with a physical Tamagotchi
Friends and Flipper Zero. See the [desktop instructions](desktop/README.md) for
installation and usage.

## Original web application

Check out the original web app here: https://zacharesmer.github.io/tamagometer/

# Hardware
## Flipper Zero
The simplest way to get started is with a Flipper Zero. (Not the cheapest,though--for that see the DIY instructions)

1. Install the "Tamagometer" app from the Flipper App Catalog (on the Flipper Mobile App or qFlipper).
2. Launch the Tamagometer app on the Flipper.
3. Connect the Flipper Zero to your computer via a USB-C cable.
4. Open [the web app](https://zacharesmer.github.io/tamagometer/) on your computer.
5. Follow the "Demo" instructions on [the web app](https://zacharesmer.github.io/tamagometer/) to connect to your Flipper device!

Note: the screen on the Flipper Zero itself will not change upon being connected to the computer/web app, but if the app is open, it is waiting for commands in the background.

If the Tamagometer web app is not registering the Flipper Zero that is connected, make sure your USB-C cable supports data transfer (some only support charging). As a basic connection test, if you can use your flipper with https://lab.flipper.net/ or qFlipper, then the USB cable is working correctly. (Note: the flipper can only be connected to one program at a time, so close lab.flipper.net and qflipper before using the tamagometer).

The [Flipper app source code](https://github.com/zacharesmer/tamagometer-companion-flipper) is also available if you'd like to modify it or build it yourself. It is also in the `flipper` folder of this repo as a submodule, so if you want to clone it all at once use `git clone --recursive https://github.com/zacharesmer/tamagometer.git`

## DIY/Bring Your Own Board
If you don't have a Flipper, you can make your own transmitter/receiver from a Raspberry Pi Pico. The firmware is written in MicroPython, so you'll need to prepare the Pico to run micropython programs. It might work on other boards that can run micropython, but I haven't tested any. 

1. Load the MicroPython firmware onto your pico so that it will be able to run this program. Instructions and a link to the file are on the raspberry pi website here: https://www.raspberrypi.com/documentation/microcontrollers/micropython.html
2. Copy all files in the `pico` folder onto the pico. 
3. Unplug the pico and plug it back in, and main.py will run automatically.

(To prepare the board and load the files you can also use an IDE like Thonny or VSCode with the MicroPico extension. Please note that if one of those is connected to the board, the web UI will break in some weird ways. I will try and make it break in some less weird ways, but it will never work if you're also connected to the board with Thonny or MicroPico or minicom or something)

### Parts
- Raspberry Pi Pico
- A 38kHz IR receiver 
- A 38kHz IR transmitter
- Wires/header pins/usb cable for power

I haven't tested with an ESP32 or any other boards but it should probably work as long as it can run micropython? Definitely let me know if you try it with one and it works!

[This looks like the receiver I used](https://www.ebay.com/itm/172087478029), and [this looks like the transmitter](https://www.ebay.com/itm/294328064400). I didn't actually order either of those from those sellers, so I'm not recommending those in particular. There are also bundles on Amazon and AliExpress with receivers and transmitters, and Adafruit even sells a transceiver where both are built into one chip. The important things to check for:

- They must deal with the 38kHz modulation in hardware. A plain IR LED or an analog sensor will not work with the firmware as it is written. It would not be very hard to make it work with a regular LED, I just didn't yet. Contributions are welcome if you make that work and want to share!
- If you get something that only works on 5V, you'll need a level shifter since the pico GPIO puts out 3.3V

### Pins
- Transmitter power: GPIO 2
- Transmitter data: GPIO 3
- Receiver power: GPIO 6
- Receiver data: GPIO 7

To use different pins, change the pin numbers at the top of `rx.py` and `tx.py` to match your setup.

### Troubleshooting
#### Serial reset (not implemented yet)
I plan to add a button in the settings to fully reset/forget the previous serial connections to the page. If you need to do that before the button is added, run 
```javascript
(await navigator.serial.getPorts()).forEach(port => port.forget())
```
in the devtools console.

The device that the page connects to is the first one in the list: `(await navigator.serial.getPorts())[0]`. This could be annoying if you have multiple boards connected for some reason, so I plan to add a setting to adjust that as well.

#### Linux
On Linux if you're getting errors about permissions, you may have to add yourself to the dialout group:

`sudo usermod -aG dialout` 

(Or equivalently, `sudo usermod --append --groups dialout`. Do not leave out the `a` or `--append` or you'll be removed from any groups other than dialout)

# Web interface
The web interface allows you to edit infrared codes and send them to a tamagotchi. It will be updated as I learn more about what the different bits in the transmission represent.  

It uses the WebSerial API, which only works in Chromium browsers for now.

## Conversation
This is the area to edit a conversation, then send it and/or save it. Everything is stored locally on your computer.

### Editing individual bits
Click on any bit to flip it. This will update the checksum and, if it's known, the displayed value.

### Editing larger structures
For any known parts of the transmission, select from a list of possible values. You can toggle whether to see the bits for the known parts in the settings.

## Record
This allows you to snoop/listen in on a conversation between two tamagotchis. You can add the recorded messages to a conversation and save it for later.

## View Saved
Recorded messages are saved locally on your computer using IndexedDB. **If you clear your cookies and cache or site storage you will lose your saved messages!** Please back them up by  using the export button to save them as a file so that you can add them back if this happens. Importing a file will add onto any existing saved messages; it won't overwrite them.

# Extra info

I wrote a bit about the process of making this in a blog post: https://resmer.co.za/ch/posts/tamagometer/

And there are [some slides from a talk at DCFurs 2025](extra/DCFurs-Slides.pdf)

# Prior Art and References
- [This Tamagotchi reverse engineering project by Natalie Silvanovich](https://github.com/natashenka/Tamagotchi-Hack/tree/master) helped a ton 
- The corresponding CCC talks: 
    - [Many Tamagotchis Were Harmed In the Making of This Presentation](https://media.ccc.de/v/29c3-5088-en-many_tamagotchis_were_harmed_in_the_making_of_this_presentation_h264#t=0) 
    - [Even More Tamagotchis Were Harmed In the Making of This Presentation](https://media.ccc.de/v/30C3_-_5279_-_en_-_saal_1_-_201312291715_-_even_more_tamagotchis_were_harmed_in_the_making_of_this_presentation_-_natalie_silvanovich)
- Tamagotchi fandom wiki https://tamagotchi.fandom.com/wiki/Main_Page

# Disclaimer
This project is entirely unofficial and not affiliated with Tamagotchi or Bandai. 
