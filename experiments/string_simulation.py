import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.fft import rfft, rfftfreq


# phys. properties

points = 100
length = 1.0

tension = 400.0
linear_density = 0.01

# wave speed:
# c = sqrt(T / μ)
wave_speed = np.sqrt(tension / linear_density)


# spatial grid

x = np.linspace(0, length, points)

dx = x[1] - x[0]


# time settings
dt = 0.00001
steps = 20000


# init string shape

string = np.where(
    x <= 0.5,
    x / 0.5,
    (1 - x) / 0.5
)

# fixed endpoints
string[0] = 0
string[-1] = 0


# prev state

previous = string.copy()


# store sim data

frames = []
center_motion = []


# run sim

center_index = points // 2

for step in range(steps):

    current = string.copy()

    # approximate the second spatial derivative.
    # this represents the curvature of the string.
    curvature = (
        string[2:]
        - 2 * string[1:-1]
        + string[:-2]
    )

    # numerical form of the wave equation.
    string[1:-1] = (
        2 * string[1:-1]
        - previous[1:-1]
        + (wave_speed * dt / dx) ** 2 * curvature
    )

    previous = current

    # record the displacement at the center.
    center_motion.append(string[center_index])

    # save frames for animation.
    if step % 100 == 0:
        frames.append(string.copy())


# convert recorded motion into a NumPy array.
center_motion = np.array(center_motion)



# frequency analysis


# remove the average displacement.
# this prevents the constant/DC component from
# dominating the frequency analysis.

center_signal = center_motion - np.mean(center_motion)


# create the frequency axis.

frequencies = rfftfreq(
    len(center_signal),
    dt
)


# calculate the frequency spectrum.

spectrum = np.abs(
    rfft(center_signal)
)


# ignore the zero-frequency component.

spectrum[0] = 0


# find the strongest frequency.

dominant_index = np.argmax(spectrum)

measured_frequency = frequencies[dominant_index]


# theoretical / fundamental frequency

# fundamental frequency of a string fixed at both ends:
#
# f₁ = c / (2L)

theoretical_frequency = wave_speed / (2 * length)


# print the results :)

print()
print("Resonance - Frequency Analysis")
print("------------------------------")
print(f"Wave speed: {wave_speed:.2f} m/s")
print(
    f"Theoretical fundamental: "
    f"{theoretical_frequency:.2f} Hz"
)
print(
    f"Measured dominant frequency: "
    f"{measured_frequency:.2f} Hz"
)

difference = abs(
    measured_frequency - theoretical_frequency
)

print(
    f"Difference: "
    f"{difference:.2f} Hz"
)
print()


# animation !!

fig, ax = plt.subplots(figsize=(10, 5))

line, = ax.plot(
    x,
    frames[0]
)

ax.set_xlabel("Position along string")
ax.set_ylabel("Displacement")

ax.set_title(
    "Resonance — Vibrating String"
)

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
    blit=False
)


plt.show()

# plot center displacement

time = np.arange(len(center_motion)) * dt

plt.figure(figsize=(10, 5))

plt.plot(
    time,
    center_motion
)

plt.xlabel("Time (s)")
plt.ylabel("Center displacement")

plt.title(
    "Resonance — Center of String"
)

plt.grid(True, alpha=0.2)

plt.show()