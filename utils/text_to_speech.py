import os
import logging
import time
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
        
        # If the text is too long, split it
        if len(text) > 5000:
            chunks = split_long_text(text)
            logger.info(f"Text is long, split into {len(chunks)} chunks")
            return process_text_chunks(chunks, output_path)
        
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

def process_text_chunks(chunks, output_path):
    """
    Process chunks of text and create a single audio file.
    For demo purposes, we'll only process the first chunk.
    
    Args:
        chunks (list): List of text chunks
        output_path (str): Path to save the audio file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # For demo purposes, just use the first chunk
        # In a real implementation, we would combine multiple audio files
        if chunks:
            first_chunk = chunks[0]
            tts = gTTS(text=first_chunk, lang='en', slow=False)
            tts.save(output_path)
            
            logger.info(f"Created audio from first chunk (of {len(chunks)}). Saved to {output_path}")
            
            # Add a note about using only the first part
            if len(chunks) > 1:
                logger.warning("Only using first part of commentary for demo purposes.")
            
            return True
        else:
            return False
    
    except Exception as e:
        logger.error(f"Error processing text chunks: {str(e)}")
        return False
