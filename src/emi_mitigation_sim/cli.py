import argparse
from .simulator import run_validation

def main():
    parser = argparse.ArgumentParser(description="Run 50 GHz IEEE 370 EMI Mitigation Signal Integrity Simulation.")
    parser.add_argument("--file", type=str, default="GSG_4Channel_50GHz_Aligned.s8p", help="Output Touchstone file path")
    parser.add_argument("--no-plot", action="store_true", help="Disable plotting graphical display")
    args = parser.parse_args()

    print("=== Running 50 GHz EMI Mitigation Validation Engine ===")
    results = run_validation(data_path=args.file, show_plot=not args.no_plot)
    print("\nSimulation Performance Metrics:")
    for key, val in results.items():
        print(f"  {key}: {val}")

if __name__ == "__main__":
    main()
