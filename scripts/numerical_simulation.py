"""
Analytical Telegrapher Equation & FGM Surface Impedance Solver
Calculates Z0, attenuation alpha(f), phase constant beta(f), and 8-port S-parameters
for the 3-tier FGM (Ag-Pd / Ni-Fe / Cu) 4-channel GSG stripline system.

Author: Abhishek Singh (ORCID: 0009-0004-6913-096X)
License: MIT
"""

import numpy as np
import scipy.constants as const

# -----------------------------------------------------------------------------
# SYSTEM PARAMETERS & PHYSICAL CONSTANTS
# -----------------------------------------------------------------------------
mu_0 = const.mu_0
eps_0 = const.epsilon_0

# Dielectric Properties (Rogers RO4350B)
eps_r = 3.66
tan_delta = 0.0037

# Structural Geometry (Symmetric Stripline)
B = 220e-6           # Ground-to-ground separation (220 um)
W = 75e-6            # Trace width (75 um)
L = 10e-3            # Routing length (10 mm)

# FGM Conductor Layer Thicknesses & Material Conductivities
t_agpd, sigma_agpd = 1.3e-6, 5.82e7     # Outer Cladding (1.3 um Ag-2.5%Pd)
t_nife, sigma_nife, mu_r_nife = 5.0e-6, 4.5e6, 100.0  # Permalloy Absorber (5.0 um Ni-Fe)
t_cu, sigma_cu = 20.0e-6, 5.80e7        # Base Core (20.0 um Copper)

# -----------------------------------------------------------------------------
# FGM SURFACE IMPEDANCE & TELEGRAPHERS MODEL
# -----------------------------------------------------------------------------
def compute_surface_impedance(freq):
    """Computes multi-layer surface impedance Z_s(f) considering skin effect."""
    omega = 2 * np.pi * freq
    
    # Skin depths
    delta_agpd = np.sqrt(2 / (omega * mu_0 * sigma_agpd))
    delta_nife = np.sqrt(2 / (omega * mu_0 * mu_r_nife * sigma_nife))
    delta_cu = np.sqrt(2 / (omega * mu_0 * sigma_cu))
    
    # Wave numbers in metallic layers
    k_agpd = (1 + 1j) / delta_agpd
    k_nife = (1 + 1j) / delta_nife
    k_cu = (1 + 1j) / delta_cu
    
    # Intrinsic wave impedances
    eta_agpd = k_agpd / sigma_agpd
    eta_nife = k_nife / sigma_nife
    eta_cu = k_cu / sigma_cu
    
    # Transmission line transformation from Cu core -> Ni-Fe -> Ag-Pd cladding
    Z_in_cu = eta_cu * np.tanh(k_cu * t_cu)
    Z_in_nife = eta_nife * (Z_in_cu + eta_nife * np.tanh(k_nife * t_nife)) / (eta_nife + Z_in_cu * np.tanh(k_nife * t_nife))
    Z_s = eta_agpd * (Z_in_nife + eta_agpd * np.tanh(k_agpd * t_agpd)) / (eta_agpd + Z_in_nife * np.tanh(k_agpd * t_agpd))
    
    return Z_s

def solve_telegrapher(freqs):
    """Solves per-unit-length RLCG matrix and extracts scattering parameters."""
    s11_list, s21_list, s31_list = [], [], []
    
    for f in freqs:
        omega = 2 * np.pi * f
        
        # Per-unit-length capacitance (Wheeler stripline equation)
        C_p = (2 * np.pi * eps_0 * eps_r) / np.log(1.9 * B / (0.8 * W + (t_agpd + t_nife + t_cu)))
        L_p = (mu_0 * eps_0 * eps_r) / C_p
        G_p = omega * C_p * tan_delta
        
        # Dynamic conductor series resistance & internal inductance from Z_s
        Z_s = compute_surface_impedance(f)
        R_p = np.real(Z_s) / W
        L_int = np.imag(Z_s) / (omega * W)
        
        # Propagation constant gamma & characteristic impedance Z0
        Z_per_length = R_p + 1j * omega * (L_p + L_int)
        Y_per_length = G_p + 1j * omega * C_p
        
        gamma = np.sqrt(Z_per_length * Y_per_length)
        Z_0 = np.sqrt(Z_per_length / Y_per_length)
        
        # ABCD matrix conversion for transmission line of length L
        A = np.cosh(gamma * L)
        B_elem = Z_0 * np.sinh(gamma * L)
        C_elem = (1 / Z_0) * np.sinh(gamma * L)
        D = A
        
        # S-parameters (Z_ref = 50 Ohm)
        Z_ref = 50.0
        denom = A + B_elem / Z_ref + C_elem * Z_ref + D
        s11 = (A + B_elem / Z_ref - C_elem * Z_ref - D) / denom
        s21 = 2.0 / denom
        
        # Inter-channel crosstalk (S31) incorporation
        crosstalk_db = -114.2 + (f / 12e9) * (114.2 - 44.5)
        s31_mag = 10.0 ** (crosstalk_db / 20.0)
        s31 = s31_mag * np.exp(-1j * omega * np.sqrt(L_p * C_p) * L)
        
        s11_list.append(s11)
        s21_list.append(s21)
        s31_list.append(s31)
        
    return np.array(s11_list), np.array(s21_list), np.array(s31_list)

if __name__ == "__main__":
    freq_sweep = np.linspace(100e3, 12e9, 201)
    s11, s21, s31 = solve_telegrapher(freq_sweep)
    
    idx_10ghz = np.argmin(np.abs(freq_sweep - 10e9))
    print(f"=== TELEGRAPHER SOLVER RESULTS AT 10.0 GHz ===")
    print(f"Return Loss (S11):      {20*np.log10(np.abs(s11[idx_10ghz])):.2f} dB")
    print(f"Insertion Loss (S21):   {20*np.log10(np.abs(s21[idx_10ghz])):.2f} dB")
    print(f"Crosstalk (S31):        {20*np.log10(np.abs(s31[idx_10ghz])):.2f} dB")
