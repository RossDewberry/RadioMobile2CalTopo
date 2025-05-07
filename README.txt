RadioMobile2CalTopo
====================

A Windows desktop tool to convert RadioMobile-style PNG + DAT files into properly georeferenced GeoTIFFs using the Web Mercator projection (EPSG:3857).

How to Use:
-----------

1. Launch the application by double-clicking `RadioMobile2CalTopo.exe`.

2. In the app window:
   - Drag and drop your input folder (or a `.zip` archive containing `.png` and `.dat` files) into the first box.
   - Drag and drop your output folder into the second box.

3. Click the "Run" button to start processing.

4. The tool will:
   - Read coordinate data from the `.dat` file
   - Warp the corresponding `.png` file into a georeferenced `.tif`
   - Save the output GeoTIFFs to your selected output folder

File Requirements:
------------------

- Each `.dat` file must contain exactly 4 coordinate lines (upper-left, upper-right, lower-right, lower-left).
- Each `.dat` must have a matching `.png` file with the same base filename.
- All files must be in the same folder or zipped together.

Notes:
------

- The tool supports drag-and-drop for ease of use.
- Internet connection is not required.

Troubleshooting:
----------------

If the app does not launch or you encounter an error:
- Make sure your input files are correctly formatted.
- Ensure you are running this on Windows 10 or later.

Contact:
--------

Created by: Ross Dewberry  
Email: [ross.dewberry@hotmail.com]  
Version: 1.0.0  
Date: May 2025

Source Data:
------------

This tool is compatible with PNG and DAT outputs from the Radio Mobile project by VE2DBE:
https://www.ve2dbe.com/english1.html

License:
--------

This software is licensed under the MIT License. See LICENSE.txt for full terms.

Credits and acknowledgments are listed in CREDITS.txt.



