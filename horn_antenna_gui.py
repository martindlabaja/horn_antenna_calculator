import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLineEdit, QPushButton, QLabel, QTextEdit, QSplitter)
from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np

from horn_calculator import solve_horn, HornLanguageHelper

class HornAntennaCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Horn Antenna Calculator')
        self.setGeometry(100, 100, 1400, 800)

        main_layout = QHBoxLayout(self)

        # Create a splitter for resizable columns
        splitter = QSplitter(Qt.Horizontal)

        # Left side - Inputs and Results
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Inputs
        input_layout = QVBoxLayout()
        self.freq_input = self.create_input("Frequency (MHz):", input_layout, "1420.4")
        self.impedance_input = self.create_input("Impedance (Ω):", input_layout, "50")
        self.gain_input = self.create_input("Gain (dBi):", input_layout, "20.2")
        input_layout.addWidget(QPushButton("Calculate", clicked=self.calculate))

        # Results
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)

        left_layout.addLayout(input_layout)
        left_layout.addWidget(QLabel("Results:"))
        left_layout.addWidget(self.results_text)

        # Right side - Matplotlib graph
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        right_layout.addWidget(self.toolbar)
        right_layout.addWidget(self.canvas)

        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

        # Set initial sizes (1:3 ratio)
        splitter.setSizes([400, 1000])

        main_layout.addWidget(splitter)

    def create_input(self, label, parent_layout, default_value):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        line_edit = QLineEdit(default_value)
        line_edit.setValidator(QDoubleValidator())
        layout.addWidget(line_edit)
        parent_layout.addLayout(layout)
        return line_edit

    def calculate(self):
        try:
            freq = float(self.freq_input.text())
            impedance = float(self.impedance_input.text())
            gain = float(self.gain_input.text())

            results = solve_horn(freq, impedance, gain)
            
            if 'error' in results:
                self.results_text.setText(results['error'])
                return

            self.display_results(results)
            self.plot_antenna(results)

        except ValueError:
            self.results_text.setText("Please enter valid numeric values for all fields.")


    def display_results(self, results):
        C = HornLanguageHelper()
        text = f"{C.CALC_HORN_TITLE}\n"
        text += "-" * 61 + "\n"
        text += f"{C.CALC_KHARCHENKO_FREQ} f: {results['frequency']} MHz\n"
        text += f"Wavelength λ: {results['wavelength']:.2f} mm\n"
        text += f"{C.CALC_HORN_GAIN}: {results['gain']} dBi\n"
        text += f"Antenna input impedance Zo: {results['impedance']} Ω\n"
        text += f"{C.CALC_HORN_DFH}: {results['DFH']}°\n"
        text += f"{C.CALC_HORN_DFV}: {results['DFV']}°\n"
        text += f"{C.CALC_HORN_FOV}: {results['FOV']}\n"
        text += "-" * 61 + "\n"
        text += f"{C.CALC_HORN_WG_DIMEN} a×b×c: {results['a']:.2f} × {results['b']:.2f} × {results['c']:.2f} mm\n"
        text += f"{C.CALC_HORN_WG_WIDEBAND} ΔF: {results['waveguide_wideband']} MHz\n"
        text += f"{C.CALC_HORN_WG_LAMBDA} λg: {results['waveguide_lambda']:.2f} mm\n"
        text += "-" * 61 + "\n"
        text += f"{C.CALC_HORN_DIMEN} Ар×Вр: {results['Ap']:.2f} × {results['Bp']:.2f} mm\n"
        text += f"{C.CALC_HORN_LENGTH_R} R: {results['R']:.2f} mm\n"
        text += f"{C.CALC_HORN_LENGTH_D1} D1: {results['D1']:.2f} mm\n"
        text += f"{C.CALC_HORN_LENGTH_D2} D2: {results['D2']:.2f} mm\n"
        text += "-" * 61 + "\n"
        text += f"{C.CALC_HORN_H} h: {results['h']:.2f} mm\n"
        text += f"{C.CALC_HORN_L1} l1: {results['l1']:.2f} mm\n"
        text += f"{C.CALC_HORN_L2} l2: {results['l2']:.2f} mm\n"

        self.results_text.setText(text)

    def plot_antenna(self, dim):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        offset = dim['Ap']*-1

        # TOP Waveguide
        quad = np.array([(0, dim['a']/-2), 
                        (dim['c'], dim['a']/-2), 
                        (dim['c'], dim['a']/2),
                        (0, dim['a']/2)
                        ])
        # TOP Horn
        quad2 = np.array([(dim['c'], dim['a']/-2), 
                        (dim['D1'], dim['Ap']/-2),
                        (dim['D1'], dim['Ap']/2),
                        (dim['c'], dim['a']/2)
                        ])
        # SIDE Waveguide
        quad3 = np.array([(0, (dim['b']/-2) + offset), 
                        (dim['c'], (dim['b']/-2) + offset), 
                        (dim['c'], (dim['b']/2) + offset),
                        (0, (dim['b']/2) + offset)
                        ])
        # SIDE Horn
        quad4 = np.array([(dim['c'], dim['b']/-2+ offset), 
                        (dim['D2'], dim['Bp']/-2+ offset),
                        (dim['D2'], dim['Bp']/2+ offset),
                        (dim['c'], dim['b']/2+ offset)
                        ])

        # Plot the quadrilaterals
        ax.plot(np.append(quad[:, 0], quad[0, 0]), np.append(quad[:, 1], quad[0, 1]), 'b-')
        ax.plot(np.append(quad2[:, 0], quad2[0, 0]), np.append(quad2[:, 1], quad2[0, 1]), 'b-')
        ax.plot(np.append(quad3[:, 0], quad3[0, 0]), np.append(quad3[:, 1], quad3[0, 1]), 'b-')
        ax.plot(np.append(quad4[:, 0], quad4[0, 0]), np.append(quad4[:, 1], quad4[0, 1]), 'b-')

        # Function to add labels
        def add_labels(q, ax):
            for i in range(4):
                start, end = q[i], q[(i+1)%4]
                midpoint = (start + end) / 2
                dx, dy = end - start
                angle = np.arctan2(dy, dx)
                length = np.linalg.norm(end - start)
                
                # Offset the label slightly
                offset = -30
                perpendicular = np.array([-dy, dx]) / np.linalg.norm([dx, dy])
                label_pos = midpoint + offset * perpendicular
                
                ax.annotate(f'{length:.2f}', xy=label_pos, xytext=(0, 0), textcoords='offset points',
                            ha='center', va='center', rotation=np.degrees(angle),
                            bbox=dict(boxstyle='round,pad=0.5', fc='white', ec='none', alpha=0.7))

        # Add labels to all quadrilaterals
        add_labels(quad, ax)
        add_labels(quad2, ax)
        add_labels(quad3, ax)
        add_labels(quad4, ax)

        # Add new lines and labels
        # Exciting pin
        pin_x = dim['c'] - dim['l2']
        pin_y = dim['b'] / -2 + offset
        ax.plot([pin_x, pin_x], [pin_y, pin_y + dim['h']], 'r-', linewidth=2)
        ax.annotate(f"h: {dim['h']:.2f}", xy=(pin_x, pin_y + dim['h']/2), xytext=(5, 0), 
                    textcoords='offset points', ha='left', va='center', color='red')

        # l1 and l2
        ax.plot([0, dim['c']], [pin_y, pin_y], 'g--', linewidth=1)
        ax.annotate(f"l1: {dim['l1']:.2f}", xy=(dim['l1']/2, pin_y), xytext=(0, 5), 
                    textcoords='offset points', ha='center', va='bottom', color='green')
        ax.annotate(f"l2: {dim['l2']:.2f}", xy=(dim['c'] - dim['l2']/2, pin_y), xytext=(0, 5), 
                    textcoords='offset points', ha='center', va='bottom', color='green')

        # R, D1, and D2
        ax.plot([dim['c'], dim['D1']], [0, 0], 'k--', linewidth=1)
        ax.annotate(f"D1: {dim['D1']:.2f}", xy=(dim['c'] + dim['D1']/2, 0), xytext=(0, -10), 
                    textcoords='offset points', ha='center', va='top', color='black')

        ax.plot([dim['c'], dim['D2']], [offset, offset], 'k--', linewidth=1)
        ax.annotate(f"D2: {dim['D2']:.2f}", xy=(dim['c'] + dim['D2']/2, offset), xytext=(0, -10), 
                    textcoords='offset points', ha='center', va='top', color='black')

        # Set equal aspect ratio and remove axes
        ax.set_aspect('equal', 'box')
        ax.axis('off')

        # Set title
        ax.set_title('Horn Antenna Dimensions, Top and Side View', fontsize=16)
        self.figure.tight_layout()
        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = HornAntennaCalculator()
    ex.show()
    sys.exit(app.exec())