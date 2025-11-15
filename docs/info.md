<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

Explain how your project works

## How to test

Explain how to use your project

## External hardware

List external hardware used in your project (e.g. PMOD, LED display, etc), if any


## Round Key Generation

### How the AES Standard Defines the Process

The first 2 keys remain unchanged from the original value. The next keys are generated via key expansion which relies on previous values. 

There are 3 main conditions for this process:

-For every 8th word, rotate the previous word, apply the S-box to each byte, xor the round constant, and xor that with the word from 8 positions earlier.

-For the 4th word of every 8 word block, apply the S-box to each byte, thne xor that with the word from 8 positions earlier. (This step is unique to AES-256, not found in AES-128)

-For all other words, just xor the previous word with the word from 8 positions earlier.


### Implementation

The module uses a 2-phase design. When it recieves the signal to advance, it continuously outputs all 15 keys across 56 cycles, where 1 cycle is used to output the first 4 words to the shift registers, and the remaining 55 cycles are used to generate the 52 new words and shift the 52 + 4 original words into the output shift registers, for a total of 60 outputted words. 

### Testing Methodology

The branch test/roundkeygen includes a custom testbench for this module, based on the FIPS 197 standard document Section A.3 available here: https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197-upd1.pdf.

The testbench verifies that 15 round keys are produced, and displays the keys so that they can be compared to the document. This could also be automated in future.

### Integration Notes

Currently a pulse of the advance signal will result in all 15 round keys being produced. For top level integration, depending on the approach taken to manage timing between modules (e.g. if we choose to use a pipelining), it may be best to add a third phase (e.g. WAIT) that waits for a signal to continue running the EXPAND phase. Once count reaches 63, EXPAND can go back to IDLE. WAIT could use the advance signal to determine when to produce the next  key.

I've included the WAIT implementation in my code if needed during top level integration (it's all commented out).