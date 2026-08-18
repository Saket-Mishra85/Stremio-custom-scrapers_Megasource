import json
import requests
from bs4 import BeautifulSoup

def get_streams(media_type, media_id, config):
    """
    MegaSource core entry point.
    media_type: 'movie' or 'series'
    media_id: string (IMDb ID, e.g., 'tt0111161', or TMDB ID depending on your catalog)
    config: dictionary containing user configuration settings passed from the addon
    """
    streams = []
    
    # 1. Target provider configuration
    base_url = "https://example-streaming-website.com" 
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    # 2. Handle series formatting if media_id contains episode data (e.g., "tt0111161:1:1")
    # Public catalogs often pass TV shows as 'imdb_id:season:episode'
    season = None
    episode = None
    
    if ":" in media_id:
        parts = media_id.split(":")
        media_id = parts[0]
        if len(parts) > 2:
            season = parts[1]
            episode = parts[2]

    # 3. Build the search path based on content type
    if media_type == "movie":
        search_url = f"{base_url}/movie/{media_id}"
    else:
        search_url = f"{base_url}/tv/{media_id}/{season}/{episode}"

    try:
        # 4. Fetch and parse the target website's HTML source
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 5. Extract the source video tags (Adjust selector to match your target site)
            video_tags = soup.find_all('video')
            for index, video in enumerate(video_tags):
                video_url = video.get('src')
                if video_url:
                    # 6. Format the dictionary exactly as required by Stremio/MegaSource
                    streams.append({
                        "name": "📂 My Custom Scraper",
                        "title": f"Source {index + 1}\n⚡ Direct Stream",
                        "url": video_url
                    })
    except Exception as e:
        # Return a visible error stream layout if the request breaks
        return [{
            "name": "⚠️ Scraper Error",
            "title": str(e),
            "url": ""
        }]

    # 7. MegaSource expects a standard Python list returned (it handles the JSON conversion itself)
    return streams
