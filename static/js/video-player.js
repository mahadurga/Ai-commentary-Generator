document.addEventListener('DOMContentLoaded', function() {
    // Elements for video and commentary playback
    const videoPlayer = document.getElementById('results-video');
    const audioPlayer = document.getElementById('commentary-audio');
    const playButton = document.getElementById('play-button');
    const pauseButton = document.getElementById('pause-button');
    const muteButton = document.getElementById('mute-button');
    const volumeControl = document.getElementById('volume-control');
    const progressBar = document.getElementById('video-progress');
    const currentTime = document.getElementById('current-time');
    const totalTime = document.getElementById('total-time');
    const eventsTimeline = document.getElementById('events-timeline');
    const cricketEvents = document.getElementById('cricket-events');
    
    // Initialize player controls if video player exists
    if (videoPlayer) {
        initializeVideoPlayer();
    }
    
    function initializeVideoPlayer() {
        // Add event listeners for controls
        if (playButton) {
            playButton.addEventListener('click', playMedia);
        }
        
        if (pauseButton) {
            pauseButton.addEventListener('click', pauseMedia);
        }
        
        if (muteButton) {
            muteButton.addEventListener('click', toggleMute);
        }
        
        if (volumeControl) {
            volumeControl.addEventListener('input', updateVolume);
        }
        
        // Add click event to progress container
        const progressContainer = document.getElementById('progress-container');
        if (progressContainer) {
            progressContainer.addEventListener('click', seekVideo);
        }
        
        // Video events
        videoPlayer.addEventListener('loadedmetadata', initializeVideo);
        videoPlayer.addEventListener('timeupdate', updateProgressBar);
        videoPlayer.addEventListener('ended', videoEnded);
        
        // Get events data for timeline
        fetchEventsData();
    }
    
    function initializeVideo() {
        // Set up initial video state
        updateTimeDisplay();
        
        // Synchronize audio with video
        if (audioPlayer) {
            audioPlayer.volume = 0.8; // Set default audio volume
        }
        
        // Enable controls once video is loaded
        if (playButton) playButton.disabled = false;
        if (pauseButton) pauseButton.disabled = false;
        if (muteButton) muteButton.disabled = false;
        if (volumeControl) volumeControl.disabled = false;
        if (progressBar) progressBar.disabled = false;
    }
    
    function playMedia() {
        try {
            // Play video with promise handling
            const playPromise = videoPlayer.play();
            
            if (playPromise !== undefined) {
                playPromise.then(() => {
                    // Video started playing successfully
                    // Update UI
                    if (playButton) playButton.style.display = 'none';
                    if (pauseButton) pauseButton.style.display = 'inline-block';
                }).catch(error => {
                    console.log("Error playing video:", error);
                    // Don't update UI if play failed
                });
            }
        } catch (e) {
            console.error("Error in playMedia:", e);
        }
    }
    
    function pauseMedia() {
        try {
            // First update UI to prevent rapid toggling
            if (pauseButton) pauseButton.style.display = 'none';
            if (playButton) playButton.style.display = 'inline-block';
            
            // Then pause media
            if (!videoPlayer.paused) {
                videoPlayer.pause();
            }
            
            if (audioPlayer && !audioPlayer.paused) {
                audioPlayer.pause();
            }
        } catch (e) {
            console.error("Error in pauseMedia:", e);
        }
    }
    
    function toggleMute() {
        videoPlayer.muted = !videoPlayer.muted;
        if (audioPlayer) audioPlayer.muted = videoPlayer.muted;
        
        // Update UI
        if (muteButton) {
            muteButton.innerHTML = videoPlayer.muted ? 
                '<i class="bi bi-volume-mute-fill"></i>' : 
                '<i class="bi bi-volume-up-fill"></i>';
        }
    }
    
    function updateVolume() {
        if (volumeControl) {
            const volume = volumeControl.value;
            videoPlayer.volume = volume;
            if (audioPlayer) audioPlayer.volume = volume;
        }
    }
    
    function seekVideo(e) {
        const progressContainer = document.querySelector('.progress');
        if (progressContainer) {
            const rect = progressContainer.getBoundingClientRect();
            const percent = (e.clientX - rect.left) / rect.width;
            const seekTime = percent * videoPlayer.duration;
            
            videoPlayer.currentTime = seekTime;
            if (audioPlayer) {
                // Try to keep audio in sync with video
                audioPlayer.currentTime = seekTime;
            }
        }
    }
    
    function updateProgressBar() {
        if (videoPlayer.duration) {
            const percent = (videoPlayer.currentTime / videoPlayer.duration) * 100;
            
            // Update the progress bar
            const progressBarElem = document.getElementById('video-progress-bar');
            if (progressBarElem) {
                progressBarElem.style.width = `${percent}%`;
            }
        }
        
        updateTimeDisplay();
        highlightCurrentEvents();
    }
    
    function updateTimeDisplay() {
        if (currentTime && totalTime) {
            currentTime.textContent = formatTime(videoPlayer.currentTime);
            totalTime.textContent = formatTime(videoPlayer.duration);
        }
    }
    
    function formatTime(seconds) {
        if (isNaN(seconds)) return '0:00';
        
        const minutes = Math.floor(seconds / 60);
        seconds = Math.floor(seconds % 60);
        return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
    }
    
    function videoEnded() {
        // Reset UI
        if (playButton) playButton.style.display = 'inline-block';
        if (pauseButton) pauseButton.style.display = 'none';
        
        // Pause audio if it's still playing
        if (audioPlayer && !audioPlayer.paused) {
            audioPlayer.pause();
        }
    }
    
    // Cricket events handling
    function fetchEventsData() {
        fetch('/api/events')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success' && data.events) {
                    displayEvents(data.events);
                    createEventTimeline(data.events);
                }
            })
            .catch(error => {
                console.error('Error fetching events:', error);
            });
    }
    
    function displayEvents(events) {
        if (!cricketEvents) return;
        
        // Clear existing events
        cricketEvents.innerHTML = '';
        
        if (events.length === 0) {
            cricketEvents.innerHTML = '<p class="text-center text-muted">No events detected in this video.</p>';
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
        const eventList = document.createElement('ul');
        eventList.className = 'list-group';
        
        for (const type in eventsByType) {
            const typeEvents = eventsByType[type];
            
            // Create type header
            const typeHeader = document.createElement('li');
            typeHeader.className = 'list-group-item active';
            typeHeader.textContent = `${type.charAt(0).toUpperCase() + type.slice(1)} Events (${typeEvents.length})`;
            eventList.appendChild(typeHeader);
            
            // Add individual events
            typeEvents.forEach(event => {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
                listItem.setAttribute('data-timestamp', event.timestamp);
                
                // Event description
                const description = document.createElement('div');
                description.innerHTML = `
                    <strong>${event.subtype || ''}</strong>
                    <small class="d-block text-muted">at ${formatTime(event.timestamp)}</small>
                `;
                
                // Jump to event button
                const jumpButton = document.createElement('button');
                jumpButton.className = 'btn btn-sm btn-outline-primary';
                jumpButton.innerHTML = '<i class="bi bi-play-fill"></i>';
                jumpButton.addEventListener('click', () => {
                    jumpToEvent(event.timestamp);
                });
                
                listItem.appendChild(description);
                listItem.appendChild(jumpButton);
                eventList.appendChild(listItem);
            });
        }
        
        cricketEvents.appendChild(eventList);
    }
    
    function createEventTimeline(events) {
        if (!eventsTimeline || !videoPlayer.duration) return;
        
        // Clear existing markers
        eventsTimeline.innerHTML = '';
        
        events.forEach(event => {
            // Calculate position as percentage of video duration
            const position = (event.timestamp / videoPlayer.duration) * 100;
            
            // Create marker
            const marker = document.createElement('div');
            marker.className = 'event-marker';
            marker.style.left = `${position}%`;
            
            // Set color based on event type
            switch(event.type) {
                case 'boundary':
                    marker.classList.add('boundary-event');
                    break;
                case 'wicket':
                    marker.classList.add('wicket-event');
                    break;
                case 'shot_played':
                    marker.classList.add('shot-event');
                    break;
                default:
                    marker.classList.add('other-event');
            }
            
            // Add tooltip with event info
            marker.setAttribute('data-bs-toggle', 'tooltip');
            marker.setAttribute('data-bs-placement', 'top');
            marker.setAttribute('title', `${event.type}: ${event.subtype || ''} at ${formatTime(event.timestamp)}`);
            
            // Add click handler to jump to event
            marker.addEventListener('click', () => {
                jumpToEvent(event.timestamp);
            });
            
            eventsTimeline.appendChild(marker);
        });
        
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    function jumpToEvent(timestamp) {
        try {
            // First pause everything
            if (!videoPlayer.paused) {
                videoPlayer.pause();
            }
            if (audioPlayer && !audioPlayer.paused) {
                audioPlayer.pause();
            }
            
            // Wait a moment before seeking
            setTimeout(() => {
                // Seek video to event timestamp
                videoPlayer.currentTime = timestamp;
                if (audioPlayer) {
                    audioPlayer.currentTime = timestamp;
                }
                
                // Wait a bit before playing to let the seek complete
                setTimeout(() => {
                    // Play media
                    playMedia();
                }, 100);
            }, 50);
        } catch (e) {
            console.error("Error in jumpToEvent:", e);
        }
    }
    
    function highlightCurrentEvents() {
        // Highlight events near the current time
        if (!cricketEvents) return;
        
        const currentVideoTime = videoPlayer.currentTime;
        const tolerance = 2; // seconds
        
        // Find all event items
        const eventItems = cricketEvents.querySelectorAll('li[data-timestamp]');
        
        eventItems.forEach(item => {
            const timestamp = parseFloat(item.getAttribute('data-timestamp'));
            
            // Check if this event is currently active
            if (Math.abs(currentVideoTime - timestamp) <= tolerance) {
                item.classList.add('current-event');
            } else {
                item.classList.remove('current-event');
            }
        });
    }
});
