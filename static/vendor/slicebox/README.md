# Tympanus / Codrops Slicebox vendor

This directory vendors the original Slicebox demo engine used by Phase50.A.2K.

- Reference demo: https://tympanus.net/Development/Slicebox/index.html
- Plugin source: https://tympanus.net/Development/Slicebox/js/jquery.slicebox.js
- Plugin version: 1.1.0
- License: MIT (license header retained in `js/jquery.slicebox.js`)
- Verified official/vendor SHA-256 on 2026-09-17:
  `246DA4F1AFD789CC1AEA2F410AE4CCCD321DDFD40485376C1406046EFFE7A92D`

The original engine and reference navigation/shadow assets are kept local so the public Hero does not depend on Tympanus at runtime. The project wrapper only supplies 3DPrintHub content, RTL caption handling, responsive sizing, autoplay/play/pause, dots, and the combined Example 2/3/4 options requested by the owner.
