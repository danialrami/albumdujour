import requests
import json
import gspread
import pandas as pd
from pathlib import Path
from gspread_formatting import DataValidationRule, BooleanCondition
from gspread_formatting import set_data_validation_for_cell_range
from gspread_formatting import ConditionalFormatRule, GridRange
from gspread_formatting import format_cell_range, Color

def update_music_sheet():
    try:
        # Setup Google Sheets connection
        script_dir = Path(__file__).parent
        credentials_path = script_dir / 'concrete-spider-446700-f9-4646496845d1.json'
        gc = gspread.service_account(filename=str(credentials_path))
        spreadsheet = gc.open("2025-media")
        music_sheet = spreadsheet.get_worksheet(0)  # First worksheet

        # Read Apple Music tokens
        with open('./utilities/musickit/musickit-developer-token.txt', 'r') as f:
            developer_token = f.read().strip()
        with open('./utilities/musickit/music_user_token.txt', 'r') as f:
            user_token = f.read().strip()

        # Fetch recently added music from Apple Music API
        url = 'https://api.music.apple.com/v1/me/library/recently-added?include=catalog'
        headers = {
            'Authorization': f'Bearer {developer_token}',
            'Music-User-Token': user_token
        }

        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if not data.get('data'):
                print("No recently added music found.")
                return

            # Get existing sheet data
            existing_data = music_sheet.get_all_records()
            existing_urls = [row.get('Link', '') for row in existing_data]
            
            new_entries = []
            for item in data['data']:
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
                
                # Skip playlists and already existing entries
                if artist == 'Unknown Artist' or (catalog_url and catalog_url in existing_urls):
                    continue
                
                # Prepare new row
                new_entry = {
                    'Music': f"{name} - {artist}",
                    'Link': catalog_url or 'No URL Available',
                    'Status': 'Open'  # Changed order to match sheet columns
                }
                new_entries.append(new_entry)
                print(f"Adding: {new_entry['Music']}")

            # Add new entries to sheet
            if new_entries:
                # Get the next empty row
                next_row = len(existing_data) + 2  # +2 for header and 1-based indexing
                
                # Prepare the values to append
                values = [[entry['Music'], entry['Link'], entry['Status']] 
                         for entry in new_entries]
                
                # Append rows
                music_sheet.append_rows(values)

                # Add dropdown validation to Status column
                for i in range(len(new_entries)):
                    target_row = next_row + i
                    target_cell = f'C{target_row}'
                    
                    # Create validation rule for dropdown
                    validation_rule = DataValidationRule(
                        BooleanCondition('ONE_OF_LIST', ['Open', 'Current', 'Done']),
                        showCustomUi=True
                    )
                    set_data_validation_for_cell_range(music_sheet, target_cell, validation_rule)

                print(f"\nAdded {len(new_entries)} new albums to the sheet.")
            else:
                print("\nNo new albums to add.")

        else:
            print(f"Error: {response.status_code}")
            print("Response:", response.text)
            
    except FileNotFoundError as e:
        print(f"Error: Could not find token file - {str(e)}")
    except json.JSONDecodeError:
        print("Error: Failed to parse API response")
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {str(e)}")
    except Exception as e:
        print(f"Error updating sheet: {str(e)}")

if __name__ == "__main__":
    update_music_sheet()