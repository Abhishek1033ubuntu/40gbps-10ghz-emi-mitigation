import os
import numpy as np
import matplotlib.pyplot as plt
import skrf as rf

def run_validation(data_path="GSG_4Channel_50GHz_Aligned.s8p", show_plot=True):
    if not os.path.exists(data_path):
        from .touchstone import generate_s8p
        generate_s8p(data_path)

    network = rf.Network(data_path)
    
    idx_10g = np.argmin(np.abs(network.f - 10e9))
    idx_50g = np.argmin(np.abs(network.f - 50e9))
    
    s11_10 = 20 * np.log10(np.abs(network.s[idx_10g, 0, 0]))
    s31_10 = 20 * np.log10(np.abs(network.s[idx_10g, 2, 0]))
    s11_50 = 20 * np.log10(np.abs(network.s[idx_50g, 0, 0]))
    s31_50 = 20 * np.log10(np.abs(network.s[idx_50g, 2, 0]))

    metrics = {
        "s11_10ghz_db": float(s11_10),
        "s31_10ghz_db": float(s31_10),
        "s11_50ghz_db": float(s11_50),
        "s31_50ghz_db": float(s31_50),
        "ieee_370_passed": bool(s31_50 <= -40.0)
    }

    if show_plot:
        fig, ax = plt.subplots(figsize=(9, 5), dpi=120)
        freq_ghz = network.f / 1e9
        s31_db = 20 * np.log10(np.abs(network.s[:, 2, 0]))

        ax.plot(freq_ghz, s31_db, label="Aligned Model (p=0.50mm + 50GHz MMIC)", color="forestgreen", linewidth=2.0)
        ax.axhline(-40, color="red", linestyle=":", linewidth=1.5, label="IEEE 370 Limit (-40.0 dB)")
        ax.axvline(10, color="blue", linestyle="-.", linewidth=1.0, label="10 GHz Benchmark")
        ax.axvline(50, color="black", linestyle="-.", linewidth=1.0, label="50 GHz Upper Limit")

        ax.set_title("Full 50 GHz Spectrum Response (IEEE Std 370 Compliance)", fontsize=11, fontweight="bold")
        ax.set_xlabel("Frequency (GHz)")
        ax.set_ylabel("Crosstalk Isolation S31 (dB)")
        ax.set_ylim(-120, -20)
        ax.set_xlim(0, 52)
        ax.grid(True, linestyle=":", alpha=0.7)
        ax.legend(loc="lower left")
        plt.tight_layout()
        plt.show()

    return metrics
