from bb84_simulator import run_bb84

print("Noise 15% QBER across 5 seeds:")
for s in [42, 1, 7, 100, 200]:
    r = run_bb84(1000, 0.0, 0.15, 0.25, 0.11, s)
    qber = r["qber_pct"]
    verdict = r["verdict"]
    print(f"  Seed {s:3d}: QBER={qber:.2f}%  Verdict={verdict}")

print()
print("Eve 50% QBER across 5 seeds (expect ~12.5%):")
for s in [42, 1, 7, 100, 200]:
    r = run_bb84(1000, 0.5, 0.0, 0.25, 0.11, s)
    qber = r["qber_pct"]
    verdict = r["verdict"]
    print(f"  Seed {s:3d}: QBER={qber:.2f}%  Theory=12.50%  Verdict={verdict}")

print()
print("Eve 100% QBER across 5 seeds (expect ~25%):")
for s in [42, 1, 7, 100, 200]:
    r = run_bb84(1000, 1.0, 0.0, 0.25, 0.11, s)
    qber = r["qber_pct"]
    verdict = r["verdict"]
    print(f"  Seed {s:3d}: QBER={qber:.2f}%  Theory=25.00%  Verdict={verdict}")
