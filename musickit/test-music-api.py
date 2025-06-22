import requests
import json
import csv
from datetime import datetime

def get_library_music():
    try:
        # Read tokens from files
        with open('musickit-developer-token.txt', 'r') as f:
            developer_token = f.read().strip()
        
        with open('music_user_token.txt', 'r') as f:
            user_token = f.read().strip()

        print("\nFetching complete library music...\n")

        url = 'https://api.music.apple.com/v1/me/library/albums'
        headers = {
            'Authorization': f'Bearer {developer_token}',
            'Music-User-Token': user_token
        }
        
        all_items = []
        offset = 0
        limit = 100
        
        # Open CSV file for writing
        output_file = f'library_music_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Album', 'Artist', 'Date Added', 'Link']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            while True:
                params = {
                    'limit': limit,
                    'offset': offset,
                    'include': 'catalog',
                    'sort': '-dateAdded'
                }
                
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code != 200:
                    print(f"Error: {response.status_code}")
                    print("Response:", response.text)
                    break
                    
                data = response.json()
                items = data.get('data', [])
                
                if not items:
                    break
                    
                for item in items:
                    attributes = item['attributes']
                    name = attributes.get('name', 'Unknown Name')
                    artist = attributes.get('artistName', 'Unknown Artist')
                    date_added = attributes.get('dateAdded', 'Unknown Date')
                    
                    # Get catalog URL
                    catalog_url = None
                    if 'relationships' in item and 'catalog' in item['relationships']:
                        catalog_data = item['relationships']['catalog']['data']
                        if catalog_data:
                            catalog_url = catalog_data[0].get('attributes', {}).get('url')
                    
                    # Skip items without an artist
                    if artist == 'Unknown Artist':
                        continue
                    
                    # Write to CSV
                    writer.writerow({
                        'Album': name,
                        'Artist': artist,
                        'Date Added': date_added,
                        'Link': catalog_url or 'No URL Available'
                    })
                    
                    # Print to console
                    print(f"Name: {name}")
                    print(f"Artist: {artist}")
                    print(f"Added: {date_added}")
                    print("-------------------")
                    
                    all_items.append(item)
                
                offset += limit
                print(f"Fetched {len(all_items)} albums so far...")
                
            print(f"\nTotal albums fetched: {len(all_items)}")
            print(f"Output written to {output_file}")
            
    except FileNotFoundError as e:
        print(f"Error: Could not find token file - {str(e)}")
    except json.JSONDecodeError:
        print("Error: Failed to parse API response")
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {str(e)}")

if __name__ == "__main__":
    get_library_music()
