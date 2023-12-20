let startIndex = 11;  // Define startIndex in a broader scope

// Function to format the date
function format_date(date_string) {
    try {
        const date_object = new Date(date_string);
        const options = { year: 'numeric', month: '2-digit', day: '2-digit' };
        const formatted_date = date_object.toLocaleDateString('en-US', options);
        return formatted_date;
    } catch (error) {
        return "Invalid Date";
    }
}

// Function to create and show an event element
function showEvent(event, index) {
    const eventElement = document.createElement("div");
    eventElement.classList.add("event", (index >= 10) ? 'hidden' : '');

    // Call the format_date function with the correct argument
    const formattedDate = event.geometries[0]?.date ? format_date(event.geometries[0].date) : 'No date available';

    // Create HTML content for the event element
    eventElement.innerHTML = `
        <h3 id="title_${index + 1}" class="pt-5 text-center">${event.title}</h3>
        <p id="date_${index + 1}" class="text-center">${formattedDate}</p>
        <hr class="line" />
    `;

    return eventElement;
}

function toggleHiddenEvents(hiddenEvents) {
    // Toggle visibility for hidden events based on index
    hiddenEvents.forEach(function (event, index) {
        if (index >= 10) {
            event.classList.remove("hidden");
        }
    });
}

function showData(data) {
    const eventsContainer = document.getElementById("events-container");
    const hiddenEvents = [];
    
    // Iterate through the events and display them
    data.events.forEach(function (event, index) {
        const eventElement = showEvent(event, index + startIndex);
        eventsContainer.appendChild(eventElement);
        
        // Track hidden events for toggling visibility
        if (index >= 10) {
            hiddenEvents.push(eventElement);
        }
    });

    // Toggle visibility for hidden events
    toggleHiddenEvents(hiddenEvents);

    // Adjust visibility of the "Load More" button
    if (startIndex >= data.total_count) {
        document.getElementById('load-more-btn').style.display = 'none';
    } else {
        // Move the button to the end of the events
        const loadMoreButton = document.getElementById('load-more-btn');
        eventsContainer.appendChild(loadMoreButton);
    }
}

function loadMoreCatastrophes() {
    // Fetch more catastrophe data with an updated start index
    fetch(`/get_catastrophes?start_index=${startIndex}`)
        .then(response => response.json())
        .then(result => {
            // Display the fetched data
            showData(result);
            startIndex += 10;  // Increment the index for the next load

            // Apply styles to the lines after loading more events
            applyStylesToLines();
        })
        .catch(error => console.error('Error fetching data:', error));
}

// Attach event listener to the "Load More" button
document.getElementById("load-more-btn").addEventListener("click", loadMoreCatastrophes);

// Function to apply styles to the lines
function applyStylesToLines() {
    var lines = document.querySelectorAll('.event .line');
  
    lines.forEach(function (line) {
      // Apply the necessary styles or adjustments to each line
      line.style.width = '100%';
      line.style.height = '2px';
      line.style.backgroundColor = 'white';
      line.style.margin = '10px 0';
    });
  }
  
  // Add a click event to the "Watch More" button
  document.getElementById('load-more-btn').addEventListener('click', function () {
    // Here you should have the code to load more events and add them to the DOM
  
    // After adding the new events, reapply the styles
    applyStylesToLines();
  });
  
  // Call the function to apply styles to the lines initially
  applyStylesToLines();