import requests
from bs4 import BeautifulSoup

def get_streams(media_type, media_id, config):
    """
    MegaSource entry point.
    media_type: 'movie' or 'series'
    media_id: string (IMDb ID, e.g., 'tt0111161', or 'tt0111161:1:1' for series)
    config: dict containing optional user config parameters
    """
    streams = []
    
    # 1. Base URL of the target streaming site or indexer
    base_url = "https://example-streaming-website.com" 
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    # 2. Parse series data if packed into the ID (e.g. "imdb_id:season:episode")
    season = None
    episode = None
    imdb_id = media_id

    if ":" in media_id:
        parts = media_id.split(":")
        imdb_id = parts[0]
        if len(parts) > 2:
            season = parts[1]
            episode = parts[2]

    # 3. Formulate the path based on media type
    if media_type == "movie":
        search_url = f"{base_url}/movie/{imdb_id}"
    else:
        search_url = f"{base_url}/tv/{imdb_id}/{season}/{episode}"

    try:
        # 4. Fetch the target data
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 5. Extract video streaming links (Match your site's HTML layout)
            video_tags = soup.find_all('video')
            for index, video in enumerate(video_tags):
                video_url = video.get('src')
                if video_url:
                    # 6. Append formatted stream objects
                    streams.append({
                        "name": "📂 My Custom Scraper",
                        "title": f"Source {index + 1}\n⚡ Direct Stream",
                        "url": video_url
                    })
    except Exception as e:
        # If an error happens, return a clean message as a fake stream option
        return [{
            "name": "⚠️ Scraper Error",
            "title": str(e),
            "url": ""
        }]

    # MegaSource reads the raw returned python list directly
    return streams
