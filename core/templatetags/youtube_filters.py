from django import template
import re

register = template.Library()

@register.filter
def youtube_embed(url):
    """
    Converts a standard YouTube URL into an embed URL.
    """
    if not url:
        return ""
    
    # Check if it's already an embed URL
    if 'youtube.com/embed/' in url:
        return url
        
    # Extract the video ID
    # Matches watch?v=ID, youtu.be/ID, youtube.com/v/ID
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    match = re.match(youtube_regex, url)
    if match:
        video_id = match.group(6)
        return f"https://www.youtube.com/embed/{video_id}"
    
    return url
