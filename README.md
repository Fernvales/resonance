#### Resonance


> Resonance is an experimental project exploring the intersection of music, physics, mathematics, and computer science.

> The goal is to model how a physical vibration becomes the sound we hear, starting with a simple vibrating string.


#### Exploring
> Vibrating strings
> <br>Wave equations
> <br>Harmonics & resonance
> <br>Numerical simulation
> <br>Fourier analysis
> <br>Waveforms & frequency spectra
> <br>Computational sound
#### The Physics

For an ideal string, the frequency of its nth harmonic is

$$ f_n = \frac{n}{2L}\sqrt{\frac{T}{\mu}} $$

where:

L = string length <br>
T = tension <br>
μ = linear density <br>
n = harmonic number <br>

The project turns these relationships into actual simulations rather than treating them as equations on a page.

#### Current Progress
> Represent a string mathematically
> <br>Create a plucked-string model
> <br>Simulate vibration
> <br>Animate string motion
> <br>Measure oscillation frequency
> <br>Analyze harmonics
> <br>Perform Fourier analysis
> <br>Generate sound
> <br>Build interactive visualization
#### Current Model

The current simulation uses a finite-difference approximation of the one-dimensional wave equation:

$$ \frac{\partial^2u}{\partial t^2} = c^2 \frac{\partial^2u}{\partial x^2} $$

The string is represented as a discrete set of points and evolved through time numerically.

The wave speed is determined by:

$$ c = \sqrt{\frac{T}{\mu}} $$

This allows physical parameters such as tension and linear density to directly affect the behavior of the simulated string.

#### Built With

`Python` · `NumPy` · `Matplotlib`

#### Planned:

`SciPy` · `TypeScript` · `React` · `Web Audio API`

