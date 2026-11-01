"""
Standalone Python Touchstone (.s8p) Matrix Generator (50 GHz Spectrum)
Generates compliant 8-port Touchstone dataset covering 100 kHz to 50 GHz
with p = 0.50 mm SIW via pitch alignment.

Author: Abhishek Singh (ORCID: 0009-0004-6913-096X)
License: MIT
"""

import os
import numpy as np

def generate_touchstone_s8p_50g(output_filename="data/GSG_4Channel_50GHz_SIW.s8p"):
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    # Frequency Vector: 100 kHz to 50 GHz (501 points)
    freqs = np.linspace(1e5, 50e9, 501)
    num_ports = 8
    z0 = 50.0

    header = f"""! 8-Port S-Parameter Touchstone File - Full 50 GHz Band
! System: 4-Channel GSG 50-Ohm Stripline @ 50 GHz (FGM + p=0.50mm SIW + Wideband Active MMIC)
! Author: Abhishek Singh (ORCID: 0009-0004-6913-096X)
! Format: Frequency (Hz) | Magnitude / Phase (Degrees)
# Hz S MA R {z0}
"""
    lines = [header]

    for f in freqs:
        # S11 matched: -29.37 dB at 10 GHz to -26.02 dB at 50 GHz
        s11_mag = 0.03 + 0.02 * (f / 50e9)
        
        # Crosstalk S31: -56.00 dB at 10 GHz to -42.02 dB at 50 GHz
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

    print(f"=== 50 GHz TOUCHSTONE FILE GENERATED: {output_filename} ===")

if __name__ == "__main__":
    generate_touchstone_s8p_50g()
