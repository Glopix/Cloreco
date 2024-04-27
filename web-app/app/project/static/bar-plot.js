/**
 interactive Recall Plot Visualization
 
 This script is designed to create an interactive bar chart visualization
 for displaying recall data of different clone detector tools. The data
 is passed from the webserver as a JSON array and rendered using Plotly.js.
 
 Key Functionalities:
 1. Data Handling: Parses the JSON data received from the webserver, 
    extracting unique names and types for the plot.
 2. Plot Generation: Utilizes Plotly.js to generate a grouped bar chart 
    where each group represents a clone detector tool, and each bar within 
    a group represents a specific clone type.
 3. clone type filtering: Offers the ability to dynamically include or 
    exclude specific clone types from the visualization. This is achieved 
    through checkboxes for each clone type, allowing users to tailor the 
    view according to their preferences.
 4. Responsive layout: Ensures that the plot adjusts to different screen 
    sizes and provides an interactive user experience.
 
 Usage:
 - The script expects a global variable 'summaryData' to be available, which 
   should contain the data to be visualized, passed from the webserver.
 - Upon loading, the script initializes the plot with all clone types 
   selected. Users can then interact with the checkboxes to filter the data.
 
 Dependencies:
 - Plotly.js: A plotting library used for creating the bar chart.

 */

document.addEventListener('DOMContentLoaded', function() {
    const plotContainer = document.getElementById('recallPlot');
    const typeSelectorsContainer = document.getElementById('cloneTypeSelectors');

    if (!plotContainer || !typeSelectorsContainer) {
        console.error('Required elements not found on the page.');
        return; 
        // Exit the script if elements are not found
    }

    // extract unique names and types
    let names = new Set(summaryData.map(d => d.Name));
    let types = new Set(summaryData.map(d => d.Type));

    // generate the plot data (x and y values, names of bars)
    function generatePlotData(selectedTypes) {
        let plotData = [];
        names.forEach(name => {
            let trace = {
                x: [],
                y: [],
                name: name,
                type: 'bar'
            };
            selectedTypes.forEach(type => {
                let entry = summaryData.find(d => d.Name === name && d.Type === type);
                if (entry) {
                    trace.x.push(type);
                    trace.y.push(entry.recall);
                }
            });
            plotData.push(trace);
        });
        return plotData;
    }

    // layout settings
    var layout = {
        title: 'Recall comparison by clone type for different clone detector tools',
        xaxis: { title: 'Clone Type' },
        yaxis: { title: 'Recall' },
        barmode: 'group'
    };

    // Initial plot
    Plotly.newPlot(plotContainer, generatePlotData(Array.from(types)), layout);

    // create checkboxes for each clone type
    let typeSelectorsDiv = document.getElementById('cloneTypeSelectors');
    types.forEach(type => {
        let checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = type;
        checkbox.checked = true;
        checkbox.onchange = () => {
            let selectedTypes = Array.from(types).filter(t => document.getElementById(t).checked);
            Plotly.newPlot('recallPlot', generatePlotData(selectedTypes), layout);
        };
        let label = document.createElement('label');
        label.htmlFor = type;
        label.appendChild(document.createTextNode(type));
        typeSelectorsDiv.appendChild(checkbox);
        typeSelectorsDiv.appendChild(label);
    });
});
