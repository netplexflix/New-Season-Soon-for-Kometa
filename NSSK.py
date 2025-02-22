import requests
import yaml
from datetime import datetime, timedelta, UTC
from collections import defaultdict
import sys
import os

NSSK_VERSION = "1.2"

# ANSI color codes
GREEN = '\033[32m'
ORANGE = '\033[33m'
BLUE = '\033[34m'
RED = '\033[31m'
RESET = '\033[0m'
BOLD = '\033[1m'

def load_config(file_path='config.yml'):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Config file '{file_path}' not found.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML config file: {e}")
        sys.exit(1)

def process_sonarr_url(base_url, api_key):
    base_url = base_url.rstrip('/')
    
    if base_url.startswith('http'):
        protocol_end = base_url.find('://') + 3
        next_slash = base_url.find('/', protocol_end)
        if next_slash != -1:
            base_url = base_url[:next_slash]
    
    api_paths = [
        '/api/v3',
        '/sonarr/api/v3'
    ]
    
    for path in api_paths:
        test_url = f"{base_url}{path}"
        try:
            headers = {"X-Api-Key": api_key}
            response = requests.get(f"{test_url}/health", headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"Successfully connected to Sonarr at: {test_url}")
                return test_url
        except requests.exceptions.RequestException as e:
            print(f"{ORANGE}Testing URL {test_url} - Failed: {str(e)}{RESET}")
            continue
    
    raise ConnectionError(f"{RED}Unable to establish connection to Sonarr. Tried the following URLs:\n" + 
                        "\n".join([f"- {base_url}{path}" for path in api_paths]) + 
                        f"\nPlease verify your URL and API key and ensure Sonarr is running.{RESET}")

def get_sonarr_series(sonarr_url, api_key):
    try:
        url = f"{sonarr_url}/series"
        headers = {"X-Api-Key": api_key}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"{RED}Error connecting to Sonarr: {str(e)}{RESET}")
        sys.exit(1)

def get_sonarr_episodes(sonarr_url, api_key, series_id):
    try:
        url = f"{sonarr_url}/episode?seriesId={series_id}"
        headers = {"X-Api-Key": api_key}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"{RED}Error fetching episodes from Sonarr: {str(e)}{RESET}")
        sys.exit(1)

def find_new_season_shows(sonarr_url, api_key, future_days, skip_unmonitored=False):
    cutoff_date = datetime.now(UTC) + timedelta(days=future_days)
    matched_shows = []
    skipped_shows = []
    
    all_series = get_sonarr_series(sonarr_url, api_key)
    
    for series in all_series:
        episodes = get_sonarr_episodes(sonarr_url, api_key, series['id'])
        
        future_episodes = []
        for ep in episodes:
            air_date_str = ep.get('airDateUtc')
            if not air_date_str:
                continue
            
            air_date = datetime.fromisoformat(air_date_str.replace('Z','')).replace(tzinfo=UTC)
            
            if air_date > datetime.now(UTC):
                future_episodes.append(ep)
        
        future_episodes.sort(key=lambda x: datetime.fromisoformat(x['airDateUtc'].replace('Z','')).replace(tzinfo=UTC))
        
        if not future_episodes:
            continue
        
        next_future = future_episodes[0]
        
        air_date_next_str = next_future.get('airDateUtc')
        if not air_date_next_str:
            continue
        
        air_date_next = datetime.fromisoformat(air_date_next_str.replace('Z','')).replace(tzinfo=UTC)
        
        if (
            next_future['seasonNumber'] >= 1
            and next_future['episodeNumber'] == 1
            and not next_future['hasFile']
            and air_date_next <= cutoff_date
        ):
            tvdb_id = series.get('tvdbId')
            air_date_str_yyyy_mm_dd = air_date_next.date().isoformat()

            show_dict = {
                'title': series['title'],
                'seasonNumber': next_future['seasonNumber'],
                'airDate': air_date_str_yyyy_mm_dd,
                'tvdbId': tvdb_id
            }
            
            if skip_unmonitored:
                episode_monitored = next_future.get("monitored", True)
                
                season_monitored = True
                for season_info in series.get("seasons", []):
                    if season_info.get("seasonNumber") == next_future['seasonNumber']:
                        season_monitored = season_info.get("monitored", True)
                        break
                
                if not episode_monitored or not season_monitored:
                    skipped_shows.append(show_dict)
                    continue
            
            matched_shows.append(show_dict)
    
    return matched_shows, skipped_shows

def create_overlay_yaml(output_file, shows, config):
    import yaml
    from copy import deepcopy
    from datetime import datetime

    if not shows:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("#No matching shows found")
        return
    
    # Group shows by date
    date_to_tvdb_ids = defaultdict(list)
    all_tvdb_ids = set()
    for s in shows:
        if s["tvdbId"]:
            all_tvdb_ids.add(s['tvdbId'])
        date_to_tvdb_ids[s['airDate']].append(s['tvdbId'])
    
    overlays_dict = {}
    
    # -- Backdrop Block --
    backdrop_config = deepcopy(config.get("backdrop", {}))
    backdrop_config["name"] = "backdrop"
    all_tvdb_ids_str = ", ".join(str(i) for i in sorted(all_tvdb_ids) if i)
    
    overlays_dict["backdrop"] = {
        "overlay": backdrop_config,
        "tvdb_show": all_tvdb_ids_str
    }
    
    # -- NSSK_<date> Blocks --
    text_config = deepcopy(config.get("text", {}))
    date_format = text_config.pop("date_format", "yyyy-mm-dd")
    use_text = text_config.pop("use_text", "New Season")
    
    def format_date(yyyy_mm_dd):
        dt_obj = datetime.strptime(yyyy_mm_dd, "%Y-%m-%d")
        if date_format == "dd/mm":
            return dt_obj.strftime("%d/%m")
        elif date_format == "mm/dd":
            return dt_obj.strftime("%m/%d")
        elif date_format == "yyyy-mm-dd":
            return dt_obj.strftime("%Y-%m-%d")
        # Fallback
        return dt_obj.strftime(date_format)
    
    for date_str in sorted(date_to_tvdb_ids):
        formatted_date = format_date(date_str)
        sub_overlay_config = deepcopy(text_config)
        sub_overlay_config["name"] = f"text({use_text} {formatted_date})"
        
        tvdb_ids_for_date = sorted(tvdb_id for tvdb_id in date_to_tvdb_ids[date_str] if tvdb_id)
        tvdb_ids_str = ", ".join(str(i) for i in tvdb_ids_for_date)
        
        block_key = f"NSSK_{formatted_date}"
        overlays_dict[block_key] = {
            "overlay": sub_overlay_config,
            "tvdb_show": tvdb_ids_str
        }
    
    final_output = {"overlays": overlays_dict}
    
    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(final_output, f, sort_keys=False)

def create_collection_yaml(output_file, shows, config):
    import yaml
    from yaml.representer import SafeRepresenter

    if not shows:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("#No matching shows found")
        return
    
    tvdb_ids = [s['tvdbId'] for s in shows if s.get('tvdbId')]
    if not tvdb_ids:
        return

    # Convert to comma-separated
    tvdb_ids_str = ", ".join(str(i) for i in sorted(tvdb_ids))

    collection_name = config.get("collection_name", "New Season Soon")
    sort_title_value = config.get("sort_title", "+1_2New Season Soon")
    future_days = config.get("future_days", 21)

    class QuotedString(str):
        pass

    def quoted_str_presenter(dumper, data):
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

    yaml.add_representer(QuotedString, quoted_str_presenter, Dumper=yaml.SafeDumper)

    # Convert our sort_title_value into a QuotedString
    # so PyYAML forces quotes in the output
    sort_title_quoted = QuotedString(sort_title_value)

    data = {
        "collections": {
            collection_name: {
                "summary": f"A new season will air within {future_days} days",
                "sort_title": sort_title_quoted,
                "sync_mode": "sync",
                "tvdb_show": tvdb_ids_str
            }
        }
    }

    with open(output_file, "w", encoding="utf-8") as f:
        # Use SafeDumper so our custom representer is used
        yaml.dump(data, f, Dumper=yaml.SafeDumper, sort_keys=False)

def main():
    print(f"{BLUE}{'*' * 40}\n{'*' * 15} NSSK {NSSK_VERSION} {'*' * 15}\n{'*' * 40}{RESET}")

    config = load_config('config.yml')
    
    try:
        # Process and validate Sonarr URL
        sonarr_url = process_sonarr_url(config['sonarr_url'], config['sonarr_api_key'])
        sonarr_api_key = config['sonarr_api_key']
        future_days = config['future_days']
               
        skip_unmonitored = str(config.get("skip_unmonitored", "false")).lower() == "true"

        # Print chosen values
        print(f"future_days: {future_days}")
        print(f"skip_unmonitored: {skip_unmonitored}\n")

        matched_shows, skipped_shows = find_new_season_shows(
            sonarr_url, sonarr_api_key, future_days, skip_unmonitored
        )
        
        # Print matched shows
        if matched_shows:
            print(f"{GREEN}Shows with a new season starting within {future_days} days:{RESET}")
            for show in matched_shows:
                print(f"- {show['title']} (Season {show['seasonNumber']}) airs on {show['airDate']}")
        else:
            print(f"{RED}No shows with new seasons starting within {future_days} days (or all were skipped).{RESET}")
        
        # Print skipped shows if present
        if skipped_shows:
            print(f"\n{ORANGE}Skipped shows (unmonitored season):{RESET}")
            for show in skipped_shows:
                print(f"- {show['title']} (Season {show['seasonNumber']}) airs on {show['airDate']}")

        # Create YAMLs
        overlay_file = "NSSK_TV_OVERLAYS.yml"
        create_overlay_yaml(overlay_file, matched_shows, config)
        
        collection_file = "NSSK_TV_COLLECTION.yml"
        create_collection_yaml(collection_file, matched_shows, config)
        
        print(f"\nCreated overlay file: {overlay_file}")
        print(f"Created collection file: {collection_file}")

    except ConnectionError as e:
        print(f"{RED}Error: {str(e)}{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}Unexpected error: {str(e)}{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
