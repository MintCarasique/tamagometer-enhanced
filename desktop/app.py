"""Entry point for Tamagometer Desktop."""

from tamagometer_desktop.window import TamagometerDesktop


def main() -> None:
    TamagometerDesktop().mainloop()


if __name__ == "__main__":
    main()
