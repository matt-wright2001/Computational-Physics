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
import yaml
import numpy as np
from scipy.stats import lognorm

def main():
    # Read YAML configuration file
    with open('config.yml', 'r') as config_file:
        config = yaml.safe_load(config_file)

    # Read LAS data file
    with open(config['dataFilePath'], newline='') as data_file:
        reader = csv.reader(data_file, delimiter='\t')
        data = [[float(item) if item.replace('.', '', 1).isdigit() else item for item in row] for row in reader]

    # Transpose data to group by rows in LAS data file
    transposeData = list(zip(*data))
    transposeData = [list(row) for row in transposeData]

    # Map row to header string
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
    headerRows = [transposeData[row] for row in headers]
    dataRows   =  transposeData[len(headers):]

    # Particle-size bins (upper and lower bounds) replaced with bin midpoint and sigma
    for row in dataRows:
        if len(row) >= 2 and all(isinstance(x, (float, int)) for x in row[:2]):
            binMidpoint = 0.5 * sum(row[:2])
            sigma       = 0.5 * (row[1] - row[0])

            row[0], row[1] = binMidpoint, sigma

    upBound  = config['particleSizeOfInterest'] + config['windowSize']
    lowBound = config['particleSizeOfInterest'] - config['windowSize']

    upSample   = range(config['upSampleStart'],   config['upSampleEnd'])
    downSample = range(config['downSampleStart'], config['downSampleEnd'])

    upstreamPSD   = []
    downstreamPSD = []

    # Pull data corresponding to user-specified aerosol sample numbers from each particle size bin
    # Data stored as tuples: (particle size, concentration, uncertainty in size)
    for row in dataRows:
        if lowBound <= row[0] <= upBound:
            for i in upSample:
                upstreamPSD.append((row[0], row[i+1], row[1])) 

            for i in downSample:
                downstreamPSD.append((row[0], row[i+1], row[1]))
    
    # Fit the upstream and downstream PSDs to a lognormal distribution
    upstream_sizes   = [point[0] for point in upstreamPSD]
    downstream_sizes = [point[0] for point in downstreamPSD]

    upstream_concentrations   = [point[1] for point in upstreamPSD]
    downstream_concentrations = [point[1] for point in downstreamPSD]

    # Renormalize the concentrations
    upstream_concentrations   = [point[1] / sum(upstream_concentrations)   for point in upstreamPSD]
    downstream_concentrations = [point[1] / sum(downstream_concentrations) for point in downstreamPSD]

    upstream_shape, upstream_loc, upstream_scale = lognorm.fit(upstream_sizes)
    downstream_shape, downstream_loc, downstream_scale = lognorm.fit(downstream_sizes)

    # Plot the fitted distributions
    plt.figure()
    x = np.linspace(min(upstream_sizes + downstream_sizes), max(upstream_sizes + downstream_sizes), 1000)
    plt.plot(x, lognorm.pdf(x, upstream_shape,   loc=upstream_loc,   scale=upstream_scale),   color='red',  linestyle='dashed', label='Fitted Upstream PSD')
    plt.plot(x, lognorm.pdf(x, downstream_shape, loc=downstream_loc, scale=downstream_scale), color='blue', linestyle='dashed', label='Fitted Downstream PSD')

    # Plot upstream and downstream PSD
    for point, concentration in zip(upstreamPSD, upstream_concentrations):
        plt.errorbar(point[0], concentration, xerr=point[2], color='red', fmt='o', label='Upstream PSD')

    for point,concentration in zip(downstreamPSD, downstream_concentrations):
        plt.errorbar(point[0], concentration, xerr=point[2], color='blue', fmt='o', label='Downstream PSD')
        

    # Format plot
    plt.title('Particle Size Distribution')
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='upper left')
    plt.xlabel('Particle Size (nm)')
    plt.ylabel('Concentration $(particles/cm^3)$')
    plt.xscale('log')
    plt.show()

if __name__ == "__main__":
    main()
