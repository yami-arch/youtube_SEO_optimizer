import re
import requests
from urllib.parse import parse_qs,urlparse
import json

def extract_video_id(url):
    """Extract video ID from various YouTube URL formats."""
    if not url:
        return None
    url=url.strip()
    if not url.startswith(('http','https')):
        url='https://'+url

    patterns = [
    r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/|youtube\.com\/e\/|youtube\.com\/watch\?.*v=|youtube\.com\/watch\?.*&v=)([^\s&#]+)',
    r'youtube\.com\/shorts\/([^\s&#]+)'
    ]
    for pattern in patterns:
        match=re.search(pattern,url)
        if match:
            return match.group(1)
    parse_url=urlparse(url)
    if 'youtube.com' in parse_url.netloc:
        if 'watch' in parse_url.path:
            query=parse_qs(parse_url.query)
            if 'v' in query:
                return query['v'][0]
        elif 'shorts' in parse_url.path:
            path_paths=parse_url.path.split('/')
            for i,path in enumerate(path_paths):
                if path=='shorts' and i+1<len(path_paths) :
                    return path_paths[i+1]
    return None



def get_video_platform(url):
    """Determine the video platform from the URL."""
    if not url:
        return "Unknown"
    url=url.strip().lower()

    if "youtube.com" in url or "youtu.be" in url:
        return "YouTube" 
    elif "instagram.com" in url:
        return "Instagram"
    elif "linkedin.com" in url:
        return "Linkedin"
    elif "facebook.com" in url:
        return "Facebook"
    elif "tiktok.com" in url:
        return "Tiktok"
    else:
        return "Unknown"


def get_youtube_metadata(video_id):
    """Get metadata for a YouTube video with falling mechanisms"""

    basic_metadata = {
    "title": f"YouTube Video ({video_id})",
    "description": "",
    "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
    "duration": 300, # Default 5 minutes
    "views": 0,
    "author": "YouTube Creator",
    "platform": "YouTube",
    "video_id":video_id
    }
  
    try:

    # Method 1: Try direct page HTML scraping
        url = f"https://www.youtube.com/watch?v={video_id}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64;     x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96. 0.4664.110 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            html_content=response.text

            title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html_content)
            if title_match:
                basic_metadata["title"] = title_match.group(1)

            # Extract author/channel
            author_match = re.search(r'<link itemprop="name" content="([^"]+)"', html_content)
            if author_match:
                basic_metadata["author"]=author_match.group(1)
            description_match = re.search(r'<meta property="og:description" content="([^"]+)"', html_content)
            if description_match:
                basic_metadata["description"] = description_match.group(1)
            

            duration_match = re.search(r'"lengthSeconds":"(\d+)"', html_content)

            if duration_match:
                try:
                    basic_metadata["duration"] = int(duration_match.group(1))
                except ValueError:
                    pass # Use default duration 
            
            views_match = re.search(r'"viewCount":"(\d+)"', html_content)
            if views_match:
                try:
                    basic_metadata["views"] = int(views_match.group(1))
                except ValueError:
                    pass # Use default views

            thumbnail_match = re.search(r'<meta property="og:image" content="([^"]+)"', html_content)
            if thumbnail_match:
                basic_metadata["thumbnail_url"] = thumbnail_match.group(1)  
        
        try:
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            oembed_response = requests.get(oembed_url)

            if oembed_response.status_code==200:
                oembed_data=oembed_response.json()
                if 'title' in oembed_data and oembed_data['title']:
                    basic_metadata['title']=oembed_data['title']
                if 'author_name' in oembed_data and oembed_data['author_name']:
                    basic_metadata['author']=oembed_data['author_name']
                if 'thumbnail_url' in oembed_data and oembed_data['thumbnail_url']:
                    basic_metadata['thumbnail_url']=oembed_data['thumbnail_url']
        except:
            pass

    except Exception as e:
        print(f"Error fetching metadata for video: {str(e)}")
        
    return basic_metadata


def get_video_metadata(url):
    """Get metadata for a video from a URL."""
    if not url:
        raise ValueError("Please enter a video URL")

    # Determine platform
    platform = get_video_platform(url)

    if platform == "YouTube":
        video_id=extract_video_id(url)
        if not video_id:
            raise ValueError("Could not extract videoid from url.Please provide a valid youtube url")
        return get_youtube_metadata(video_id)
    
    else:
        return {
            "title": "video on "+platform,
            "description": "",
            "thumbnail_url": "https://via.placeholder.com/1280x720.png?text="+platform,
            "duration": 300,
            "views": 0,
            "author": platform+"creator",
            "platform": platform,
            "video_id": "unknown"
        }