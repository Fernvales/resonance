import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.fft import rfft, rfftfreq
from scipy.io import wavfile
from pathlib import Path
 
 

# simulation

 
def simulate(
    tension=400.0,        # N
    linear_density=0.01,  # kg/m
    length=1.0,           # m
    points=101,           # odd, so the exact midpoint is a grid point
    pluck_pos=0.3,        # where the string is pulled (fraction of length)
    pickup_pos=0.15,      # where we "listen" (fraction of length)
    duration=1.0,         # seconds of simulated time
    courant=0.9,          # c*dt/dx, must be <= 1 for stability
    damping=3.0,          # gamma, 1/s (0 = ideal string that rings forever)
    frame_every=200,      # save one animation frame every N steps
):
    wave_speed = np.sqrt(tension / linear_density)
 
    x = np.linspace(0, length, points)
    dx = x[1] - x[0]
 
    # pick dt from the Courant number so the scheme is always stable
    assert 0 < courant <= 1, f"Unstable: c*dt/dx = {courant:.2f} (must be <= 1)"
    dt = courant * dx / wave_speed
    steps = int(duration / dt)
 
    # triangular pluck, peak at pluck_pos, fixed endpoints
    string = np.where(
        x <= pluck_pos * length,
        x / (pluck_pos * length),
        (length - x) / (length - pluck_pos * length),
    )
    string[0] = string[-1] = 0
 
    r2 = courant ** 2
    b = damping * dt  # damping term per step
 
    def curvature(u):
        return u[2:] - 2 * u[1:-1] + u[:-2]
 
    # first step assumes the string starts at rest (zero velocity):
    # u(dt) = u(0) + 0.5 * r^2 * curvature
    previous = string.copy()
    string = string.copy()
    string[1:-1] = previous[1:-1] + 0.5 * r2 * curvature(previous)
 
    pickup_index = int(round(pickup_pos * (points - 1)))
    signal = np.zeros(steps)
    frames = []
 
    for step in range(steps):
        current = string.copy()
        string[1:-1] = (
            2 * string[1:-1]
            - (1 - b) * previous[1:-1]
            + r2 * curvature(string)
        ) / (1 + b)
        previous = current
 
        signal[step] = string[pickup_index]
        if step % frame_every == 0:
            frames.append(string.copy())
 
    return dict(
        x=x, frames=frames, signal=signal, dt=dt,
        wave_speed=wave_speed, length=length, courant=courant,
    )
 
 

# Fourier analysis

 
def analyze(signal, dt, fundamental, n_harmonics=8, pad_factor=8):
    """Return the spectrum and the measured frequency of each harmonic."""
    signal = signal - np.mean(signal)          # remove DC
    signal = signal * np.hanning(len(signal))  # window: less spectral leakage
 
    n_fft = len(signal) * pad_factor           # zero-pad: finer frequency grid
    freqs = rfftfreq(n_fft, dt)
    spectrum = np.abs(rfft(signal, n=n_fft))
 
    df = freqs[1] - freqs[0]
    results = []
    for n in range(1, n_harmonics + 1):
        target = n * fundamental
        # look for a peak within +-25% of the fundamental around the target
        lo = np.searchsorted(freqs, target - 0.25 * fundamental)
        hi = np.searchsorted(freqs, target + 0.25 * fundamental)
        k = lo + np.argmax(spectrum[lo:hi])
 
        # parabolic interpolation between neighbouring bins
        a, m, c = spectrum[k - 1], spectrum[k], spectrum[k + 1]
        shift = 0.5 * (a - c) / (a - 2 * m + c) if (a - 2 * m + c) != 0 else 0
        measured = freqs[k] + shift * df
 
        results.append((n, target, measured, spectrum[k]))
 
    return freqs, spectrum, results
 
 

# sound

 
def save_wav(signal, dt, filename=None, sample_rate=44100):
        if filename is None:
        filename = Path(__file__).parent / "resonance.wav"
    """Resample the simulated signal to audio rate and write a 16-bit WAV."""
    t_sim = np.arange(len(signal)) * dt
    t_audio = np.arange(0, t_sim[-1], 1 / sample_rate)
    audio = np.interp(t_audio, t_sim, signal)
 
    audio = audio - np.mean(audio)
    audio = audio / np.max(np.abs(audio))          # normalize to [-1, 1]
    fade = int(0.005 * sample_rate)                # 5 ms fade-out, avoids a click
    audio[-fade:] *= np.linspace(1, 0, fade)
 
    wavfile.write(filename, sample_rate, (audio * 32767 * 0.9).astype(np.int16))
    return filename
 
 

# plots
 
def plot_results(sim, freqs, spectrum, results):
    dt, signal = sim["dt"], sim["signal"]
    time = np.arange(len(signal)) * dt
    fundamental = results[0][1]
 
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7))
 
    ax1.plot(time, signal, linewidth=0.8)
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Displacement at pickup")
    ax1.set_title("Resonance - Pickup Signal")
    ax1.grid(True, alpha=0.2)
 
    ax2.plot(freqs, spectrum, linewidth=0.8)
    for n, theory, measured, _ in results:
        ax2.axvline(theory, color="tab:red", alpha=0.35, linestyle="--")
    ax2.set_xlim(0, (len(results) + 1) * fundamental)
    ax2.set_xlabel("Frequency (Hz)")
    ax2.set_ylabel("Magnitude")
    ax2.set_title("Spectrum (dashed = theoretical harmonics n * f1)")
    ax2.grid(True, alpha=0.2)
 
    fig.tight_layout()
 
 
def animate(sim):
    x, frames, length = sim["x"], sim["frames"], sim["length"]
 
    fig, ax = plt.subplots(figsize=(10, 5))
    line, = ax.plot(x, frames[0])
    ax.set_xlabel("Position along string")
    ax.set_ylabel("Displacement")
    ax.set_title("Resonance - Vibrating String")
    ax.set_xlim(0, length)
    ax.set_ylim(-1.2, 1.2)
    ax.grid(True, alpha=0.2)
 
    def update(frame):
        line.set_ydata(frame)
        return line,
 
    # keep a reference so the animation isn't garbage collected
    fig._anim = FuncAnimation(fig, update, frames=frames, interval=20, blit=False)
 
 

# main

 
if __name__ == "__main__":
    sim = simulate()
 
    theoretical_f1 = sim["wave_speed"] / (2 * sim["length"])
    freqs, spectrum, results = analyze(sim["signal"], sim["dt"], theoretical_f1)
 
    print()
    print("Resonance - Harmonic Analysis")
    print("-----------------------------")
    print(f"Wave speed: {sim['wave_speed']:.2f} m/s   Courant: {sim['courant']:.2f}")
    print(f"{'n':>3} {'theory (Hz)':>12} {'measured (Hz)':>14} {'error (Hz)':>11}")
    for n, theory, measured, _ in results:
        print(f"{n:>3} {theory:>12.2f} {measured:>14.2f} {measured - theory:>11.3f}")
 
    wav_name = save_wav(sim["signal"], sim["dt"])
    print(f"\nSaved audio: {wav_name}\n")
 
    animate(sim)
    plot_results(sim, freqs, spectrum, results)
    plt.show()