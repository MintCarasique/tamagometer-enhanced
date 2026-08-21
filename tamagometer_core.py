"""Protocol helpers for Tamagometer Desktop.

The message layout and starter conversation are based on Zach Resmer's
MIT-licensed Tamagometer project (https://github.com/zacharesmer/tamagometer).
"""

from __future__ import annotations

import re


MESSAGE_BITS = 160
GIFT_BYTE_START = 14 * 8

# Message 2 and message 4 from the upstream "Cone gift" starter conversation.
# In receiver mode the Tamagotchi sends messages 1 and 3; the desktop responds
# with these two templates. Byte 15 of message 4 selects the gift.
GIFT_RESPONSE_2 = (
    "0000111000000001101111110010001000101100000000010000111000000001101000001010000000000000011001000010001000000000000001000000000000000000000000000000000011110110"
)
GIFT_RESPONSE_4 = (
    # Upstream's experimental starter packet used 0x05 (Gift) here even
    # though message 3 requests 0x06 (Gift + Visit). The matching response is
    # 0x07. A mismatched 0x05 packet is received over IR but ends in FAIL.
    "0000111000000111101111110010001000101100000000010000111000000001101000001010000000000000000000000000000000000000100001000000000000000000000000000000000011110110"
)


_ITEM_NAMES = """Scone
Sushi
Bread
Cereal
Omelet
Milk
Hamburger
BBQ
Sandwich
Beef Bowl
Cheese
Pizza
Steak
Taco
Sausage on stick
Hot Dog
Pasta
Corn
Turkey
Noodle
Fried Chicken
Waffle
Choco Bar
Escargot
Octopus Sausage
Chikuwa
Rice Ball
Curry
Kobu Maki
Umeboshi
Natto
Fried Shrimp
Takoyaki
Oyster
Naruto
Pigs Feet
Cone
Pudding
Cake
Apple
Sundae
Banana
Fries
Roll Cake
Cupcake
Fruit Juice
Ice Cream
Cheese Cake
Apple Pie
Energy Drink
Corn Dog
Donut
Soda
Popcorn
Pear
Pineapple
Melon
Grapes
Chocolate Heart
Cookie
Whole Cake
Yogurt
Lollipop
Candy
Crepe Suzette
Cherry
Biscuit
Marron Cake
Cream Puff
Gum
Dango
Shaved Ice
Sweet Potato
Mochi
Peanuts
Toast
Crackers
Water
Ball
Pencil
Wig
Sunglasses
RC Car 1
Pen
Weights
RC Car 2 (duck)
RC Car 3
Bow
Darts
Building Block
Cap
Bow Tie
Wings
Hair Gel
Clock
Chest
Phonograph
Fishing Pole
Mirror
Make Up
Boom Box
Music Disc
Shirt
Shoes
Ticket 1
Ticket 2
Ticket 3
Ticket 4
Ticket 5
Doll 1
Umbrella
Lamp
Roller Blades
Action Figure
Stuffed Tama 1
Stuffed Tama 2
Trumpet
Drum
Throne
Music
Plant
Shovel
TV
Honey
Royal Costume
! ! (Clone)
Balloon
Rope
Doll 2
Tama Drink
Castle
Shaver
Cone (animation)
Flower (animation)
Poop (animation)
Jack in the Box
Cake (animation)
Heart (animation)
Snake (animation)
Nothing
Ghost (animation)
Sickness
Passport
Key
Key 2
Map
Book
Laptop
Medal
Cell Phone
Bicycle
Skis Souvenir
Island Souvenir
Surfboard Souvenir
Panda Souvenir
Maracas Souvenir
Diamond Ring
Cape
Crown
Skateboard
3 Balloons
Baseball Cap
Teddy Bear
Rare CD
Rare Shoes
Poster 1
Poster 2
Poster 3
Microphone
Suitcase
Trophy
Famous Picture
Small Crown
Glasses
Sword
Camera
Heart Key
Sparkly Heart
Sparkly Star
M Ball
Heart Ring""".splitlines()

GIFT_ITEMS = tuple(enumerate(_ITEM_NAMES))


def checksum(bits_without_checksum: str) -> int:
    """Return the unsigned byte-sum checksum used by Connection messages."""
    if len(bits_without_checksum) % 8 or not re.fullmatch(r"[01]+", bits_without_checksum):
        raise ValueError("Checksum input must be a whole number of binary bytes")
    return sum(int(bits_without_checksum[i:i + 8], 2)
               for i in range(0, len(bits_without_checksum), 8)) & 0xFF


def with_checksum(bits_without_checksum: str) -> str:
    return bits_without_checksum + f"{checksum(bits_without_checksum):08b}"


def make_gift_response(item_id: int) -> str:
    """Build message 4 for a gift id and recalculate its final checksum."""
    if not 0 <= item_id <= 180:
        raise ValueError("Gift id must be between 0 and 180")
    body = GIFT_RESPONSE_4[:MESSAGE_BITS - 8]
    body = body[:GIFT_BYTE_START] + f"{item_id:08b}" + body[GIFT_BYTE_START + 8:]
    return with_checksum(body)


def gift_response_type_for(request_message: str) -> int:
    """Return the required message-4 type for a received message 3."""
    if len(request_message) != MESSAGE_BITS or not re.fullmatch(r"[01]{160}", request_message):
        raise ValueError("Invalid request message")
    request_type = int(request_message[8:16], 2)
    response_types = {0x04: 0x05, 0x06: 0x07}
    if request_type not in response_types:
        raise ValueError(f"Expected gift request type 0x04 or 0x06, got 0x{request_type:02X}")
    return response_types[request_type]


def make_gift_response_for_request(item_id: int, request_message: str) -> str:
    """Build message 4 with a type that matches the live Tamagotchi request."""
    response = make_gift_response(item_id)
    body = response[:MESSAGE_BITS - 8]
    response_type = gift_response_type_for(request_message)
    body = body[:8] + f"{response_type:08b}" + body[16:]
    return with_checksum(body)


def validate_message(bits: str) -> bool:
    return (
        len(bits) == MESSAGE_BITS
        and re.fullmatch(r"[01]{160}", bits) is not None
        and int(bits[-8:], 2) == checksum(bits[:-8])
    )


assert len(GIFT_ITEMS) == 181
assert validate_message(GIFT_RESPONSE_2)
assert validate_message(GIFT_RESPONSE_4)
