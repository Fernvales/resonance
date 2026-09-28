import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# -----------------------------
# Physical properties
# -----------------------------

points = 100
length = 1.0

tension = 400.0
linear_density = 0.01

# Wave speed:
# c = sqrt(T / μ)
wave_speed = np.sqrt(tension / linear_density)

# -----------------------------
# Spatial grid
# -----------------------------

x = np.linspace(0, length, points)

dx = x[1] - x[0]

# -----------------------------
# Time settings
# -----------------------------

dt = 0.00001
steps = 2000

# -----------------------------
# Initial string shape
# -----------------------------

string = np.where(
    x <= 0.5,
    x / 0.5,
    (1 - x) / 0.5
)

# Fixed endpoints
string[0] = 0
string[-1] = 0

# -----------------------------
# Previous state
# -----------------------------

previous = string.copy()

frames = []

# -----------------------------
# Simulation
# -----------------------------

for step in range(steps):

    current = string.copy()

    curvature = (
        string[2:]
        - 2 * string[1:-1]
        + string[:-2]
    )

    string[1:-1] = (
        2 * string[1:-1]
        - previous[1:-1]
        + (wave_speed * dt / dx) ** 2 * curvature
    )

    previous = current

    if step % 20 == 0:
        frames.append(string.copy())

# -----------------------------
# Plot
# -----------------------------

fig, ax = plt.subplots(figsize=(10, 5))

line, = ax.plot(x, frames[0])

ax.set_xlabel("Position along string")
ax.set_ylabel("Displacement")
ax.set_title("Resonance — Vibrating String")

ax.set_xlim(0, length)
ax.set_ylim(-1.2, 1.2)

ax.grid(True, alpha=0.2)


def update(frame):
    line.set_ydata(frame)
    return line,


animation = FuncAnimation(
    fig,
    update,
    frames=frames,
    interval=20,
    blit=True
)

plt.show()