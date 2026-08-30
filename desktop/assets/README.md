# Bundled item sprites

The Connection item sprites in `item-sprites/` are copied from the legacy web
interface inherited from the upstream MIT-licensed
[Tamagometer](https://github.com/zacharesmer/tamagometer) project. The upstream
footer credits the Tamagotchi Wiki and MasterPengo as sprite sources.

The desktop uses these files only when an exact catalog-name mapping is
available. Items absent from the upstream sprite set use a text fallback rather
than an invented image.

Every file in `item-sprites/` is a real PNG. Some inherited assets originally
contained WebP data under a `.png` extension; `python tools/normalize_sprites.py`
performs the deterministic conversion and the catalog tests verify signatures
and decodeability.
