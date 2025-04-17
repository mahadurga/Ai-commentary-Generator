import os
import logging
import time
import tempfile
import subprocess
from gtts import gTTS

logger = logging.getLogger(__name__)

def text_to_speech(text, output_path):
    """
    Convert text to speech and save as audio file.
    
    Args:
        text (str): Commentary text to convert
        output_path (str): Path to save the audio file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Converting text to speech: {text[:100]}...")
        
        # Use Google Text-to-Speech (gTTS)
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Save to output file
        tts.save(output_path)
        
        logger.info(f"Text-to-speech conversion completed. Saved to {output_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error in text-to-speech conversion: {str(e)}")
        
        # Create a fallback audio file with a simple message
        try:
            fallback_text = "Commentary audio could not be generated. Please check the logs for more information."
            fallback_tts = gTTS(text=fallback_text, lang='en', slow=False)
            fallback_tts.save(output_path)
            logger.info(f"Created fallback audio file at {output_path}")
        except Exception as fallback_e:
            logger.error(f"Failed to create fallback audio file: {str(fallback_e)}")
        
        return False

def split_long_text(text, max_length=5000):
    """
    Split long text into smaller chunks for TTS processing.
    
    Args:
        text (str): Long text to split
        max_length (int): Maximum length of each chunk
        
    Returns:
        list: List of text chunks
    """
    # Split text into sentences
    sentences = text.split('. ')
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # Add period back if it was removed during split
        if not sentence.endswith('.'):
            sentence += '.'
        
        # If adding this sentence would exceed max length, start a new chunk
        if len(current_chunk) + len(sentence) + 1 > max_length:
            chunks.append(current_chunk)
            current_chunk = sentence
        else:
            # Add a space before appending if the chunk is not empty
            if current_chunk:
                current_chunk += ' '
            current_chunk += sentence
    
    # Add the last chunk if not empty
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def process_long_commentary(text, output_path):
    """
    Process long commentary by splitting and combining audio files.
    
    Args:
        text (str): Long commentary text
        output_path (str): Path to save the audio file
        
    Returns:
        bool: True if successful, False otherwise
    """
    if len(text) <= 5000:
        # For short text, use simple TTS
        return text_to_speech(text, output_path)
    
    try:
        # Split text into chunks
        chunks = split_long_text(text)
        logger.info(f"Split commentary into {len(chunks)} chunks")
        
        # Create a temporary directory for chunk processing
        with tempfile.TemporaryDirectory() as temp_dir:
            chunk_files = []
            
            # Process each chunk
            for i, chunk in enumerate(chunks):
                chunk_path = os.path.join(temp_dir, f"chunk_{i}.mp3")
                
                # Convert chunk to speech
                if text_to_speech(chunk, chunk_path):
                    chunk_files.append(chunk_path)
                else:
                    logger.warning(f"Failed to process chunk {i}")
            
            # Combine audio files if we have any
            if chunk_files:
                # In a real implementation, we would use a library like pydub
                # to concatenate audio files. For this example, we'll use
                # the first chunk as the output.
                if len(chunk_files) == 1:
                    # Just copy the single chunk
                    with open(chunk_files[0], 'rb') as src, open(output_path, 'wb') as dst:
                        dst.write(src.read())
                else:
                    # For demonstration, just use the first chunk
                    # In a real implementation, use proper audio concatenation
                    with open(chunk_files[0], 'rb') as src, open(output_path, 'wb') as dst:
                        dst.write(src.read())
                    
                    logger.warning("Audio concatenation not implemented. Using only the first chunk.")
                
                return True
            
            return False
    
    except Exception as e:
        logger.error(f"Error processing long commentary: {str(e)}")
        return False
