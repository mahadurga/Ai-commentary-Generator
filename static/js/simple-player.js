document.addEventListener('DOMContentLoaded', function() {
    // Simple event handler for the "Jump to Events" button
    const eventsButton = document.getElementById('events-button');
    if (eventsButton) {
        eventsButton.addEventListener('click', function() {
            // Scroll to the events section
            const eventsSection = document.getElementById('cricket-events');
            if (eventsSection) {
                eventsSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
    
    // Populate the events list
    fetch('/api/events')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success' && data.events) {
                displayEvents(data.events);
            }
        })
        .catch(error => {
            console.error('Error fetching events:', error);
            const eventsContainer = document.getElementById('cricket-events');
            if (eventsContainer) {
                eventsContainer.innerHTML = '<div class="alert alert-warning">Could not load events. Please try again later.</div>';
            }
        });
    
    function displayEvents(events) {
        const eventsContainer = document.getElementById('cricket-events');
        if (!eventsContainer) return;
        
        // Clear loading spinner
        eventsContainer.innerHTML = '';
        
        if (events.length === 0) {
            eventsContainer.innerHTML = '<p class="text-center">No events detected in this video.</p>';
            return;
        }
        
        // Group events by type
        const eventsByType = {};
        events.forEach(event => {
            const type = event.type;
            if (!eventsByType[type]) {
                eventsByType[type] = [];
            }
            eventsByType[type].push(event);
        });
        
        // Create event list
        const eventList = document.createElement('div');
        eventList.className = 'list-group';
        
        for (const type in eventsByType) {
            const typeEvents = eventsByType[type];
            
            // Create type header
            const typeHeader = document.createElement('div');
            typeHeader.className = 'list-group-item list-group-item-dark';
            typeHeader.innerHTML = `<strong>${capitalizeFirstLetter(type)} Events (${typeEvents.length})</strong>`;
            eventList.appendChild(typeHeader);
            
            // Add individual events
            typeEvents.forEach(event => {
                const listItem = document.createElement('div');
                listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
                
                // Event description
                const description = document.createElement('div');
                description.innerHTML = `
                    <div><strong>${event.subtype ? capitalizeFirstLetter(event.subtype) : ''}</strong></div>
                    <small class="text-muted">at ${formatTime(event.timestamp)}</small>
                `;
                
                listItem.appendChild(description);
                eventList.appendChild(listItem);
            });
        }
        
        eventsContainer.appendChild(eventList);
    }
    
    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
    
    function formatTime(seconds) {
        if (isNaN(seconds)) return '0:00';
        
        const minutes = Math.floor(seconds / 60);
        seconds = Math.floor(seconds % 60);
        return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
    }
});