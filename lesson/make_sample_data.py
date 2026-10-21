"""Generate the Cosmic Lab sample-lesson dataset (simulated).

A Monte Carlo of the two-scintillator detector: two 15 x 15 cm tiles, 11 cm apart.
Muons arrive with the sea-level angular distribution (intensity ~ cos^2 theta) and a
vertical-equivalent flux of 1 per cm^2 per minute through a horizontal surface.
Each tile also sees random low-energy background hits (radioactivity, electronics).

Every row is one trigger: time_s, adc_A, adc_B  (0 = no signal above the readout threshold)
"""
import numpy as np

rng = np.random.default_rng(5)
T = 600.0                    # 10 minutes of running, seconds
TILE = 15.0                  # tile side, cm
GAP = 11.0                   # vertical distance A -> B, cm
FLUX = 1.0 / 60.0            # muons per cm^2 per second through a horizontal plane
GEN = 60.0                   # generation square at tile A height, cm
NOISE_RATE = 1.6             # background singles per tile per second
MEV_PER_CM = 2.0             # minimum-ionising energy loss in plastic
ADC_PER_MEV = 190.0          # detector gain
THRESH = 30                  # readout threshold, ADC

def moyal(n):                # Landau-like energy-loss fluctuations
    return -np.log(rng.chisquare(1, n))

n_mu = rng.poisson(FLUX * GEN**2 * T)
t_mu = np.sort(rng.uniform(0, T, n_mu))
cos_t = rng.uniform(0, 1, n_mu) ** 0.25           # cos^3 for flux through a flat surface
sin_t = np.sqrt(1 - cos_t**2)
phi = rng.uniform(0, 2*np.pi, n_mu)
xa, ya = rng.uniform(-GEN/2, GEN/2, (2, n_mu))
xb = xa + GAP * sin_t / cos_t * np.cos(phi)
yb = ya + GAP * sin_t / cos_t * np.sin(phi)
hitA = (abs(xa) < TILE/2) & (abs(ya) < TILE/2)
hitB = (abs(xb) < TILE/2) & (abs(yb) < TILE/2)

def deposit(n, cos):          # 1 cm thick tile, longer path when tilted
    e = MEV_PER_CM * (1.0 / cos) * (1 + 0.12 * moyal(n))
    return np.clip(e * ADC_PER_MEV * rng.normal(1, 0.08, n), 0, 4095)

keep = hitA | hitB
t, c = t_mu[keep], cos_t[keep]
A = np.where(hitA[keep], deposit(keep.sum(), c), 0)
B = np.where(hitB[keep], deposit(keep.sum(), c), 0)

# background singles: steeply falling spectrum, mostly below the muon peak
rows = [np.column_stack([t, A, B])]
for col in (1, 2):
    n = rng.poisson(NOISE_RATE * T)
    adc = THRESH + rng.exponential(55, n)
    z = np.zeros((n, 3)); z[:, 0] = rng.uniform(0, T, n); z[:, col] = adc
    rows.append(z)
ev = np.vstack(rows)
ev = ev[np.argsort(ev[:, 0])]
ev[:, 1:] = np.where(ev[:, 1:] < THRESH, 0, np.round(ev[:, 1:]))
ev = ev[(ev[:, 1] > 0) | (ev[:, 2] > 0)]

np.savetxt("muon_sample.csv", ev, fmt=["%.6f", "%d", "%d"], delimiter=",",
           header="time_s,adc_A,adc_B", comments="")
acc = (hitA & hitB).sum() / hitA.sum()
print(f"{len(ev)} triggers, {(hitA&hitB).sum()} true coincidences, acceptance B|A = {acc:.3f}")
