# Website Content Tracker

A Python-based system for monitoring website content changes and receiving email notifications via Gmail.

## Features

- Track content changes on multiple websites (20-100 sites)
- Focus on text content monitoring using CSS selectors
- Email notifications for detected changes
- Rate limiting and efficient resource usage
- GitHub Actions automation for regular monitoring
- Historical change tracking
- Configurable monitoring frequency and thresholds

## Setup

### Option 1: Using pip

1. Clone the repository:
```bash
git clone https://github.com/yourusername/website_tracker.git
cd website_tracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Option 2: Using Mamba/Conda

1. Clone the repository:
```bash
git clone https://github.com/yourusername/website_tracker.git
cd website_tracker
```

2. Create and activate environment:
```bash
mamba env create -f environment.yml  # or use: conda env create -f environment.yml
mamba activate website-tracker       # or use: conda activate website-tracker
```

### Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)

2. Create a new project:
   - Click the project dropdown at the top
   - Click "New Project"
   - Enter a name and click "Create"

3. Enable the Gmail API:
   - Select your project
   - Click "Enable APIs and Services"
   - Search for "Gmail API"
   - Click "Enable"

4. Configure OAuth consent screen:
   - In left sidebar, go to "APIs & Services" > "OAuth consent screen"
   - Choose "External" user type
   - Fill in required fields:
     * App name
     * User support email
     * Developer contact email
   - Click "Save and Continue"
   - Under "Test users", click "Add Users"
   - Add your Gmail address
   - Click "Save"

5. Create OAuth 2.0 credentials:
   - Go to "Credentials" in left sidebar
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Web application"
   - Name: "Website Tracker"
   - Under "Authorized redirect URIs":
     * Click "Add URI"
     * Add EXACTLY: `http://localhost:8080`
     * No trailing slash, no other variations
   - Click "Create"
   - Download the client secrets JSON file
   - Move the file to your project's config directory

6. Get the refresh token using our helper script:
```bash
# First ensure you're in your virtual environment
pip install -r requirements.txt  # or use your conda env

# Run the helper script
python scripts/get_gmail_token.py

# When prompted:
# 1. Enter the path to your downloaded client secrets file
# 2. A browser window will open for Gmail authorization
# 3. Login with your Gmail account
# 4. Grant access to the application
# 5. The script will display your credentials
```

### Troubleshooting Gmail Setup

If you see "redirect_uri_mismatch" error:
1. Go back to Google Cloud Console > Credentials
2. Edit your OAuth 2.0 Client ID
3. Ensure the redirect URI is EXACTLY: `http://localhost:8080`
4. Remove any other redirect URIs
5. Save and try again

If you see "invalid_client" error:
1. Make sure you downloaded the Web application credentials
2. The client secrets file should contain a "web" section
3. Try downloading the credentials file again

### GitHub Repository Setup

1. Go to your GitHub repository settings
2. Navigate to "Secrets and variables" > "Actions"
3. Add these secrets (using values from the helper script):
   - `GMAIL_CLIENT_ID`
   - `GMAIL_CLIENT_SECRET`
   - `GMAIL_REFRESH_TOKEN`
   - `GMAIL_FROM_EMAIL` (your Gmail address)

### Website Configuration

Create or modify `config/websites.yml`:
```yaml
websites:
  - name: "Example Jobs"
    url: "https://example.com/jobs"
    frequency: "hourly"
    content:
      selectors:
        - ".job-listing"
        - ".vacancy-info"
      exclude:
        - ".advertisement"
    notification:
      threshold: 
        added: 1
        removed: 1
        changed: 0.3
      email:
        to: ["your-email@example.com"]

email:
  service: "gmail"
  credentials:
    client_id: "${GMAIL_CLIENT_ID}"
    client_secret: "${GMAIL_CLIENT_SECRET}"
    refresh_token: "${GMAIL_REFRESH_TOKEN}"
  from: "${GMAIL_FROM_EMAIL}"
  batch_interval: 3600
  rate_limit:
    max_emails: 50
    period: 3600
```

## Usage

### Manual Run

```bash
python -m src
```

### GitHub Actions

The tracker runs automatically:
- Every 6 hours
- On push to main branch (affecting src/, config/, or workflow files)
- Manually via GitHub Actions interface

## Configuration

### Website Configuration

- `name`: Unique identifier for the website
- `url`: Website URL to monitor
- `frequency`: Monitoring frequency (hourly, daily, weekly)
- `content`:
  - `selectors`: CSS selectors to extract content
  - `exclude`: CSS selectors to ignore
- `notification`:
  - `threshold`: Change detection thresholds
  - `email`: Notification recipients

### Email Configuration

- `service`: Email service (currently only gmail)
- `credentials`: Gmail API credentials
- `batch_interval`: Time between notifications
- `rate_limit`: Email sending limits

## Directory Structure

```
website_tracker/
├── src/
│   ├── monitor/
│   │   ├── content_fetcher.py
│   │   ├── rate_limiter.py
│   │   └── website_monitor.py
│   └── utils/
│       ├── config.py
│       └── logger.py
├── scripts/
│   └── get_gmail_token.py
├── config/
│   └── websites.yml
├── data/           # Website content history
├── logs/           # Application logs
└── .github/
    └── workflows/
        └── monitor.yml
```

## Logs and Data

- Logs are stored in `logs/` directory
- Website content history in `data/` directory
- GitHub Actions artifacts contain logs for 7 days

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Adding New Features

1. Add new functionality in appropriate module
2. Update configuration schema if needed
3. Add tests for new features
4. Test manually before committing

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.