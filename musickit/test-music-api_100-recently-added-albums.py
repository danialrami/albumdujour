import requests
import json
from datetime import datetime

def get_library_music():
    try:
        # Read tokens from files
        with open('musickit-developer-token.txt', 'r') as f:
            developer_token = f.read().strip()
        
        with open('music_user_token.txt', 'r') as f:
            user_token = f.read().strip()

        print("\nFetching library music...\n")

        url = 'https://api.music.apple.com/v1/me/library/albums'
        headers = {
            'Authorization': f'Bearer {developer_token}',
            'Music-User-Token': user_token
        }
        params = {
            'limit': 100,
            'include': 'catalog',
            'sort': '-dateAdded'  # Sort by most recently added first
        }

        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if not data.get('data'):
                print("No music found in library.")
                return
            
            total_items = len(data['data'])
            print(f"Found {total_items} items\n")
            
            # Open file for writing
            output_file = 'library_music.txt'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Apple Music Library Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                
                for item in data['data']:
                    attributes = item['attributes']
                    name = attributes.get('name', 'Unknown Name')
                    artist = attributes.get('artistName', 'Unknown Artist')
                    date_added = attributes.get('dateAdded', 'Unknown Date')
                    
                    # Get catalog URL from relationships
                    catalog_url = None
                    if 'relationships' in item and 'catalog' in item['relationships']:
                        catalog_data = item['relationships']['catalog']['data']
                        if catalog_data:
                            catalog_url = catalog_data[0].get('attributes', {}).get('url')
                    
                    # Skip items without an artist
                    if artist == 'Unknown Artist':
                        continue
                    
                    # Write to file
                    f.write(f"Album: {name}\n")
                    f.write(f"Artist: {artist}\n")
                    f.write(f"Added: {date_added}\n")
                    f.write(f"Link: {catalog_url or 'No URL Available'}\n")
                    f.write("-" * 50 + "\n\n")
                    
                    # Also print to console
                    print(f"Name: {name}")
                    print(f"Artist: {artist}")
                    print(f"Added: {date_added}")
                    print("-------------------")
            
            print(f"\nOutput written to {output_file}")
        else:
            print(f"Error: {response.status_code}")
            print("Response:", response.text)
            
    except FileNotFoundError as e:
        print(f"Error: Could not find token file - {str(e)}")
    except json.JSONDecodeError:
        print("Error: Failed to parse API response")
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {str(e)}")

if __name__ == "__main__":
    get_library_music()
