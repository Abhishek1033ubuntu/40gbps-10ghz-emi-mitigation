import os
import numpy as np

def generate_s8p(output_filename="GSG_4Channel_50GHz_Aligned.s8p"):
    freqs = np.linspace(1e5, 50e9, 501)
    num_ports = 8
    z0 = 50.0

    header = f"""! 8-Port S-Parameter Touchstone File - Full 50 GHz Band
! System: 4-Channel GSG 50-Ohm Stripline @ 50 GHz (FGM + p=0.50mm SIW + Active MMIC)
! Author: Abhishek Singh (ORCID: 0009-0004-6913-096X)
# Hz S MA R {z0}
"""
    lines = [header]

    for f in freqs:
        s11_mag = 0.03 + 0.02 * (f / 50e9)
        s31_db = -56.0 + (f / 50e9) * 13.98
        s31_mag = 10.0 ** (s31_db / 20.0)
        
        row_str = f"{f:.6e}"
        for i in range(num_ports):
            for j in range(num_ports):
                if i == j:
                    mag, phase = s11_mag, 0.0
                elif (i == 2 and j == 0) or (i == 0 and j == 2):
                    mag, phase = s31_mag, -72.0 * (f / 10e9)
                else:
                    mag, phase = 0.0001, 0.0
                row_str += f"  {mag:.6e} {phase:.2f}"
        lines.append(row_str + "\n")

    with open(output_filename, "w") as f:
        f.writelines(lines)
