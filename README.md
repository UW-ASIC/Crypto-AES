![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg) ![](../../workflows/fpga/badge.svg)

# Tiny Tapeout Verilog Project Template

- [Read the documentation for project](docs/info.md)

<details><summary>Explanation on Tiny Tapeout and Setting up Project</summary>

## What is Tiny Tapeout?

Tiny Tapeout is an educational project that aims to make it easier and cheaper than ever to get your digital and analog designs manufactured on a real chip.

To learn more and get started, visit https://tinytapeout.com.

## Set up your Verilog project

1. Add your Verilog files to the `src` folder.
2. Edit the [info.yaml](info.yaml) and update information about your project, paying special attention to the `source_files` and `top_module` properties. If you are upgrading an existing Tiny Tapeout project, check out our [online info.yaml migration tool](https://tinytapeout.github.io/tt-yaml-upgrade-tool/).
3. Edit [docs/info.md](docs/info.md) and add a description of your project.
4. Adapt the testbench to your design. See [test/README.md](test/README.md) for more information.

The GitHub action will automatically build the ASIC files using [OpenLane](https://www.zerotoasiccourse.com/terminology/openlane/).

## Enable GitHub actions to build the results page

- [Enabling GitHub Pages](https://tinytapeout.com/faq/#my-github-action-is-failing-on-the-pages-part)

## Resources

- [FAQ](https://tinytapeout.com/faq/)
- [Digital design lessons](https://tinytapeout.com/digital_design/)
- [Learn how semiconductors work](https://tinytapeout.com/siliwiz/)
- [Join the community](https://tinytapeout.com/discord)
- [Build your design locally](https://www.tinytapeout.com/guides/local-hardening/)

## What next?

- [Submit your design to the next shuttle](https://app.tinytapeout.com/).
- Edit [this README](README.md) and explain your design, how it works, and how to test it.
- Share your project on your social network of choice:
  - LinkedIn [#tinytapeout](https://www.linkedin.com/search/results/content/?keywords=%23tinytapeout) [@TinyTapeout](https://www.linkedin.com/company/100708654/)
  - Mastodon [#tinytapeout](https://chaos.social/tags/tinytapeout) [@matthewvenn](https://chaos.social/@matthewvenn)
  - X (formerly Twitter) [#tinytapeout](https://twitter.com/hashtag/tinytapeout) [@tinytapeout](https://twitter.com/tinytapeout)
</details>

# Project Description
This project implements a hardware version of the AES-256 encryption algorithm, designed to run efficiently within the Tiny Tapeout platform’s constraints. The system takes in plaintext data and a secret key, then transforms the plaintext into ciphertext through a series of controlled rounds. At the heart of the design is the AESState module, which acts as both the input loader and the working state register. It first collects 16 bytes of plaintext, one per clock cycle, until a complete 128-bit block is ready. Once loaded, it becomes the “memory” of the encryption engine — holding the intermediate 128-bit state as it is transformed during each of the 14 AES-256 rounds. Each round performs a sequence of operations: SubBytes substitutes every byte in the state with a new value from a lookup table to add nonlinearity; ShiftRows rearranges bytes to spread information across the block; MixColumns blends each column using finite-field arithmetic to further diffuse data; and AddRoundKey combines the state with a unique round key derived from the original 256-bit key. The KeyLoader is responsible for collecting the full 256-bit encryption key, while RoundKeyGen, supported by RconGen, expands that key into a series of per-round subkeys so that each transformation uses a different one. The RoundCounter keeps track of which round is in progress and signals when the final round is reached, ensuring the system runs for exactly 14 iterations. Overseeing everything is the Top-Level AESHash controller, which orchestrates the entire process — managing when to load input, when to advance rounds, and when to output the final ciphertext. Together, these modules form a complete AES-256 encryption pipeline where data flows smoothly from plaintext input to ciphertext output, illustrating both the structure and rhythm of real digital cryptographic hardware.