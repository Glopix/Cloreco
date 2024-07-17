"""
functions in this file can:
 extract statistic data from multiple report files from BigCloneEval
 create plots based on these statistic data
"""

from pathlib import Path
import project.settings as settings
import pandas as pd
from plotnine import *
import re

def create_recall_plot(csvFile: Path, dst: Path, clusterBy: str ='Type') -> None:
    """
    Create a plot (bar chart) based on the tool statistics from a CSV file
    and save it to the specified destination filepath

    Cluster by (Clone) 'Type' or (Tool) 'Name'
    """
    if clusterBy == 'Type':
        legendID = "Name"
    else:
        clusterBy = "Name"
        legendID = "Type"

    # Read the CSV file into a DataFrame
    data = pd.read_csv(csvFile)

    # Round the 'recall' values to 4 decimal places
    data['recall'] = data['recall'].round(4)

    # Sort the order of clone types in the plot legend
    # remove duplicates
    legendOrder = dict.fromkeys(data[legendID])
    
    if clusterBy == 'Type':
        legendOrder = sorted(legendOrder)
    else:
        # Sort the list of clone types based on the last digit in the string
        legendOrder = sorted(legendOrder, key=lambda x: int(x.rsplit('-',1)[1][0]))

    # Create the bar chart
    plot = (
        ggplot(data, aes(x=clusterBy, y='recall', fill=legendID)) +
        geom_bar(stat='identity', position='dodge') +
        geom_text(aes(label='recall', group=legendID), position=position_dodge(width=0.9), size=8, va='bottom') +  # Add recall values on top of bars
        labs(title='Recall comparison by clone type for different clone detector tools', x=clusterBy, y='Recall') +
        scale_fill_discrete(limits=legendOrder) +
        theme(axis_text_x=element_text())
    )

    # Save the plot
    #ggsave(plot, filename=dst, width=12, height=6)
    ggsave(plot, filename=dst, width=15, height=6, verbose = False)

def create_runtime_plot(csvFile: Path, dst: Path) -> None:
    # Read the CSV file into a DataFrame
    data = pd.read_csv(csvFile)

    # Drop duplicate rows based on the 'Name' and 'Runtime' columns
    # -> only one row wiht runtime per detector tool remains
    data = data.drop_duplicates(subset=['Name', 'Runtime'])

    # Create the bar chart
    plot = (
        ggplot(data, aes(x='Name', y='Runtime', fill='Name')) +
        geom_bar(stat='identity', position='dodge') +
        geom_text(aes(label='Runtime'), position=position_dodge(width=0.9), size=8, va='bottom') +  # Add runtime values on top of bars
        labs(title='Runtime comparison for different clone detector tools', x='Tool', y='Runtime (s)') +
        theme(axis_text_x=element_text(), legend_position='none')
    )

    # Save the plot
    #ggsave(plot, filename=dst, width=12, height=6, verbose = False)
    ggsave(plot, filename=dst, verbose = False)


def extract_run_time(logFile: Path) -> float:
    """
    reads the log file of the run and extracts the run time of the "detectClones" command
    """
    # Regular expression pattern to match the message and extract run time
    pattern = r"Runtime \(s\) of .*detectClones.*: (\d+\.\d+|\d+)"
    
    # Open the log file and scan each line
    with open(logFile, 'r') as file:
        for line in file:
            match = re.search(pattern, line)
            if match:
                runtime = float(match.group(1))

    return runtime


def extract_per_clone_type_statistic(lines: list[str]) -> list[dict]:
    """
    extract the main statistics (numDetected / numClones = recall) from a given line of a .report file
    Extraction is terminated as soon as an empty line is encountered

    e.g. input: 
    [
        '              Type-1: 20777 / 47146 = 0.44069486276672465', 
        '              Type-2: 3474 / 4609 = 0.7537426773703624', 
        '      Type-2 (blind): 242 / 386 = 0.6269430051813472', 
        ' Type-2 (consistent): 3232 / 4223 = 0.765332701870708', 
        'Very-Strongly Type-3: 3270 / 4163 = 0.7854912322844103', 
        '     Strongly Type-3: 6526 / 16631 = 0.3923997354338284', 
        '    Moderatly Type-3: 4152 / 83444 = 0.0497579214802742', 
        'Weakly Type-3/Type-4: 2583 / 8219320 = 3.1425957378469267E-4',
        ' ',
        ' ignored'
    ]

    Returns:
    [
        {'Type': 'Type-1', 'numDetected': '20777', 'numClones': '47146', 'recall': '0.44069486276672465'}, 
        {'Type': 'Type-2', 'numDetected': '3474', 'numClones': '4609', 'recall': '0.7537426773703624'}, 
        {'Type': 'Type-2 (blind)', 'numDetected': '242', 'numClones': '386', 'recall': '0.6269430051813472'}, 
        {'Type': 'Type-2 (consistent)', 'numDetected': '3232', 'numClones': '4223', 'recall': '0.765332701870708'}, 
        {'Type': 'Very-Strongly Type-3', 'numDetected': '3270', 'numClones': '4163', 'recall': '0.7854912322844103'}, 
        {'Type': 'Strongly Type-3', 'numDetected': '6526', 'numClones': '16631', 'recall': '0.3923997354338284'}, 
        {'Type': 'Moderatly Type-3', 'numDetected': '4152', 'numClones': '83444', 'recall': '0.0497579214802742'}, 
        {'Type': 'Weakly Type-3/Type-4', 'numDetected': '2583', 'numClones': '8219320', 'recall': '3.1425957378469267E-4'}
    ]
        """
    statistic = []
    for line in lines:
        # empty line means we have reached the end of the current text block -> break and return collected values
        if not line.strip():
            break
        
        # extract the values from the line, e.g.:
        # Type-1: 18358 / 47146 = 0.38938616213464555 
        # to
        # ['Type-1', '18358', '47146', '0.38938616213464555']
        line = line.split(":")
        cloneType = line[0].strip()
        detectedNumber = line[1].split("/")[0].strip()
        totalNumber = line[1].split("/")[1].split("=")[0].strip()
        recallPercent = line[1].rsplit("=",1)[1].strip()

        data = {
            'Type': cloneType, 
            'numDetected': detectedNumber, 
            'numClones': totalNumber, 
            'recall': recallPercent
        }
        statistic.append(data)
    

    return statistic

def extract_statistics_from_file(reportFilePath: Path) -> list[dict]:
    """
    extracts the tool name, runtime, total number of reported clones (true and false positives) 
    and main statistics from a .report file 
    main statistics means the values of the following report part:
        ================================================================================
            All Functionalities
        ================================================================================
        -- Recall Per Clone Type (type: numDetected / numClones = recall) --
                    Type-1: 18358 / 47146 = 0.38938616213464555
                    Type-2: 3318 / 4609 = 0.719895855934042
            Type-2 (blind): 228 / 386 = 0.5906735751295337
        Type-2 (consistent): 3090 / 4223 = 0.7317073170731707
        Very-Strongly Type-3: 1854 / 4163 = 0.44535190968051885
            Strongly Type-3: 1825 / 16631 = 0.10973483254163911
            Moderatly Type-3: 2427 / 83444 = 0.02908537462250132
        Weakly Type-3/Type-4: 60438 / 8219320 = 0.007353163035384923

    Returns:
    [
        {'Type': 'Type-1', 'numDetected': '20777', 'numClones': '47146', 'recall': '0.44069486276672465', 'Name': 'StoneDetector', 'Runtime': '6719.07', 'TotalReportedClones (true and false positives)': '1030568'}, 
        {'Type': 'Type-2', 'numDetected': '3474', 'numClones': '4609', 'recall': '0.7537426773703624', 'Name': 'StoneDetector', 'Runtime': '6719.07', 'TotalReportedClones (true and false positives)': '1030568'}, 
        {'Type': 'Type-2 (blind)', 'numDetected': '242', 'numClones': '386', 'recall': '0.6269430051813472', 'Name': 'StoneDetector', 'Runtime': '6719.07', 'TotalReportedClones (true and false positives)': '1030568'}, 
        {'Type': 'Type-2 (consistent)', 'numDetected': '3232', 'numClones': '4223', 'recall': '0.765332701870708', 'Name': 'StoneDetector', 'Runtime': '6719.07', 'TotalReportedClones (true and false positives)': '1030568'}, 
        ...
    ]
    """
    reportFilePath = Path(reportFilePath)
    
    # read file
    with open(reportFilePath, "r") as file:
        text = file.read()

    lines = text.split("\n")

    cloneStatistic = []

    # search and extract the main statistics in the report file 
    for index, line in enumerate(lines):
        # get tool name from report file
        #if "Tool:" in line:
        #    toolName = line.split(":")[1]
        #    toolName = line.split("-")[1].strip()
        # get tool name from parent directory
        toolName = reportFilePath.parent.name

        # get total number of found clones (true and false positives included) 
        if "#Clones:" in line:
            totalReportedClones = line.split(":")[1].strip()

        if "Runtime (s) of detectClones:" in line:
            runtime = line.split(":")[1].strip()

        # get main statistic for each clone type
        if "-- Recall Per Clone Type (type: numDetected / numClones = recall) --" in line:
            cloneStatistic = extract_per_clone_type_statistic(lines[index+1:])
            break


    for element in cloneStatistic:
        element['Name'] = toolName
        element['Runtime'] = runtime
        element['TotalReportedClones (true and false positives)'] = totalReportedClones

    return cloneStatistic

def extract_statistics_to_csv(runPath: str|Path, csvPath: Path) -> None:
    """
    extracts the tool name, total number of found clones and main statistics of multiple report files from BigCloneEval
    and export it to a csv file
    """
    runPath = Path(runPath)
    csvPath = Path(csvPath)

    reportFiles = runPath.rglob(f"*/*{settings.benchmarks['reportFileExtension']}")

    totalStatistics = []

    # Iterate through each input file
    for reportFile in reportFiles:
        # get statistics of each detector tool
        statistics = extract_statistics_from_file(reportFile)
        for row in statistics:
            totalStatistics.append(row)

    # create a dataframe
    df = pd.DataFrame(totalStatistics)
    # and reorder the columns
    columnOrder = ['Name', 'Runtime', 'TotalReportedClones (true and false positives)', 'Type', 'numDetected', 'numClones', 'recall']
    df = df[columnOrder]

    df.to_csv(csvPath, index=False)
    print(f"CSV file '{csvPath.name}' has been created.")

