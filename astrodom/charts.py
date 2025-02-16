from PyQt6.QtWidgets import QDialog, QVBoxLayout
from PyQt6.QtCore import Qt
import pandas as pd
from PyQt6.QtGui import QColor
import pyqtgraph as pg
from astrodom.settings import *

class Charts(QDialog):
    def __init__(self, df: pd.DataFrame, parent=None):
        super().__init__(parent)

        self.altLimit = float( parent.altEdit.text()) if parent else 0
        self.fwhmLimit = float( parent.fwhmEdit.text()) if parent else 0
        self.snrLimit = float( parent.snrEdit.text()) if parent else 0
        self.eccentricityLimit = float( parent.eccentricityEdit.text()) if parent else 0
        
        self.setWindowTitle("Charts")
        self.setGeometry(100, 100, 800,800)

        # Create a layout
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Create plots
        self.fwhm_plot = pg.PlotWidget(title="FWHM")
        self.eccentricity_plot = pg.PlotWidget(title="Eccentricity")
        self.snr_plot = pg.PlotWidget(title="SNR")
        self.alt_plot = pg.PlotWidget(title="ALT")
        
        # Set background color for the plots
        self.fwhm_plot.setBackground((20, 20, 20))
        self.eccentricity_plot.setBackground((20, 20, 20))
        self.snr_plot.setBackground((20, 20, 20))
        self.alt_plot.setBackground((20, 20, 20))
        
        # Enable antialiasing for all plots
        self.fwhm_plot.setAntialiasing(True)
        self.eccentricity_plot.setAntialiasing(True)
        self.snr_plot.setAntialiasing(True)
        self.alt_plot.setAntialiasing(True)
        
        # linked scrolling 
        self.link_views()

        # Allow zoom only on the x-axis for all plots
        self.fwhm_plot.setMouseEnabled(x=True, y=False)
        self.eccentricity_plot.setMouseEnabled(x=True, y=False)
        self.snr_plot.setMouseEnabled(x=True, y=False)
        self.alt_plot.setMouseEnabled(x=True, y=False)
        
        # Add axis labels
        self.fwhm_plot.setLabel('left', 'FWHM')
        self.fwhm_plot.setLabel('bottom', 'Date')
        self.eccentricity_plot.setLabel('left', 'Eccentricity')
        self.eccentricity_plot.setLabel('bottom', 'Date')
        self.snr_plot.setLabel('left', 'SNR')
        self.snr_plot.setLabel('bottom', 'Date')
        self.alt_plot.setLabel('left', 'ALT')
        self.alt_plot.setLabel('bottom', 'Date')
        
        # Add a horizontal line at FWHM_LIMIT_DEFAULT
        fwhm_limit_line = pg.InfiniteLine(
            pos=self.fwhmLimit, angle=0, pen=pg.mkPen(color='r', style=Qt.PenStyle.DashLine)
        )
        self.fwhm_plot.addItem(fwhm_limit_line)

        # Add a horizontal line at eccentricity limit
        eccentricity_limit_line = pg.InfiniteLine(
            pos=self.eccentricityLimit, angle=0, pen=pg.mkPen(color='r', style=Qt.PenStyle.DashLine)
        )
        self.eccentricity_plot.addItem(eccentricity_limit_line)

        # Add a horizontal line at snr limit
        snr_limit_line = pg.InfiniteLine(
            pos=self.snrLimit , angle=0, pen=pg.mkPen(color='r', style=Qt.PenStyle.DashLine)
        )
        self.snr_plot.addItem(snr_limit_line)

        # Add a horizontal line at alt limit
        alt_limit_line = pg.InfiniteLine(
            pos=self.altLimit , angle=0, pen=pg.mkPen(color='r', style=Qt.PenStyle.DashLine)
        )
        self.alt_plot.addItem(alt_limit_line)
        
        # Add plots to the layout
        layout.addWidget(self.fwhm_plot)
        layout.addWidget(self.eccentricity_plot)
        layout.addWidget(self.snr_plot)
        layout.addWidget(self.alt_plot)

        # Plot the data
        self.plot_data(df)

    def plot_data(self, df: pd.DataFrame):
        # Convert DATE_OBS to numerical format for plotting
        df['DATE_OBS'] = pd.to_datetime(df['DATE_OBS'], format='%Y-%m-%dT%H:%M:%S', errors='coerce')
        df = df.dropna(subset=['DATE_OBS'])
        df['DATE_OBS_NUM'] = df['DATE_OBS'].astype('int64') / 10**9  # Convert to seconds since epoch


        # Sort by DATE_OBS
        df = df.sort_values(by='DATE_OBS_NUM')
        # Set up the x-axis to show time in %Y-%m-%dT%H:%M:%S format
        date_axis_fwhm = pg.graphicsItems.DateAxisItem.DateAxisItem(orientation='bottom')
        date_axis_eccentricity = pg.graphicsItems.DateAxisItem.DateAxisItem(orientation='bottom')
        date_axis_snr = pg.graphicsItems.DateAxisItem.DateAxisItem(orientation='bottom')
        date_axis_alt = pg.graphicsItems.DateAxisItem.DateAxisItem(orientation='bottom')

        self.fwhm_plot.setAxisItems({'bottom': date_axis_fwhm})
        self.eccentricity_plot.setAxisItems({'bottom': date_axis_eccentricity})
        self.snr_plot.setAxisItems({'bottom': date_axis_snr})
        self.alt_plot.setAxisItems({'bottom': date_axis_alt})

        df = df.sort_values(by='DATE_OBS_NUM')
 
        # Convert filter colors to QColor using RGB values
        filter_colors = {
            'R': (255, 0, 0),  # Red
            'G': (0, 140, 55),  # Green
            'B': (55, 55, 255),  # Blue
            'Ha': (55, 55, 255),  # Ha
            'Oiii': (150, 220, 220),  # Oiii
            'Sii': (55, 55, 255),  # Sii
            'L': (255, 120, 190),  # Luminance (white)
            # Add more filters and their corresponding RGB values if needed
        }

        # Customize the appearance of the plots
        symbol_pen = pg.mkPen(color=(155, 155, 155), width=1)  # White outline for symbols

        for index, row in df.iterrows():
            filter_name = row['FILTER']
            if filter_name in filter_colors:
                color = filter_colors[filter_name]
                brush = pg.mkBrush(QColor(*color))

                # Plot FWHM vs DATE_OBS_NUM
                self.fwhm_plot.plot(
                    [row['DATE_OBS_NUM']], [row['FWHM']],
                    pen=None, symbol='o', symbolBrush=brush, symbolPen=symbol_pen
                )

                # Plot Eccentricity vs DATE_OBS_NUM
                self.eccentricity_plot.plot(
                    [row['DATE_OBS_NUM']], [row['ECCENTRICITY']],
                    pen=None, symbol='o', symbolBrush=brush, symbolPen=symbol_pen
                )


                # Plot SNR vs DATE_OBS_NUM
                self.snr_plot.plot(
                    [row['DATE_OBS_NUM']], [float(row['OBJECT_ALT'])],
                    pen=None, symbol='o', symbolBrush=brush, symbolPen=symbol_pen
                )

                # Convert OBJECT_ALT to numeric
                try:
                    object_alt = float(row['OBJECT_ALT'])
                except ValueError:
                    continue  # Skip this row if OBJECT_ALT is not a valid number

                # Plot ALT vs DATE_OBS_NUM
                self.alt_plot.plot(
                    [row['DATE_OBS_NUM']], [object_alt],
                    pen=None, symbol='o', symbolBrush=brush, symbolPen=symbol_pen
                )

    # Sync the zoom and panning on all four plots
    def link_views(self):
        self.fwhm_plot.setXLink(self.eccentricity_plot)
        self.eccentricity_plot.setXLink(self.snr_plot)
        self.snr_plot.setXLink(self.alt_plot)