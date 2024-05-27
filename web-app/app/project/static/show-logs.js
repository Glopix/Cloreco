

document.addEventListener('DOMContentLoaded', function() {

    if (!window.EventSource) {
        // IE or an old browser
        alert("The browser doesn't support EventSource.");
        return;
    }

    function clear_logs() {
        var logs = document.getElementById("log-terminal");
        while (logs.firstChild) {
            logs.removeChild(logs.firstChild);
        }
    }

    // colorize a HTML element (designed for logEntry paragraphs)
    function colorize_element(element) {
        if (!element.innerHTML.includes('|')) {
            return
        }
        // extract log level from the message
        const logLevel = element.innerHTML.split('|')[1].trim();

        // apply a CSS class based on the log level
        // these classes are stored in the ansi_colors.css file and resemble console ansi color codes
        switch (logLevel) {
            case 'ERROR':
                element.classList.add('ansi91');
                break;
            case 'SUCCESS':
                element.classList.add('ansi92');
                break;
            case 'WARNING':
                element.classList.add('ansi93');
                break;
            case 'INFO':
                //element.classList.add('ansi97');
                break;
            case 'TRACE':
                element.classList.add('ansi90');
                break;
        }
    }

    // append a new message to the log shown on the website
    function display_log_entry(msg) {
        const logs = document.getElementById("log-terminal");
        // skip this message if it's the same as the last message
        if(logs.hasChildNodes() && logs.lastChild.innerHTML === msg) {
            //console.log(msg)
            return
        }
        const logEntry = document.createElement("p");
        logEntry.innerHTML = msg;
        colorize_element(logEntry);
        logs.appendChild(logEntry);
    }

    // colorize log entries which have been generated prior to the current page load
    function colorize_past_logs() {
        const logs = document.getElementById("log-terminal");
        if(!logs.hasChildNodes()) {
            return
        }
        Array.from(logs.children).forEach(colorize_element);
    }

    // hide the progress bar at the top of the page
    function disable_progress_bar() {
        const progressBar = document.getElementById("progress-bar");
        progressBar.classList.add("hidden");
    }

    function toggle_loading_icon(enabled) {
        const loadingIcon = document.getElementById("loading-spinner");

        if (enabled == true) {
            loadingIcon.classList.remove("hidden")
        }
        else {
            loadingIcon.classList.add("hidden")
        }
    }

    const nextStepButton = document.getElementById("nextStep");
    // show, enable or disabled "nextStep" button, 
    // if the logs are for an imageBuild process 
    // and depending on wether the build was started or successfully finished
    function setup_nextStep_button(progressUpdate) {
        if (progressUpdate.type === "imageBuild") {
            nextStepButton.classList.remove('hidden');
        }

        if (progressUpdate.status === "success") {
            nextStepButton.classList.remove('pure-button-disabled');
            
            // Scroll to the end of the page, to the "next-step" button
            document.getElementById("content").scrollTo(0, document.getElementById("content").scrollHeight);

            // go to next page (add tool via image) if the "next"(nextStep) button is clicked
            // also, add the image URL and tool name in the query string
            // these values will be used to pre-fill the corresponding form fields
            nextStepButton.addEventListener('click', function(event) {
                event.preventDefault();
                let toolName = progressUpdate.toolName;
                let imageURL = progressUpdate.imageURL;
                let action = this.getAttribute('data-action');
                let queryString = `?toolName=${encodeURIComponent(toolName)}&imageURL=${encodeURIComponent(imageURL)}`;
                window.location.href = action + queryString;
            });
        } 
    }

    function update_progress(progressUpdate) {
        setup_nextStep_button(progressUpdate);
        
        if (updateProgressBar) {
            update_progress_bar(progressUpdate);
        }

        if (progressUpdate.status === "startup") {
            nextStepButton.classList.add('pure-button-disabled');
            clear_logs();
        }
    }

    // change the progress bar fill state and displayed message
    function update_progress_bar(progressUpdate) {
        const progressBarFill  = document.getElementById("progress-bar-fill");
        const messageElement = document.getElementById("progress-bar-message");
        let message;

        //console.log(progressUpdate)

        if(progressUpdate.status !== "no heartbeat"){
            // save this progress update for later use, if it needs to restore later (e.g. if a heartbeat was skipped)
            progress = progressUpdate;
        }

        if (['running', 'finished', 'startup'].includes(progressUpdate.status)) {
            // add imaginary extra steps to the progress bar calculation as long as the run is not finished
            let extraSteps = 1;
            if(progressUpdate.status === "finished" ){
                extraSteps = 0;
            }

            let progressPercent = (100 / (parseInt(progressUpdate.totalSteps) + extraSteps)) * parseInt(progressUpdate.currentStep);
            progressBarFill.style.width = progressPercent + "%";

            // concatenate steps and message, e.g.: (1/5)  executing NiCad
            message = `(${progressUpdate.currentStep}/${progressUpdate.totalSteps})  ${progressUpdate.currentMessage}`;

            // reset color of the progress bar
            progressBarFill.style.backgroundColor = null

        // in case of an error of any sort
        } else if (['error', 'failure', 'aborted'].includes(progressUpdate.status)) {
            // display the received error message in the progress bar
            message = progressUpdate.currentMessage;
            progressBarFill.style.backgroundColor = "red";
            //progressBarFill.style.width = "0%";
        }else if (progressUpdate.status === "no heartbeat"){
            // display a "no heartbeat" message only if the last progress status is not already a error
            if (!['error', 'failure', 'aborted'].includes(progress.status)) {
                message = progressUpdate.currentMessage;
                progressBarFill.style.backgroundColor = "red";
            }
        }

        // if a message was set in the previous steps: display it
        if (message) {
            messageElement.innerText = message;
        }

        // if a message specifies a color: display it
        if (progressUpdate.color) {
            progressBarFill.style.backgroundColor = progressUpdate.color;
        }
    }


    function initialize_event_source(channel, eventName, handler) {
        var source = new EventSource(channel);
        source.onopen = function() {
            console.log(`DEBUG: ${eventName} Event: open`)
        };
        source.onerror = function(e) {
            //console.log(e);
            display_log_entry(`DEBUG: ${eventName} Event: error`);

            if (this.readyState === source.CONNECTING) {
                display_log_entry(`DEBUG: Reconnecting (readyState=${this.readyState})...`);
            } else {
                display_log_entry(`DEBUG: Error has occurred.`);

            }
        };
        source.onmessage = function(e) {
            var data = JSON.parse(e.data);
            handler(data.message);
        };
        return source;
    }

    function start_check_heartbeat() {
        // create a new interval if no interval was created before
        if (!heartbeatInterval) {
            heartbeatInterval = setInterval(check_heartbeat, 1000); // Check every 1 second
        }
    }
    function stop_check_heartbeat() {
        if (heartbeatInterval) {
            clearInterval(heartbeatInterval);
            toggle_loading_icon(false)
            heartbeatInterval = undefined;
        }
    }

    function check_heartbeat() {
        const currentTime = Date.now();
        if (currentTime - lastHeartbeatTime > 2000) {
            // no heartbeat was received in time (2 seconds)
            // Display an error message in the progress bar
            heartbeatReceived = false;
            let progressUpdate = {
                status: "no heartbeat",
                currentMessage: "No run seems to be executed at the moment"
            };
            update_progress_bar(progressUpdate);
            toggle_loading_icon(false)
        } else {
            // heartbeat was received in time, everything is fine
            
            if (!heartbeatReceived) {
                // Clear the error message and restore last "normal" message if heartbeat is received
                update_progress_bar(progress);
                toggle_loading_icon(false)
                heartbeatReceived = true;

                toggle_loading_icon(true)
            }
        }
    }

    // control the heartbeat check based on the latest progress status
    function control_heartbeats() {
        if (progress.isExecuted === "True") {
            start_check_heartbeat();
            toggle_loading_icon(true)
        } else {
            stop_check_heartbeat();
        }
    }

    // if a new heartbeat is received
    function handle_heartbeat(message) {
        lastHeartbeatTime = Date.now();
        control_heartbeats()
    }


    function close_event_source(eventSource) {
        eventSource.close()      
    }

    // close all EventSources (SSE) before page unload (on exit/reload of this page)
    window.addEventListener('beforeunload', function(event) {
        SSE_eventSources.forEach(close_event_source);
    });


    // Initial Setup
    var progress = JSON.parse(initialProgress);
    var updateProgressBar = true;
    if (progress.progressBar === "disabled") {
        updateProgressBar = false;
        disable_progress_bar();
    }
    else {
        update_progress_bar(progress);
    }
    setup_nextStep_button(progress);

    const SSE_eventSources = [];
    // Server-sent events of current container status logs
    // current container status logs: log entries, stdout from the container
    let SSE_logs = initialize_event_source(logsChannel, 'logs', display_log_entry);
    SSE_eventSources.push(SSE_logs);

    // Server-sent events of current container execution progress
    // progress: dict/json with current step, total steps and current message, e.g.: 
    // {
    // "currentStep" : 2,
    // "totalSteps"  : 5,
    // "currentMessage" : "executing NiCad..."
    // }
    let SSE_progress = initialize_event_source(progressChannel, 'progress', update_progress);
    SSE_eventSources.push(SSE_progress);
    
    // Server-sent events of heartbeats
    // every second heartbeats are sent to the web clients via server-sent events
    // as periodic signal to indicate normal operation of the container execution
    // These heartbeats should be received here, if a container is executed
    let SSE_heartbeats = initialize_event_source(heartbeatsChannel, 'heartbeats', handle_heartbeat);
    SSE_eventSources.push(SSE_heartbeats);

    var lastHeartbeatTime = Date.now();
    var heartbeatReceived = true;

    var heartbeatInterval;

    colorize_past_logs();

});

