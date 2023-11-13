## Software Developer: Matt Wright
## Research Associate I, Institute for Clean Energy Technology (ICET)
## Course: PH 6433 Computational Physics, Mississippi State University (MSU)
## Semester: Fall 2023
## Professor: Dr. R.T. Clay

## lasFE is developed to facilitate a statistical analysis of particle-size distribution (PSD) data collected with a TSI model 3340A Laser Aerosol Spectrometer (LAS) to determine the Filtration Efficiency (FE) of nuclear-grade High Efficieny Particlulate Air (HEPA) filters at a specified particle diameter for qualification or performance-evaluation purposes. Data collection is controlled by ICET test procedure for measuring FE. To estimate FE, lasFE shall perform a nonlinear fit on the upstream and downstream PSD and calculates the penetration (P) as a ratio of the aerosol concentration before and after filtration. FE is related to penetration through the relationship, FE = 1 - P.

## User interaction with lasFE is facilatated through YAML Ain't Markup Language (YAML) configuration files. These files contain necessary information to process the data such as aerosol-sample numbers and instrumental parameters.

## This version of lasFE has been developed for PH 6433 Computational Physics at MSU. This project is not subject to ASME-NQA-1 nor ICET-QA-036, Software Control, quality assurance requirements. For this reason, this software shall not be used for any purpose other than PH 6433.

import csv
import matplotlib.pyplot as plt

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
dataRows   =  transposeData[len(headers):]

# Particle-size bins (upper and lower bounds) replaced with bin midpoint and sigma
for row in dataRows:
    if len(row) >= 2 and all(isinstance(x, (float, int)) for x in row[:2]):
        binMidpoint = 0.5 * sum(row[:2])
        sigma       = 0.5 * (row[1] - row[0])

        row[0], row[1] = binMidpoint, sigma

# User input
upSampleStart = 2
upSampleEnd = 4
downSampleStart = 11
downSampleEnd = 13
particleSizeOfInterest = 300
windowSize = 200

upBound = particleSizeOfInterest + windowSize
lowBound = particleSizeOfInterest - windowSize

upSample   = range(upSampleStart, upSampleEnd)
downSample = range(downSampleStart, downSampleEnd)

plt.figure()
plt.title('Particle Size Distribution')

upstreamPSD = []
downstreamPSD = []

# Pull data corresponding to user-specified aerosol sample numbers from each particle size bin
for row in dataRows:
    if lowBound <= row[0] <= upBound:
        for i in upSample:
            upstreamPSD.append((row[0], row[i+1]))

        for i in downSample:
            downstreamPSD.append((row[0], row[i+1]))

# Plot the upstream and downstream PSDs directly from the lists of tuples
for point in upstreamPSD:
    plt.scatter(*point, color='red', label='Upstream PSD')

for point in downstreamPSD:
    plt.scatter(*point, color='blue', label='Downstream PSD')

# Remove duplicate labels in the legend
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys(), loc='upper right')
plt.xlabel('Particle Size (nm)')
plt.ylabel('Concentration $(particles/cm^3)$')

plt.show()