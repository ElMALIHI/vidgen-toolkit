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

def apply_transition(video1_url, video2_url, transition_type, transition_params, job_id, webhook_url=None):
    """
    Apply a transition effect between two videos.
    
    Args:
        video1_url (str): URL of the first video file
        video2_url (str): URL of the second video file
        transition_type (str): Type of transition to apply (e.g., 'fade', 'wipe', 'dissolve', etc.)
        transition_params (dict): Parameters specific to the transition type
        job_id (str): Unique job identifier
        webhook_url (str, optional): URL to send webhook notifications
        
    Returns:
        str: Path to the processed video file with transition
    """
    # Download input videos
    video1_path = download_file(video1_url, os.path.join(STORAGE_PATH, f"{job_id}_video1"))
    video2_path = download_file(video2_url, os.path.join(STORAGE_PATH, f"{job_id}_video2"))
    output_filename = f"{job_id}_transition.mp4"
    output_path = os.path.join(STORAGE_PATH, output_filename)
    
    try:
        # Get transition duration (default: 1 second)
        duration = transition_params.get('duration', 1.0)
        
        # Create input streams
        video1 = ffmpeg.input(video1_path)
        video2 = ffmpeg.input(video2_path)
        
        # Get video information
        probe1 = ffmpeg.probe(video1_path)
        video1_duration = float(probe1['format']['duration'])
        
        # Apply the requested transition
        if transition_type == 'fade':
            # Create fade out for video1
            v1_fade = video1.video.filter('fade', type='out', start_time=video1_duration-duration, duration=duration)
            # Create fade in for video2
            v2_fade = video2.video.filter('fade', type='in', start_time=0, duration=duration)
            
            # Get audio from both videos
            a1 = video1.audio.filter('afade', type='out', start_time=video1_duration-duration, duration=duration)
            a2 = video2.audio.filter('afade', type='in', start_time=0, duration=duration)
            
            # Create temporary output files
            temp1 = os.path.join(STORAGE_PATH, f"{job_id}_temp1.mp4")
            temp2 = os.path.join(STORAGE_PATH, f"{job_id}_temp2.mp4")
            
            # Output each video with its fade effect
            ffmpeg.output(v1_fade, a1, temp1).run(overwrite_output=True)
            ffmpeg.output(v2_fade, a2, temp2).run(overwrite_output=True)
            
            # Create a concat file
            concat_file = os.path.join(STORAGE_PATH, f"{job_id}_concat.txt")
            with open(concat_file, 'w') as f:
                f.write(f"file '{os.path.abspath(temp1)}'\
                \nfile '{os.path.abspath(temp2)}'")
            
            # Concatenate the videos
            ffmpeg.input(concat_file, format='concat', safe=0).output(output_path, c='copy').run(overwrite_output=True)
            
            # Clean up temporary files
            os.remove(temp1)
            os.remove(temp2)
            os.remove(concat_file)
            
        elif transition_type == 'dissolve':
            # Get the resolution of videos
            width = probe1['streams'][0]['width']
            height = probe1['streams'][0]['height']
            
            # Create a complex filter for crossfade/dissolve
            # First, we need to trim video1 to remove the transition part
            v1_main = video1.video.filter('trim', start=0, end=video1_duration-duration)
            # Then create the transition part from video1
            v1_trans = video1.video.filter('trim', start=video1_duration-duration).filter('setpts', 'PTS-STARTPTS')
            
            # Create the transition part from video2
            v2_trans = video2.video.filter('trim', start=0, end=duration).filter('setpts', 'PTS-STARTPTS')
            # Then the main part of video2
            v2_main = video2.video.filter('trim', start=duration).filter('setpts', 'PTS-STARTPTS')
            
            # Create the crossfade/dissolve effect
            xfade = ffmpeg.filter([v1_trans, v2_trans], 'xfade', transition='fade', duration=duration, offset=0)
            
            # Concatenate all parts
            video = ffmpeg.concat(v1_main, xfade, v2_main)
            
            # Handle audio similarly
            a1_main = video1.audio.filter('atrim', start=0, end=video1_duration-duration)
            a1_trans = video1.audio.filter('atrim', start=video1_duration-duration).filter('asetpts', 'PTS-STARTPTS')
            a2_trans = video2.audio.filter('atrim', start=0, end=duration).filter('asetpts', 'PTS-STARTPTS')
            a2_main = video2.audio.filter('atrim', start=duration).filter('asetpts', 'PTS-STARTPTS')
            
            # Create audio crossfade
            axfade = ffmpeg.filter([a1_trans, a2_trans], 'acrossfade', d=duration)
            
            # Concatenate audio parts
            audio = ffmpeg.concat(a1_main, axfade, a2_main, v=0, a=1)
            
            # Output the final video with audio
            ffmpeg.output(video, audio, output_path).run(overwrite_output=True)
            
        elif transition_type == 'wipe':
            # Direction of wipe (default: 'left')
            direction = transition_params.get('direction', 'left')
            
            # Map direction to transition name
            transition_map = {
                'left': 'slideright',
                'right': 'slideleft',
                'up': 'slidedown',
                'down': 'slideup',
            }
            
            transition_name = transition_map.get(direction, 'slideright')
            
            # Create a complex filter for wipe transition
            # First, we need to trim video1 to remove the transition part
            v1_main = video1.video.filter('trim', start=0, end=video1_duration-duration)
            # Then create the transition part from video1
            v1_trans = video1.video.filter('trim', start=video1_duration-duration).filter('setpts', 'PTS-STARTPTS')
            
            # Create the transition part from video2
            v2_trans = video2.video.filter('trim', start=0, end=duration).filter('setpts', 'PTS-STARTPTS')
            # Then the main part of video2
            v2_main = video2.video.filter('trim', start=duration).filter('setpts', 'PTS-STARTPTS')
            
            # Create the wipe transition effect
            xfade = ffmpeg.filter([v1_trans, v2_trans], 'xfade', transition=transition_name, duration=duration, offset=0)
            
            # Concatenate all parts
            video = ffmpeg.concat(v1_main, xfade, v2_main)
            
            # Handle audio similarly to dissolve
            a1_main = video1.audio.filter('atrim', start=0, end=video1_duration-duration)
            a1_trans = video1.audio.filter('atrim', start=video1_duration-duration).filter('asetpts', 'PTS-STARTPTS')
            a2_trans = video2.audio.filter('atrim', start=0, end=duration).filter('asetpts', 'PTS-STARTPTS')
            a2_main = video2.audio.filter('atrim', start=duration).filter('asetpts', 'PTS-STARTPTS')
            
            # Create audio crossfade
            axfade = ffmpeg.filter([a1_trans, a2_trans], 'acrossfade', d=duration)
            
            # Concatenate audio parts
            audio = ffmpeg.concat(a1_main, axfade, a2_main, v=0, a=1)
            
            # Output the final video with audio
            ffmpeg.output(video, audio, output_path).run(overwrite_output=True)
            
        else:
            # If no valid transition is specified, just concatenate the videos
            logger.warning(f"Unknown transition type '{transition_type}', concatenating videos without transition")
            
            # Create a concat file
            concat_file = os.path.join(STORAGE_PATH, f"{job_id}_concat.txt")
            with open(concat_file, 'w') as f:
                f.write(f"file '{os.path.abspath(video1_path)}'\
                \nfile '{os.path.abspath(video2_path)}'")
            
            # Concatenate the videos
            ffmpeg.input(concat_file, format='concat', safe=0).output(output_path, c='copy').run(overwrite_output=True)
            
            # Clean up concat file
            os.remove(concat_file)
        
        # Clean up input files
        os.remove(video1_path)
        os.remove(video2_path)
        
        logger.info(f"Video transition '{transition_type}' applied successfully: {output_path}")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error applying video transition: {str(e)}")
        # Clean up input files if they exist
        if os.path.exists(video1_path):
            os.remove(video1_path)
        if os.path.exists(video2_path):
            os.remove(video2_path)
        raise

def apply_multi_video_transition(video_urls, transition_type, transition_params, job_id, webhook_url=None):
    """
    Apply transitions between multiple videos.
    
    Args:
        video_urls (list): List of video URLs to process
        transition_type (str): Type of transition to apply
        transition_params (dict): Parameters specific to the transition type
        job_id (str): Unique job identifier
        webhook_url (str, optional): URL to send webhook notifications
        
    Returns:
        str: Path to the processed video file with transitions
    """
    if len(video_urls) < 2:
        raise ValueError("At least two videos are required to apply transitions")
    
    # If only two videos, use the simple transition function
    if len(video_urls) == 2:
        return apply_transition(video_urls[0], video_urls[1], transition_type, transition_params, job_id, webhook_url)
    
    # For more than two videos, apply transitions sequentially
    temp_output = None
    
    try:
        for i in range(len(video_urls) - 1):
            # For the first pair, use the original URLs
            if i == 0:
                video1_url = video_urls[i]
                video2_url = video_urls[i + 1]
                temp_job_id = f"{job_id}_trans_{i}"
                temp_output = apply_transition(video1_url, video2_url, transition_type, transition_params, temp_job_id, webhook_url)
            else:
                # For subsequent pairs, use the previous output as the first video
                video2_url = video_urls[i + 1]
                # Create a file:// URL for the temporary output
                video1_url = f"file://{temp_output}"
                temp_job_id = f"{job_id}_trans_{i}"
                # Store the current temp_output to delete it later
                prev_output = temp_output
                # Apply the next transition
                temp_output = apply_transition(video1_url, video2_url, transition_type, transition_params, temp_job_id, webhook_url)
                # Delete the previous temporary output
                if os.path.exists(prev_output):
                    os.remove(prev_output)
        
        # Rename the final output to the job_id
        final_output = os.path.join(STORAGE_PATH, f"{job_id}_final.mp4")
        os.rename(temp_output, final_output)
        
        return final_output
        
    except Exception as e:
        logger.error(f"Error applying multiple video transitions: {str(e)}")
        # Clean up temporary output if it exists
        if temp_output and os.path.exists(temp_output):
            os.remove(temp_output)
        raise