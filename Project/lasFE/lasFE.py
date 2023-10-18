## Software Developer: Matt Wright
## Research Associate I, Institute for Clean Energy Technology (ICET)
## Course: PH 6433 Computational Physics, Mississippi State University (MSU)
## Semester: Fall 2023
## Professor: Dr. R.T. Clay

## lasFE is developed to facilitate a statistical analysis of particle-size distribution (PSD) data collected with a TSI model 3340A Laser Aerosol Spectrometer (LAS) to determine the Filtration Efficiency (FE) of nuclear-grade High Efficieny Particlulate Air (HEPA) filters at a specified particle diameter for qualification or performance-evaluation purposes. Data collection is controlled by ICET test procedure for measuring FE. To estimate FE, lasFE shall perform a nonlinear fit on the upstream and downstream PSD and calculates the penetration (P) as a ratio of the aerosol concentration before and after filtration. FE is related to penetration through the relationship, FE = 1 - P.

## User interaction with lasFE is facilatated through YAML Ain't Markup Language (YAML) configuration files. These files contain necessary information to process the data such as aerosol-sample numbers and instrumental parameters.

## This version of lasFE has been developed for PH 6433 Computational Physics at MSU. This project is not subject to ASME-NQA-1 nor ICET-QA-036, Software Control, quality assurance requirements. For this reason, this software shall not be used for any purpose other than PH 6433.

import csv

# Read LAS data file
filePath = './data/Dil_Char_6-10-21_LAS_100-1'
with open(filePath, newline='') as file:
    reader = csv.reader(file, delimiter='\t')
    data = [[float(item) if item.replace('.', '', 1).isdigit() else item for item in row] for row in reader]

# Transpose data to group by rows in LAS data file
transposeData = list(zip(*data))
transposeData = [list(row) for row in transposeData]

# Map rowCount to header string
headers = {
    0: "Date",
    1: "Time",
    2: "Accum.",
    3: "Scatter",
    4: "Current",
    5: "Sample",
    6: "Ref.",
    7: "Temp.",
    8: "Sheath",
    9: "Diff",
    10: "Box",
    11: "Purge",
    12: "Pres.",
    13: "Aux.",
    14: "Flow"
}

# Split matrix into seperate matrices for header information and PSD data
headerRows = [transposeData[rowCount] for rowCount in headers]
dataRows = transposeData[len(headers):]

# Find midpoint of particle-size bin
midpointDataRows = [(sum(row[:2])/2, *row[2:]) for row in dataRows]