"""Single source for the Cosmic Lab sample lesson.
build_lesson.py turns this into sample-lesson.ipynb (Colab) and ../sample-lesson.html (in-browser)."""

TITLE = "Catch your first muons"
SUB = "A 30-minute taste of Cosmic Lab: real analysis steps, run in your browser."

CELLS = [
("md", """
### What you'll do

Every minute, about one muon passes through each square centimetre of the ground around you. In this lesson you will pick them out of raw detector signals, count them, measure the muon flux, and then use Einstein's special relativity to explain why they reach the ground at all.

You don't need any coding experience. Run each cell in order, read the output, then try the ✏️ challenges.

**About the data:** this sample is a 10-minute simulation of our two-scintillator detector (two 15 × 15 cm tiles, 11 cm apart). In the full class you analyse 100,000+ real events.
"""),

("md", """
### Step 1 · Load the data

Each row is one *trigger*: a moment when at least one tile saw a flash of light. The columns are the time in seconds and the signal size in each tile, in ADC units. A value of `0` means that tile saw nothing.
"""),
("code", """
import os, urllib.request
import numpy as np
import matplotlib.pyplot as plt

# Make plots match the Cosmic Lab look
plt.rcParams.update({"figure.facecolor": "#051C2C", "axes.facecolor": "#051C2C",
    "axes.edgecolor": "#6A849C", "axes.labelcolor": "#E6F0FA", "text.color": "#E6F0FA",
    "xtick.color": "#8AA2B7", "ytick.color": "#8AA2B7", "legend.facecolor": "#051C2C",
    "legend.edgecolor": "#6A849C", "figure.figsize": (7, 3.6)})

URL = "https://raw.githubusercontent.com/kimsiang/cosmiclab/main/lesson/muon_sample.csv"
if not os.path.exists("muon_sample.csv"):
    urllib.request.urlretrieve(URL, "muon_sample.csv")

data = np.loadtxt("muon_sample.csv", delimiter=",", skiprows=1)
time, adc_A, adc_B = data[:, 0], data[:, 1], data[:, 2]

print("Number of triggers:", len(data))
print("Running time:", round(time.max() / 60, 1), "minutes")
print()
print("  time (s)   adc_A   adc_B")
for row in data[:6]:
    print(f"{row[0]:9.3f} {row[1]:7.0f} {row[2]:7.0f}")
"""),

("md", """
### Step 2 · Signal or noise?

Not every flash is a muon. Natural radioactivity and electronic noise make small signals all the time. A muon crossing 1 cm of plastic always leaves a fairly large signal. Let's draw a histogram of the signal sizes in tile A and see the two populations.
"""),
("code", """
signals = adc_A[adc_A > 0]          # only the triggers where tile A fired

plt.hist(signals, bins=80, range=(0, 1200), color="#00A9F4")
plt.yscale("log")
plt.xlabel("Signal size in tile A (ADC)")
plt.ylabel("Number of hits")
plt.title("Noise on the left, muons on the right")
plt.show()
"""),
("md", """
The steep pile on the left is noise. The bump around 400 ADC is muons. We need a **threshold**: a cut that keeps the bump and throws away most of the pile.

✏️ **Challenge:** look at the plot and choose a threshold. Change the number below, then run the cell.
"""),
("code", """
THRESHOLD = 150      # ADC. Try 50, 150 and 300

muon_like_A = (adc_A > THRESHOLD).sum()
print("Hits in tile A above threshold:", muon_like_A)
"""),

("md", """
### Step 3 · Coincidence: the physicist's trick

A noise flash happens in one tile at a time. A muon flies straight through **both** tiles at nearly the speed of light, so both tiles fire in the same instant. Requiring A **and** B together is called a *coincidence*, and it removes almost all of the noise.
"""),
("code", """
is_muon = (adc_A > THRESHOLD) & (adc_B > THRESHOLD)    # & means AND

N = is_muon.sum()
print("Triggers in total:      ", len(data))
print("Tile A only or B only:  ", len(data) - N)
print("Muons (A AND B):        ", N)
"""),
("md", """
✏️ **Challenge:** go back, change `THRESHOLD` to 50, then to 300, and run Step 2's second cell and this cell again. Does the muon count change much? Why is coincidence counting so robust?
"""),

("md", """
### Step 4 · Is the rate steady?

Muons arrive at random times. Let's count how many we catch in each minute. Counting experiments have a natural spread: if you expect *N* counts, the typical wobble is about √*N*.
"""),
("code", """
muon_times = time[is_muon]
minutes = np.arange(0, 11)                      # bin edges: 0, 1, 2, ... 10 minutes
counts, _ = np.histogram(muon_times / 60, bins=minutes)

plt.bar(minutes[:-1] + 0.5, counts, width=0.8, color="#2251FF",
        yerr=np.sqrt(counts), ecolor="#00A9F4", capsize=3)
plt.axhline(counts.mean(), color="#FFB547", linestyle="--", label="average")
plt.xlabel("Minute")
plt.ylabel("Muons per minute")
plt.legend()
plt.show()

print("Average:", round(counts.mean(), 1), "muons per minute")
print("Expected wobble √N:", round(np.sqrt(counts.mean()), 1))
print("Actual spread:", round(counts.std(), 1))
"""),

("md", """
### Step 5 · Measure the muon flux

The **flux** is how many muons cross each square centimetre per minute.

There is one correction. A muon that enters tile A at a steep angle can miss tile B, which sits 11 cm below. A geometry simulation of our detector shows that 43.5% of the muons crossing tile A also cross tile B. This number is called the *acceptance*.
"""),
("code", """
area = 15 * 15             # tile area in cm²
minutes_run = 10
acceptance = 0.435         # from a geometry simulation of the detector

flux = N / (area * minutes_run * acceptance)
error = np.sqrt(N) / (area * minutes_run * acceptance)

print(f"Muon flux = {flux:.2f} ± {error:.2f} muons per cm² per minute")
print("Textbook value at sea level: about 1 per cm² per minute")
"""),
("md", """
That is a real physics measurement, done the way professional physicists do it: count, remove background, correct for the detector, and quote an uncertainty.
"""),

("md", """
### Step 6 · Why do muons reach the ground at all?

Muons are made about 15 km up, when cosmic rays hit the atmosphere. A muon lives for only τ = 2.2 microseconds on average. Even at almost the speed of light, that is only enough time to travel about 660 m.

So by Newton's physics, almost none should survive the 15 km trip. Einstein's special relativity says a fast-moving clock runs slow by a factor γ (gamma). The muon's lifetime, as measured from the ground, becomes γτ.
"""),
("code", """
c = 3.0e8              # speed of light, m/s
tau = 2.2e-6           # muon lifetime, s
height = 15_000        # where muons are made, m

beta = 0.9992          # ✏️ speed as a fraction of c. Try 0.99 or 0.9999
v = beta * c
gamma = 1 / np.sqrt(1 - beta**2)

L_newton = v * tau                 # average distance before decay, no relativity
L_einstein = gamma * v * tau       # with time dilation

survive_newton = np.exp(-height / L_newton)
survive_einstein = np.exp(-height / L_einstein)

print(f"gamma = {gamma:.1f}  (the muon's clock runs {gamma:.0f}x slower)")
print(f"Average travel distance: Newton {L_newton:,.0f} m   Einstein {L_einstein:,.0f} m")
print(f"Fraction surviving 15 km: Newton {survive_newton:.1e}   Einstein {survive_einstein:.2f}")

d = np.linspace(0, height, 300)
plt.plot(d / 1000, np.exp(-d / L_newton), color="#8AA2B7", label="Without relativity")
plt.plot(d / 1000, np.exp(-d / L_einstein), color="#00A9F4", lw=2.5, label="With special relativity")
plt.xlabel("Distance travelled (km)")
plt.ylabel("Fraction of muons still alive")
plt.legend()
plt.show()
"""),
("md", """
Without relativity, about 1 muon in 10 billion would survive. Your detector would see nothing. With relativity, around 40% survive, which is why you just counted about 1,000 of them in 10 minutes.

**Every muon in your dataset is evidence that moving clocks run slow.**

### What's next in the full class

- Analyse 100,000+ events from the real detector
- Reconstruct each muon's direction and measure the cos²θ angular distribution
- Find a hidden density change in the rock above an underground tunnel, using muon counts alone (muography)
- Present your own result, and leave with a certificate and a Python project for your portfolio
"""),
]
