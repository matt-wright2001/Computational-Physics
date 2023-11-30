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
from scipy.integrate import trapz
from scipy.optimize import curve_fit

def lognormDistribution(dp, CMD, GSD):
    '''
    dp: particle diameter
    CMD: count median diameter
    GSD: geometric standard deviation
    '''

    dp = np.maximum(dp, np.finfo(float).tiny)
    CMD = max(CMD, np.finfo(float).tiny)
    GSD = max(GSD, np.finfo(float).tiny)
    
    # Particle-Size Frequency Function (Hinds, Equation 4.41)
    return (1 / (np.sqrt(2 * np.pi) * dp * np.log(GSD))) * np.exp(- (np.log(dp) - np.log(CMD))**2 / (2 * np.log(GSD)**2))

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
        2: "Accumulated seconds",
        3: "Scatter",
        4: "Current",
        5: "Sample flow",
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

    # Only consider data within the user-specified samples and particle-size range
    upBound  = config['particleSizeOfInterest'] + config['windowSize']
    lowBound = config['particleSizeOfInterest'] - config['windowSize']

    upSample   = range(config['upSampleStart'],   config['upSampleEnd'])
    downSample = range(config['downSampleStart'], config['downSampleEnd'])

    # Pull data corresponding to user-specified aerosol sample numbers from each particle size bin
    # Data stored as tuples: (particle size, concentration, uncertainty in size)
    upstreamPSD   = []
    downstreamPSD = []

    for row in dataRows:
        if lowBound <= row[0] <= upBound:
            for i in upSample:
                upstreamPSD.append((row[0], row[i+1], row[1])) 

            for i in downSample:
                downstreamPSD.append((row[0], row[i+1], row[1]))

    # Pull sample accumulated seconds and flow rate from header information
    upstreamTime = 0
    upstreamSampleFlow = []
    for i in upSample:
        upstreamTime += headerRows[2][i]
        upstreamSampleFlow.append(headerRows[5][i])
    upstreamTime = upstreamTime / 60 ## Convert seconds to minutes
    upstreamSampleFlow = np.average(upstreamSampleFlow)
    upstreamSample = upstreamTime * upstreamSampleFlow

    downstreamTime = 0
    downstreamSampleFlow = []
    for i in downSample:
        downstreamTime += headerRows[2][i]
        downstreamSampleFlow.append(headerRows[5][i])
    downstreamTime = downstreamTime / 60 ## Convert seconds to minutes
    downstreamSampleFlow = np.average(downstreamSampleFlow)
    downstreamSample = downstreamTime * downstreamSampleFlow

    upstream_sizes            = [point[0] for point in upstreamPSD]
    downstream_sizes          = [point[0] for point in downstreamPSD]
    upstream_concentrations   = [point[1] for point in upstreamPSD]
    downstream_concentrations = [point[1] for point in downstreamPSD]

    upstream   = [(config["upstreamDilution"] * concentration) / upstreamSample for concentration in upstream_concentrations]
    downstream = [(config["downstreamDilution"] * concentration) / downstreamSample for concentration in downstream_concentrations]

    FE = [1 - (downstream[i] / upstream[i]) for i in range(len(upstream))]
    for i in range(len(FE)):
        if FE[i] == min(FE): mpps = upstream_sizes[i]
    
    # Fit the upstream and downstream PSDs to a lognormal distribution
    ## Initial Guesses of Fit Parameters
    upstreamGeoMean   = np.exp(np.mean(np.log(upstream_sizes)))
    upstreamGSD       = np.exp(np.std(np.log(upstream_sizes)))
    downstreamGeoMean = np.exp(np.mean(np.log(downstream_sizes)))
    downstreamGSD     = np.exp(np.std(np.log(downstream_sizes)))

    print(f'Upstream Geometric Mean:   {upstreamGeoMean} \t Upstream GSD:   {upstreamGSD}')
    print(f'Downstream Geometric Mean: {downstreamGeoMean} \t Downstream GSD: {downstreamGSD}')

    upstreamGuess   = [upstreamGeoMean, upstreamGSD]
    downstreamGuess = [downstreamGeoMean, downstreamGSD]
    
    # Iterative fit
    popt_upstream, _ = curve_fit(lognormDistribution, upstream_sizes, upstream_concentrations, p0=upstreamGuess)
    fitted_upstream = lognormDistribution(upstream_sizes, *popt_upstream)
    fitted_upstream = lognormDistribution(upstream_sizes, 280, 1.5906)

    popt_downstream, _ = curve_fit(lognormDistribution, downstream_sizes, downstream_concentrations, p0=downstreamGuess)
    fitted_downstream = lognormDistribution(downstream_sizes, *popt_downstream) 
    fitted_downstream = lognormDistribution(downstream_sizes, 280, 1.5906)

    upstreamDistribution   = [lognormDistribution(dp, upstreamGeoMean, upstreamGSD) for dp in upstream_sizes]
    downstreamDistribution = [lognormDistribution(dp, downstreamGeoMean, downstreamGSD) for dp in downstream_sizes]

    upstreamScale   = trapz(upstream_concentrations,   upstream_sizes)   / trapz(upstreamDistribution,   upstream_sizes)
    downstreamScale = trapz(downstream_concentrations, downstream_sizes) / trapz(downstreamDistribution, downstream_sizes)

    fitted_upstream   *= upstreamScale
    fitted_downstream *= downstreamScale

    plt.figure("LAS Particle Size Distribution")
    plt.plot(upstream_sizes, fitted_upstream, color='red', linestyle='dashed', label='Fitted Upstream PSD')
    plt.plot(downstream_sizes, fitted_downstream, color='blue', linestyle='dashed', label='Fitted Downstream PSD')

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
