# Album du Jour - Implementation Documentation

## Overview

Album du Jour is a static website generator that creates a music discovery showcase from data stored in a Google Sheets spreadsheet. The generated website is deployed to GitHub Pages (or any static hosting) via a git subtree split workflow.

## Architecture

### High-Level Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│ Google Sheets   │────▶│ build_music_site │────▶│  Static     │
│ (2025-media)   │     │     .py          │     │  Website    │
└─────────────────┘     └──────────────────┘     └─────────────┘
                              │                        │
                              ▼                        ▼
                        ┌──────────────────┐     ┌─────────────┐
                        │ build.sh         │     │ GitHub      │
                        │ (orchestration)  │     │ (build branch)
                        └──────────────────┘     └─────────────┘
```

## Data Source

### Google Sheets Spreadsheet

**Spreadsheet Name**: `2025-media`

**Required Columns**:
| Column | Description | Example |
|--------|-------------|---------|
| Music | Album - Artist format | `Volcano - Volcano` |
| Apple Music Link | Full Apple Music URL | `https://music.apple.com/us/album/volcano/1805642752` |
| Spotify Link | Full Spotify URL | `https://open.spotify.com/album/4xmgLubwaLJ6heiz6oit9X` |
| Status | Current/Open/Done | `Current` |
| Date Added | ISO 8601 timestamp | `2025-06-28T10:30:00Z` |
| Date Finished | ISO 8601 timestamp | (optional) |
| 🌞 | Rating emoji | `🌞` (optional) |

### Status Values

- **Current**: Album currently listening to (shown prominently on website)
- **Open**: Albums available to be picked as "Current" randomly
- **Done**: Albums that have been finished (shown in "Recently Finished")

### Album Categorization Logic (build_music_site.py:175-199)

1. **Currently Listening**: `Status == "Current"`
2. **Recently Finished**: Has valid `date_finished` timestamp (and not Current)
3. **Recently Added**: Has valid `date_added` timestamp (and not Current/Finished)
4. **Fallback**: If no "Current" album exists, uses the most recent timestamped album

## Credentials

### Google Sheets API

**Service Account Credentials**:
- Location: `concrete-spider-446700-f9-4646496845d1.json` (in repo root)
- Alternative path: Could be placed anywhere and referenced via environment variable

**Required Scopes**:
- `https://www.googleapis.com/auth/spreadsheets`
- `https://www.googleapis.com/auth/drive`

### Apple Music (Optional)

**Token Location**: `/mnt/barracuda/Nextcloud/ore/Notes/Life/utilities/musickit`
- If not found, website builds without Apple Music embeds (Spotify-only)

## Build Scripts

### master-build.sh

Complete pipeline that runs build.sh followed by deploy.sh.

**Usage**:
```bash
./master-build.sh              # Full pipeline: build + deploy
./master-build.sh --build-only # Build only, skip deployment
./master-build.sh --help       # Show help
```

**Process**:
1. Validates environment (scripts exist, git repo detected)
2. Runs build.sh to generate website
3. Runs deploy.sh to commit and push to Git

### build.sh

Builds the website without Git operations.

**Process**:
1. Creates/activates Python virtual environment (venv/)
2. Installs `gspread` package
3. Runs `build_music_site.py`
4. Generates:
   - `build/index.html` - Main website
   - `build/styles.css` - Styling
   - `build/scripts.js` - JavaScript
   - `build/assets/` - Static assets

### deploy.sh

Deploys the built website to Git.

**Process**:
1. Verifies no credentials in build/ directory (security check)
2. Commits source changes to main branch
3. Uses `git subtree split` to create build branch
4. Pushes both main and build branches to origin

## Git Workflow

### Branch Structure

- **main**: Source code (build.sh, deploy.sh, build_music_site.py, etc.)
- **build**: Generated website files (served by hosting)

### Deployment Method

```bash
# Create build branch from build/ directory
git subtree split --prefix build -b build-deploy

# Push build branch
git push origin build-deploy:build

# Clean up temporary branch
git branch -D build-deploy
```

This approach:
- Preserves full git history
- No risk of deleting repository
- Can be run repeatedly safely

## Python Environment

### Virtual Environment

- **Location**: `venv/`
- **Python Version**: 3.13.2 (created via pyenv)
- **Required Packages**: gspread

### Creating the venv

```bash
# Using pyenv (recommended for version parity with Docker)
pyenv install 3.13.2
~/.pyenv/versions/3.13.2/bin/python3 -m venv venv
./venv/bin/pip install gspread
```

## Automated Triggers

### Current Setup

The website build is triggered via:
1. **n8n workflow** (preferred): Scheduled workflow that runs master-build.sh
2. **Manual**: Run `./master-build.sh` manually

### Historical (Deprecated)

- **systemd timer**: Previously used `albumdujour.timer` but disabled
- **cron**: Not currently used for albumdujour

## Related Projects

### obsidian-scripts (~/repos/obsidian-scripts)

Related project that also reads from the same Google Sheets:
- **media.py**: Generates daily note section showing current music/TV
- **sync.py**: Syncs music library between Apple Music and Google Sheets
- **mark_music_done.py**: Marks current album as "Done"

**Key Difference**:
- albumdujour: Creates public static website
- obsidian-scripts: Creates private daily notes in Obsidian

## Deployment to Live Site

### Current Hosting

- **URL**: https://albumdujour.lufs.audio
- **Provider**: Cloudflare Pages (serves from GitHub build branch)
- **Branch**: `build`

### How It Works

1. Code pushed to main branch
2. deploy.sh creates build branch via subtree split
3. Push to origin triggers Cloudflare Pages deployment
4. Cloudflare serves static files from build branch

## Security Considerations

### Credential Protection

1. **Never stored in repo**: Credentials are in repo root but gitignored
2. **External paths**: Can be placed anywhere, referenced via path
3. **Build verification**: deploy.sh checks for credential leaks before push
4. **Clean builds**: temp credentials are removed after each build

### Build Directory Security

Before deployment, deploy.sh verifies:
- No `.json` credential files
- No `musickit` directories
- No `.env` files
- No credential strings in built HTML

## Troubleshooting

### Common Issues

**ModuleNotFoundError: gspread**
- Solution: Ensure venv is created and activated: `./build.sh` handles this

**"No module named pip" in container**
- Solution: Fixed by installing dependencies in Docker container (see obsidian-scripts/run-daily-note.sh)

**Python version mismatch**
- Solution: Use pyenv to match container's Python version (3.13.2)

**Credentials not found**
- Ensure `concrete-spider-446700-f9-4646496845d1.json` exists in repo root
- Check file permissions (should be readable)

### Debugging Steps

```bash
# Test Google Sheets connection
cd ~/repos/albumdujour
./venv/bin/python3 -c "
import gspread
from pathlib import Path
gc = gspread.service_account(filename='concrete-spider-446700-f9-4646496845d1.json')
sheet = gc.open('2025-media').get_worksheet(0)
print(f'Connected! Found {len(sheet.get_all_records())} records')
"

# Test build only (no git)
./build.sh

# Verify build output
grep "Currently Listening" build/index.html
grep "Volcano" build/index.html
```

## Recent Changes (2026-04-13)

### Fixed Docker Execution (obsidian-scripts)

- Changed from copying host venv to installing dependencies in container
- Uses Docker's Python 3.13 directly
- Installs pip via get-pip.py (ensurepip not available in container)
- More robust against Python version mismatches

### Added Pre-flight Sync Script

- Created `bin/sync-python-version.sh` in obsidian-scripts
- Compares host venv Python version with container
- Can recreate venv if versions drift

---

For more details, see:
- [README.md](../README.md) - User documentation
- [build.sh](../build.sh) - Build script source
- [deploy.sh](../deploy.sh) - Deployment script source
- [build_music_site.py](../build_music_site.py) - Python build logic