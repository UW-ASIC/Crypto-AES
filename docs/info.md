<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

### AES State
This module serves as both the input loader and the state register for AES-256 encryption.
At the start, it collects 8-bit plaintext bytes one by one until a full 128-bit block is formed — similar to typing 16 characters into a box before closing it and saying “ready.”

After that, during encryption rounds, it continues to hold and update the 128-bit AES state as it goes through transformations (SubBytes, ShiftRows, MixColumns, and AddRoundKey).

In short, this module is the “memory” of the AES engine — it loads the initial data and keeps track of its transformation through all 14 rounds of AES-256.

## How to test

Explain how to use your project

## External hardware

List external hardware used in your project (e.g. PMOD, LED display, etc), if any
