<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

Explain how your project works

### Round Counter
The RoundCounter keeps track of which round the algorithm is on and signals when the final round has been reached. AES runs a different number of rounds depending on key size (10, 12, or 14). For us, we are using AES-256 so we will be doing 14 rounds. When the counter increments past 14, it will automatically reset to 0.

## How to test

Explain how to use your project

## External hardware

List external hardware used in your project (e.g. PMOD, LED display, etc), if any
