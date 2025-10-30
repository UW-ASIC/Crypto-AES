# MixColumns Module

## How it works

`MixColumns` implements the AES transformation that mixes each column of the 128-bit AES state using arithmetic in **GF(2⁸)**.  
Each column is treated as a 4-byte vector and multiplied by a fixed polynomial matrix:

02 03 01 01  
01 02 03 01  
01 01 02 03  
03 01 01 02  

This operation diffuses the influence of every input byte across the entire column, improving resistance to differential and linear attacks.  
In the **final AES round**, this transformation is bypassed using the `final_round` signal, as required by the AES standard.

---

### Port Interface

| Signal        | Direction | Width   | Description                                  |
|---------------|------------|----------|----------------------------------------------|
| `state_in`    | Input      | 128 bit | AES state input (column-major order)         |
| `final_round` | Input      | 1 bit   | 1 = bypass MixColumns (final round)          |
| `state_out`   | Output     | 128 bit | Mixed or bypassed AES state output           |

---

## How to test

1. **Testbench:** `tb_MixColumns.v` located in `/test/`  
2. **RTL module:** `MixColumns.v` located in `/src/`
3. **Simulation example (Icarus Verilog):**

   ```bash
   iverilog -o tb_MixColumns.vvp src/MixColumns.v test/tb_MixColumns.v
   vvp tb_MixColumns.vvp
