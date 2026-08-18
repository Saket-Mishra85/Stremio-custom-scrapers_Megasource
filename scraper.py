import re
import urllib.parse
import requests
from bs4 import BeautifulSoup

def get_streams(media_type, media_id, config):
    """
    Python wrapper porting Nuvio-TV streaming providers to MegaSource.
    Works by querying the specific media indexer domains.
    """
    streams = []
    
    # 1. Base domain configurations mapped from Nuvio files
    # Options: "vegamovies", "hdhub4u", "uhdmovies", "moviesdrive", "streamimdb.ru", "streamex.sh", "67movies.net"
    target_provider = "hdhub4u" 
    
    domains = {
        "vegamovies": "https://pages.dev", 
        "hdhub4u": "https://hdhub4u.work",
        "uhdmovies": "https://uhdmovies.vip",
        "moviesdrive": "https://moviesdrive.info",
        "streamimdb.ru": "https://streamimdb.ru",
        "streamex.sh": "https://streamex.sh",
        "67movies.net": "https://67movies.net/"
    }
    
    base_url = domains.get(target_provider, "https://pages.dev")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": base_url,
        "Accept-Language": "en-US,en;q=0.9"
    }

    # 2. Safely extract metadata titles from Stremio's ID layer
    # Since these websites use text searches instead of IMDb ID paths, we query meta
    query_title = config.get("title") or "Movie"
    season = None
    episode = None

    if ":" in media_id:
        parts = media_id.split(":")
        if len(parts) > 2:
            season = parts[1]
            episode = parts[2]

    # Clean text query formatting
    search_query = query_title
    if media_type == "series" and season and episode:
        search_query = f"{query_title} S{str(season).zfill(2)}E{str(episode).zfill(2)}"

    encoded_query = urllib.parse.quote_plus(search_query)
    search_url = f"{base_url}/?s={encoded_query}"

    try:
        session = requests.Session()
        search_response = session.get(search_url, headers=headers, timeout=10)
        
        if search_response.status_code == 200:
            soup = BeautifulSoup(search_response.text, 'html.parser')
            
            # Find the first matching post container (Nuvio: search for article tags)
            articles = soup.find_all(['article', 'div'], class_=['post-item', 'blog-post', 'entry-article'])
            if not articles:
                # Fallback standard grid selector link scan
                articles = soup.find_all('a', href=True)
                
            target_post_url = None
            for item in articles:
                link_element = item if item.name == 'a' else item.find('a', href=True)
                if link_element and base_url in link_element['href']:
                    # Simple fuzzy matching to verify it's not a mismatched recommendation
                    if any(word.lower() in link_element.text.lower() for word in query_title.split()):
                        target_post_url = link_element['href']
                        break

            # 3. If target article entry is resolved, scrape the internal landing files
            if target_post_url:
                post_response = session.get(target_post_url, headers=headers, timeout=10)
                post_soup = BeautifulSoup(post_response.text, 'html.parser')
                
                # Nuvio filters through button and mirror anchors looking for specific cdn patterns
                anchors = post_soup.find_all('a', href=True)
                for index, anchor in enumerate(anchors):
                    href = anchor['href']
                    anchor_text = anchor.text.strip()
                    
                    # Target direct cloud downloads or multi-quality web streaming gateways
                    if "download" in href.lower() or "drive" in href.lower() or "vcloud" in href.lower() or "link" in href.lower():
                        
                        # Match resolution strings from text layout labels
                        res_match = re.search(r'(480p|720p|1080p|2160p|4k)', anchor_text + href, re.IGNORECASE)
                        resolution = res_match.group(1).upper() if res_match else "1080p"
                        
                        # Strip tracking layers and package output mapping for MegaSource stream rendering
                        streams.append({
                            "name": f"🍿 Nuvio [{target_provider.upper()}]",
                            "title": f"{query_title} ({resolution})\n🔗 Link #{index + 1} - Tap to Process",
                            "url": href
                        })
                        
    except Exception as e:
        return [{
            "name": "⚠️ Nuvio Engine Error",
            "title": f"Parsing exception: {str(e)}",
            "url": ""
        }]

    # Return empty fallback notice instead of crashing out Stremio's UI wrapper if nothing fits
    if not streams:
        return [{
            "name": f"❌ {target_provider.upper()}",
            "title": "No mirrored sources indexed for this file selection.",
            "url": ""
        }]

    return streams
