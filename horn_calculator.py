import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
import math
import re

class HornLanguageHelper:
    def __init__(self, lang='en'):
        self.lang = lang
        if lang == 'en':
            self.CALC_HORN_TITLE = "Pyramidal Horn antenna"
            self.CALC_HORN_ALERT = "If the gain is less than 12 dBi, the calculation is incorrect"
            self.CALC_KHARCHENKO_FREQ = "Mean frequency of the range"
            self.CALC_HORN_GAIN = "Antenna Gain"
            self.CALC_HORN_DFH = "Major lobe HPBW in the horizontal plane H ΔΦ"
            self.CALC_HORN_DFV = "Major lobe HPBW in the vertical plane V ΔΦ"
            self.CALC_HORN_WG_DIMEN = "Waveguide dimensions"
            self.CALC_HORN_WG_WIDEBAND = "Waveguide bandwidth"
            self.CALC_HORN_WG_LAMBDA = "Wavelength in the waveguide"
            self.CALC_HORN_DIMEN = "Horn aperture dimensions"
            self.CALC_HORN_LENGTH_R = "Horn length"
            self.CALC_HORN_LENGTH_D1 = "Horn wide plane length"
            self.CALC_HORN_LENGTH_D2 = "Horn narrow plane length"
            self.CALC_HORN_H = "The exciting pin height"
            self.CALC_HORN_L1 = "Distance from the pin to the rear wall of the waveguide"
            self.CALC_HORN_L2 = "Distance from the pin to the horn throat"
            self.CALC_HORN_FOV = "Estimated Field of View"

def format_length(length, measure=0):
    if measure == 0:  # mm
        return f"{length:.1f} mm"
    elif measure == 1:  # cm
        return f"{length/10:.2f} cm"
    elif measure == 2:  # m
        return f"{length/1000:.3f} m"
    else:
        return f"{length:.1f} mm"


def solve_horn(freq, impedance, gain, measure=0):
    C = HornLanguageHelper()
    c = 299792.458  # Speed of light in km/s
    
    if freq <= 0 or impedance <= 0 or gain <= 0:
        print("Invalid input parameters")
        return {"error": "Invalid input parameters"}
    
    if gain < 12:
        print(C.CALC_HORN_ALERT)
        return {"error": C.CALC_HORN_ALERT}

    g = gain - 2
    i = 0.6
    r = 1.05
    wavelength = c / freq
    H = c / (0.6 * wavelength / 0.75)
    s = c / (0.9 * wavelength / 0.75)
    A = 0.75 * wavelength
    l = A / 2
    N = (10 ** (g / 9.5)) * wavelength ** 2 / (2 * math.pi)
    g = math.sqrt(N / 1.5)
    c = 1.5 * g
    O = g * (g - l) / (2 * wavelength)
    u = c * (c - A) / (3 * wavelength)
    R = max(O, u)
    m = (c - A) / 2
    E = math.sqrt(R ** 2 + m ** 2)
    D = (g - l) / 2
    M = math.sqrt(R ** 2 + D ** 2)
    d = wavelength / math.sqrt(1 - (wavelength / (2 * A)) ** 2)
    f = 2 * math.pi / wavelength
    v = 1 / f * math.acos(1 - math.sqrt(impedance * A * l * f / (120 * d))) * r
    G = 0.25 * d * i
    T = 4.6 / f * math.sqrt(wavelength / A * (wavelength / A) - 1)
    I = 67 * wavelength / c
    W = 51 * wavelength / g

    # Print results
    print(f"{C.CALC_HORN_TITLE}")
    print("-" * 61)
    print(f"{C.CALC_KHARCHENKO_FREQ} f: {freq} MHz")
    print(f"Wavelength λ: {format_length(wavelength, measure)}")
    print(f"{C.CALC_HORN_GAIN}: {gain} dBi")
    print(f"Antenna input impedance Zo: {impedance} Ω")
    print(f"{C.CALC_HORN_DFH}: {round(W)}°")
    print(f"{C.CALC_HORN_DFV}: {round(I)}°")
    print(f"{C.CALC_HORN_FOV}: {round(W)}° × {round(I)}°")
    print("-" * 61)
    print(f"{C.CALC_HORN_WG_DIMEN} a×b×c: {format_length(A, measure)} × {format_length(l, measure)} × {format_length(G + T, measure)}")
    print(f"{C.CALC_HORN_WG_WIDEBAND} ΔF: {round(s)}-{round(H)} MHz")
    print(f"{C.CALC_HORN_WG_LAMBDA} λg: {format_length(d, measure)}")
    print("-" * 61)
    print(f"{C.CALC_HORN_DIMEN} Ар×Вр: {format_length(c, measure)} × {format_length(g, measure)}")
    print(f"{C.CALC_HORN_LENGTH_R} R: {format_length(R, measure)}")
    print(f"{C.CALC_HORN_LENGTH_D1} D1: {format_length(M, measure)}")
    print(f"{C.CALC_HORN_LENGTH_D2} D2: {format_length(E, measure)}")
    print("-" * 61)
    print(f"{C.CALC_HORN_H} h: {format_length(v, measure)}")
    print(f"{C.CALC_HORN_L1} l1: {format_length(G, measure)}")
    print(f"{C.CALC_HORN_L2} l2: {format_length(T, measure)}")

    # Return dictionary of values
    return {
        "frequency": freq,
        "wavelength": wavelength,
        "gain": gain,
        "impedance": impedance,
        "DFH": round(W),
        "DFV": round(I),
        "FOV": f"{round(W)}° × {round(I)}°",
    
        "a": A,
        "b": l,
        "c": G + T,
    
        "waveguide_wideband": f"{round(s)}-{round(H)}",
        "waveguide_lambda": d,
        
        "Ap": c,
        "Bp": g,
       
        "R": R,
        "D1": M,
        "D2": E,
        
        "h": v,
        "l1": G,
        "l2": T
    }


dim = solve_horn(freq=1420.4, impedance=50, gain=20.2, measure=0)

