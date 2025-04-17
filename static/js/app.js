document.addEventListener('DOMContentLoaded', function() {
    // File upload preview
    const videoUpload = document.getElementById('video-upload');
    const fileDropArea = document.querySelector('.file-drop-area');
    const previewContainer = document.getElementById('preview-container');
    const videoPreview = document.getElementById('video-preview');
    const uploadForm = document.getElementById('upload-form');
    const uploadButton = document.getElementById('upload-button');
    
    // Processing status elements
    const processingStatus = document.getElementById('processing-status');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const startProcessingBtn = document.getElementById('start-processing');
    
    // Initialize file upload preview
    if (videoUpload) {
        // File upload events
        videoUpload.addEventListener('change', handleFileSelect);
        
        // Drag and drop events
        if (fileDropArea) {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                fileDropArea.addEventListener(eventName, preventDefaults, false);
            });
            
            ['dragenter', 'dragover'].forEach(eventName => {
                fileDropArea.addEventListener(eventName, highlight, false);
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                fileDropArea.addEventListener(eventName, unhighlight, false);
            });
            
            fileDropArea.addEventListener('drop', handleDrop, false);
        }
    }
    
    // Initialize processing functionality
    if (startProcessingBtn) {
        startProcessingBtn.addEventListener('click', startProcessing);
    }
    
    // Functions for file upload handling
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight() {
        fileDropArea.classList.add('highlight');
    }
    
    function unhighlight() {
        fileDropArea.classList.remove('highlight');
    }
    
    function handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            displayFilePreview(file);
        }
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const file = dt.files[0];
        
        videoUpload.files = dt.files;
        if (file) {
            displayFilePreview(file);
        }
    }
    
    function displayFilePreview(file) {
        // Check if file is a video
        if (!file.type.match('video.*')) {
            alert('Please upload a video file');
            return;
        }
        
        // Create object URL for preview
        const objectURL = URL.createObjectURL(file);
        
        // Show preview container
        if (previewContainer) {
            previewContainer.style.display = 'block';
        }
        
        // Set video source and display
        if (videoPreview) {
            videoPreview.src = objectURL;
            videoPreview.style.display = 'block';
        }
        
        // Enable upload button
        if (uploadButton) {
            uploadButton.disabled = false;
        }
        
        // Show file info
        const fileInfoElement = document.getElementById('file-info');
        if (fileInfoElement) {
            const fileSize = (file.size / (1024 * 1024)).toFixed(2);
            fileInfoElement.textContent = `${file.name} (${fileSize} MB)`;
            fileInfoElement.style.display = 'block';
        }
    }
    
    // Functions for video processing
    function startProcessing() {
        if (startProcessingBtn) {
            startProcessingBtn.disabled = true;
            startProcessingBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
        }
        
        if (processingStatus) {
            processingStatus.style.display = 'block';
        }
        
        updateProgress(5, 'Initializing video processing...');
        
        // Send request to start processing
        fetch('/start_processing', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                simulateProcessingProgress();
            } else {
                showError(data.message || 'An error occurred during processing');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('Network error. Please try again.');
        });
    }
    
    function simulateProcessingProgress() {
        let progress = 10;
        const steps = [
            { progress: 20, message: 'Analyzing video frames...' },
            { progress: 40, message: 'Detecting players and ball...' },
            { progress: 60, message: 'Classifying cricket shots...' },
            { progress: 75, message: 'Identifying key events...' },
            { progress: 85, message: 'Generating commentary...' },
            { progress: 95, message: 'Creating final output...' },
            { progress: 100, message: 'Processing complete!' }
        ];
        
        let currentStep = 0;
        const interval = setInterval(() => {
            if (currentStep < steps.length) {
                const step = steps[currentStep];
                updateProgress(step.progress, step.message);
                currentStep++;
                
                if (currentStep === steps.length) {
                    // Last step - redirect to results page
                    clearInterval(interval);
                    setTimeout(() => {
                        window.location.href = '/results';
                    }, 1000);
                }
            } else {
                clearInterval(interval);
            }
        }, 3000); // Adjust timing for more realistic simulation
    }
    
    function updateProgress(percent, message) {
        if (progressBar) {
            progressBar.style.width = `${percent}%`;
            progressBar.setAttribute('aria-valuenow', percent);
        }
        
        if (progressText) {
            progressText.textContent = message;
        }
    }
    
    function showError(message) {
        if (processingStatus) {
            // Create error alert
            const errorAlert = document.createElement('div');
            errorAlert.className = 'alert alert-danger mt-3';
            errorAlert.textContent = message;
            
            // Add to processing status container
            processingStatus.appendChild(errorAlert);
            
            // Re-enable button
            if (startProcessingBtn) {
                startProcessingBtn.disabled = false;
                startProcessingBtn.textContent = 'Try Again';
            }
            
            // Reset progress
            updateProgress(0, 'Processing failed');
        }
    }
});
