import requests
import json

def get_recent_music():
    try:
        # Read tokens from files
        with open('musickit-developer-token.txt', 'r') as f:
            developer_token = f.read().strip()
        
        with open('music_user_token.txt', 'r') as f:
            user_token = f.read().strip()

        print("\nFetching recently added music...\n")

        url = 'https://api.music.apple.com/v1/me/library/recently-added'
        headers = {
            'Authorization': f'Bearer {developer_token}',
            'Music-User-Token': user_token
        }
        params = {
            'limit': 25,  # Maximum allowed limit
            'include': 'catalog'
        }

        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if not data.get('data'):
                print("No recently added music found.")
                return
            
            total_items = len(data['data'])
            print(f"Found {total_items} items\n")
                
            for item in data['data']:
                attributes = item['attributes']
                name = attributes.get('name', 'Unknown Name')
                artist = attributes.get('artistName', 'Unknown Artist')
                date_added = attributes.get('dateAdded', 'Unknown Date')
                
                # Get catalog URL from relationships if available
                catalog_url = None
                if 'relationships' in item and 'catalog' in item['relationships']:
                    catalog_data = item['relationships']['catalog']['data']
                    if catalog_data:
                        catalog_url = catalog_data[0].get('attributes', {}).get('url')
                
                # Skip items without an artist (likely playlists)
                if artist == 'Unknown Artist':
                    continue
                    
                print(f"Name: {name}")
                print(f"Artist: {artist}")
                print(f"Added: {date_added}")
                print(f"Apple Music Link: {catalog_url or 'No URL Available'}")
                print("-------------------")
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
    get_recent_music()
