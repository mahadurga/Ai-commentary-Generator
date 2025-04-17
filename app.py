import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
import uuid
import time
from pathlib import Path

# Import utility modules
from utils.video_processor import process_video
from utils.commentary_generator import generate_commentary
from utils.text_to_speech import text_to_speech

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "cricket-analysis-secret")

# For YouTube link handling
YTDLP_AVAILABLE = False
try:
    # We're only importing this for feature detection
    # If not available, the YouTube feature will be disabled
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    logger.warning("yt-dlp not installed. YouTube video import will be disabled.")

# Configure folders
UPLOAD_FOLDER = Path('./static/uploads')
RESULTS_FOLDER = Path('./static/results')
SAMPLE_FOLDER = Path('./static/samples')
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

# Create necessary folders if they don't exist
UPLOAD_FOLDER.mkdir(exist_ok=True, parents=True)
RESULTS_FOLDER.mkdir(exist_ok=True, parents=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER
app.config['SAMPLE_FOLDER'] = SAMPLE_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if a file was uploaded
    if 'video' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
    
    file = request.files['video']
    
    # If user does not select file, browser submits an empty file
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Create a unique filename
        unique_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        base_filename, extension = os.path.splitext(filename)
        unique_filename = f"{base_filename}_{unique_id}{extension}"
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Store file information in session
        session['uploaded_video'] = {
            'filename': unique_filename,
            'original_name': filename,
            'path': file_path,
            'unique_id': unique_id,
            'timestamp': time.time()
        }
        
        return redirect(url_for('process_video_view'))
    else:
        flash('File type not allowed. Please upload a video file (mp4, avi, mov, mkv)', 'danger')
        return redirect(url_for('index'))

@app.route('/process')
def process_video_view():
    if 'uploaded_video' not in session:
        # For demo purposes, create a sample video entry
        session['uploaded_video'] = {
            'filename': 'samples/sample-cricket.mp4',
            'original_name': 'Sample Cricket Video.mp4',
            'path': os.path.join('static', 'samples', 'sample-cricket.mp4'),
            'unique_id': 'sample-12345',
            'timestamp': time.time()
        }
        logger.info("Created sample video entry for demo")
    
    video_info = session['uploaded_video']
    return render_template('process.html', video=video_info)

@app.route('/start_processing', methods=['POST'])
def start_processing():
    if 'uploaded_video' not in session:
        return jsonify({'status': 'error', 'message': 'No uploaded video found'})
    
    video_info = session['uploaded_video']
    video_path = video_info['path']
    unique_id = video_info['unique_id']
    
    try:
        # Process the video and get detected events
        logger.debug(f"Starting to process video: {video_path}")
        
        # Define output paths
        output_video_path = os.path.join(app.config['RESULTS_FOLDER'], f"processed_{unique_id}.mp4")
        output_audio_path = os.path.join(app.config['RESULTS_FOLDER'], f"commentary_{unique_id}.mp3")
        
        # Process the video to detect events (players, ball, shots, boundaries, wickets)
        events = process_video(video_path, output_video_path)
        
        # Generate commentary based on detected events
        commentary = generate_commentary(events)
        
        # Convert commentary to speech
        logger.info(f"Converting commentary to speech: {len(commentary)} characters")
        from utils.text_to_speech import text_to_speech
        success = text_to_speech(commentary, output_audio_path)
        
        if not success:
            logger.warning("Failed to generate commentary audio, using sample instead")
            import shutil
            sample_audio = os.path.join(app.config['SAMPLE_FOLDER'], 'sample-commentary.mp3')
            shutil.copy(sample_audio, output_audio_path)
        
        # Update session with results
        session['processing_results'] = {
            'processed_video': output_video_path,
            'commentary_audio': output_audio_path,
            'events': events,
            'commentary': commentary
        }
        
        return jsonify({
            'status': 'success', 
            'message': 'Video processing completed', 
            'redirect': url_for('results')
        })
    
    except Exception as e:
        logger.error(f"Error during video processing: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Error processing video: {str(e)}'})

@app.route('/results')
def results():
    if 'processing_results' not in session:
        # For demo purposes, create sample results
        if 'uploaded_video' not in session:
            # Also create a sample video entry if needed
            session['uploaded_video'] = {
                'filename': 'samples/sample-cricket.mp4',
                'original_name': 'Sample Cricket Video.mp4',
                'path': os.path.join('static', 'samples', 'sample-cricket.mp4'),
                'unique_id': 'sample-12345',
                'timestamp': time.time()
            }
        
        # Sample event data
        from utils.video_processor import generate_simulated_events
        sample_events = generate_simulated_events()
        
        # Sample commentary
        from utils.commentary_generator import generate_commentary
        sample_commentary = generate_commentary(sample_events)
        
        # Create sample results
        session['processing_results'] = {
            'processed_video': os.path.join('static', 'samples', 'sample-cricket.mp4'),
            'commentary_audio': os.path.join('static', 'samples', 'sample-commentary.mp3'),
            'events': sample_events,
            'commentary': sample_commentary
        }
        logger.info("Created sample results for demo")
    
    video_info = session['uploaded_video']
    results_info = session['processing_results']
    
    return render_template('results.html', 
                          video=video_info, 
                          results=results_info)

@app.route('/youtube_link', methods=['POST'])
def youtube_link():
    if not YTDLP_AVAILABLE:
        flash('YouTube download functionality is not available. Please upload a video file directly.', 'danger')
        return redirect(url_for('index'))
    
    youtube_url = request.form.get('youtube_url')
    if not youtube_url:
        flash('No YouTube URL provided', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Create a unique ID for this video
        unique_id = str(uuid.uuid4())
        
        # Set the output file path
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"youtube_{unique_id}.mp4")
        
        # Download options
        ydl_opts = {
            'format': 'best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
            'outtmpl': output_path,
            'noplaylist': True,
            'restrictfilenames': True,
            'merge_output_format': 'mp4',
            'verbose': True
        }
        
        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Downloading YouTube video: {youtube_url}")
            info = ydl.extract_info(youtube_url, download=True)
            # Get video title
            video_title = info.get('title', 'YouTube Video')
        
        # Store file information in session
        session['uploaded_video'] = {
            'filename': os.path.basename(output_path),
            'original_name': f"{video_title}.mp4",
            'path': output_path,
            'unique_id': unique_id,
            'timestamp': time.time(),
            'source': 'youtube'
        }
        
        return redirect(url_for('process_video_view'))
    
    except Exception as e:
        logger.error(f"Error downloading YouTube video: {str(e)}")
        flash(f"Error downloading video: {str(e)}", 'danger')
        return redirect(url_for('index'))

@app.route('/api/events')
def get_events():
    if 'processing_results' not in session:
        # For demo purposes, generate sample events
        from utils.video_processor import generate_simulated_events
        sample_events = generate_simulated_events()
        return jsonify({'status': 'success', 'events': sample_events})
    
    events = session['processing_results'].get('events', [])
    return jsonify({'status': 'success', 'events': events})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
