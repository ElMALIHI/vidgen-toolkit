# Copyright (c) 2025 Stephen G. Pope
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.



import os
import ffmpeg
import logging
from services.file_management import download_file

# Set the default local storage directory
STORAGE_PATH = "/tmp/"
logger = logging.getLogger(__name__)

def apply_video_effect(video_url, effect_type, effect_params, job_id, webhook_url=None):
    """
    Apply various video effects to a video file.
    
    Args:
        video_url (str): URL of the video file to process
        effect_type (str): Type of effect to apply (e.g., 'blur', 'sharpen', 'grayscale', etc.)
        effect_params (dict): Parameters specific to the effect type
        job_id (str): Unique job identifier
        webhook_url (str, optional): URL to send webhook notifications
        
    Returns:
        str: Path to the processed video file
    """
    input_filename = download_file(video_url, os.path.join(STORAGE_PATH, f"{job_id}_input"))
    output_filename = f"{job_id}_effect.mp4"
    output_path = os.path.join(STORAGE_PATH, output_filename)
    
    try:
        # Create a base input stream
        stream = ffmpeg.input(input_filename)
        
        # Apply the requested effect
        if effect_type == 'blur':
            # Get blur amount (default: 5)
            blur_amount = effect_params.get('amount', 5)
            # Apply boxblur filter
            stream = stream.video.filter('boxblur', blur_amount)
            
        elif effect_type == 'sharpen':
            # Get sharpen amount (default: 5)
            sharpen_amount = effect_params.get('amount', 5)
            # Apply unsharp filter
            stream = stream.video.filter('unsharp', 5, 5, sharpen_amount, 5, 5, 0)
            
        elif effect_type == 'grayscale':
            # Apply grayscale filter
            stream = stream.video.filter('colorchannelmixer', 0.3, 0.4, 0.3, 0, 0.3, 0.4, 0.3, 0, 0.3, 0.4, 0.3, 0)
            
        elif effect_type == 'sepia':
            # Apply sepia filter
            stream = stream.video.filter('colorchannelmixer', 0.393, 0.769, 0.189, 0, 0.349, 0.686, 0.168, 0, 0.272, 0.534, 0.131, 0)
            
        elif effect_type == 'vignette':
            # Get vignette amount (default: 0.3)
            vignette_amount = effect_params.get('amount', 0.3)
            # Apply vignette filter
            stream = stream.video.filter('vignette', vignette_amount)
            
        elif effect_type == 'mirror':
            # Get mirror direction (default: horizontal)
            direction = effect_params.get('direction', 'horizontal')
            if direction == 'horizontal':
                stream = stream.video.filter('hflip')
            elif direction == 'vertical':
                stream = stream.video.filter('vflip')
                
        elif effect_type == 'rotate':
            # Get rotation angle (default: 90)
            angle = effect_params.get('angle', 90)
            # Apply rotation filter
            stream = stream.video.filter('rotate', angle * 3.14159 / 180)
            
        elif effect_type == 'speed':
            # Get speed factor (default: 2.0 - twice as fast)
            speed = effect_params.get('factor', 2.0)
            # Apply setpts filter to adjust speed
            stream = stream.video.filter('setpts', f'PTS/{speed}')
            # Also adjust audio speed if present
            audio = ffmpeg.input(input_filename).audio.filter('atempo', min(2.0, max(0.5, speed)))
            # Output with both video and audio
            stream = ffmpeg.output(stream, audio, output_path)
            
        elif effect_type == 'reverse':
            # Reverse video
            stream = stream.video.filter('reverse')
            # Also reverse audio if present
            audio = ffmpeg.input(input_filename).audio.filter('areverse')
            # Output with both video and audio
            stream = ffmpeg.output(stream, audio, output_path)
            
        else:
            # If no valid effect is specified, just copy the video
            logger.warning(f"Unknown effect type '{effect_type}', copying video without effects")
            stream = stream
        
        # If we haven't already created an output (for special cases like speed and reverse)
        if effect_type not in ['speed', 'reverse']:
            # Get the audio from the input
            audio = ffmpeg.input(input_filename).audio
            # Create output with both video and audio
            stream = ffmpeg.output(stream, audio, output_path)
        
        # Run the FFmpeg command
        stream.run(overwrite_output=True)
        
        # Clean up input file
        os.remove(input_filename)
        
        logger.info(f"Video effect '{effect_type}' applied successfully: {output_path}")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error applying video effect: {str(e)}")
        # Clean up input file if it exists
        if os.path.exists(input_filename):
            os.remove(input_filename)
        raise