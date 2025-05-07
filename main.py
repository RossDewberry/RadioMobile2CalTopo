#!/usr/bin/env python3
"""
geotiff_warp_gui.py

A PyQt5 GUI tool to batch warp PNG + DAT files into Web-Mercator GeoTIFFs.
Features:
  • Drag-and-drop one INPUT folder **or** a .zip archive
  • Drag-and-drop an OUTPUT folder
  • Auto-extracts ZIP to temp, processes matching basename pairs, then cleans up
"""
import sys
import os
import tempfile
import zipfile
import numpy as np
from PIL import Image
import rasterio
from rasterio.transform import from_bounds
from rasterio.warp import calculate_default_transform, reproject, Resampling
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox
)

class DropLabel(QLabel):
    def __init__(self, title):
        super().__init__(title)
        self.setFrameStyle(QLabel.Box | QLabel.Plain)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setAcceptDrops(True)
        self.path = ''

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if not urls:
            return
        path = urls[0].toLocalFile()
        # accept either a dir or a .zip file
        if os.path.isdir(path) or (os.path.isfile(path) and path.lower().endswith('.zip')):
            self.path = path
            self.setText(path)
        else:
            QMessageBox.warning(self, "Invalid", f"{path} is not a folder or .zip archive.")
        event.acceptProposedAction()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GeoTIFF Warp GUI")
        self.resize(600, 300)

        # Single input drag-drop zone (folder or zip)
        self.input_label = DropLabel(
            "Drop INPUT folder here (or .zip with .dat + .png)")
        self.out_label = DropLabel("Drop OUTPUT folder here")

        # Buttons
        self.run_btn  = QPushButton("Run")
        self.exit_btn = QPushButton("Exit")
        self.run_btn.clicked.connect(self.process)
        self.exit_btn.clicked.connect(QApplication.quit)

        # Layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.input_label)
        vbox.addWidget(self.out_label)
        hbox = QHBoxLayout()
        hbox.addWidget(self.run_btn)
        hbox.addWidget(self.exit_btn)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def process(self):
        src_path = self.input_label.path
        out_dir  = self.out_label.path

        if not src_path or not out_dir:
            QMessageBox.warning(self, "Missing",
                                "Please drop both input (folder or zip) and output folder.")
            return

        # Determine actual input folder
        is_zip = os.path.isfile(src_path) and src_path.lower().endswith('.zip')
        if is_zip:
            tmpdir = tempfile.TemporaryDirectory()
            try:
                with zipfile.ZipFile(src_path, 'r') as zf:
                    zf.extractall(tmpdir.name)
                in_dir = tmpdir.name
            except Exception as e:
                QMessageBox.critical(self, "Zip Error",
                                     f"Failed to extract ZIP:\n{e}")
                tmpdir.cleanup()
                return
        else:
            in_dir = src_path

        # Find and process pairs
        dat_files = [f for f in os.listdir(in_dir) if f.lower().endswith('.dat')]
        if not dat_files:
            QMessageBox.information(self, "Nothing to do",
                                    "No .dat files found in the input.")
            if is_zip: tmpdir.cleanup()
            return

        count = 0
        for fname in dat_files:
            base     = os.path.splitext(fname)[0]
            dat_path = os.path.join(in_dir, fname)
            png_path = os.path.join(in_dir, base + '.png')
            if not os.path.exists(png_path):
                QMessageBox.warning(self, "Missing PNG",
                                    f"No matching PNG for {fname}")
                continue

            out_tif = os.path.join(out_dir, base + '.tif')
            try:
                warp(dat_path, png_path, out_tif)
                count += 1
            except Exception as e:
                QMessageBox.critical(self, "Error",
                                     f"Failed processing {base}:\n{e}")

        if is_zip:
            tmpdir.cleanup()

        QMessageBox.information(self, "Done",
                                f"Processed {count} file pair(s).")

def read_dat_coords(path):
    coords = []
    with open(path, 'r') as f:
        for line in f:
            if ',' not in line: continue
            parts = line.strip().split(',')
            try:
                lon, lat = float(parts[0]), float(parts[1])
            except ValueError:
                continue
            coords.append((lon, lat))
            if len(coords) == 4: break
    if len(coords) < 4:
        raise RuntimeError(f"Expected 4 coordinate lines in {path}, got {len(coords)}")
    return coords

def warp(dat_path, png_path, out_tif):
    UL, UR, LR, LL = read_dat_coords(dat_path)
    ul_lon, ul_lat = UL

    img   = Image.open(png_path).convert('RGBA')
    arr   = np.array(img)
    h, w  = arr.shape[:2]

    src_tfrm = from_bounds(UL[0], LL[1], UR[0], UL[1], w, h)
    src_crs  = 'EPSG:4326'

    dst_crs, (dst_tfrm, dst_w, dst_h) = (
        'EPSG:3857',
        calculate_default_transform(
            src_crs, 'EPSG:3857', w, h, UL[0], LL[1], UR[0], UL[1]
        )
    )

    profile = {
        'driver': 'GTiff',
        'dtype': arr.dtype,
        'count': 4,
        'width': dst_w,
        'height': dst_h,
        'crs': dst_crs,
        'transform': dst_tfrm,
        'compress': 'lzw',
        'tiled': True
    }

    with rasterio.open(out_tif, 'w', **profile) as dst:
        for b in range(4):
            reproject(
                source=arr[:,:,b],
                destination=rasterio.band(dst, b+1),
                src_transform=src_tfrm,
                src_crs=src_crs,
                dst_transform=dst_tfrm,
                dst_crs=dst_crs,
                resampling=Resampling.bilinear
            )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = MainWindow()
    wnd.show()
    sys.exit(app.exec_())
