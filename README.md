# Swarthmore Transit Finder Web Interface

A Python Flask web application to query the Swarthmore Exoplanet Transit Database for observable transit events.

## Features

- 🌐 Clean web interface for inputting observing parameters
- 📍 Location-based queries (observatory name or coordinates)
- 🕒 Time zone support with date and time range selection
- 🎯 Target constraints (RA/Dec, magnitude, transit depth)
- 📊 Results displayed in an interactive table
- ⚡ Real-time querying of Swarthmore Transit Finder

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Steps

1. **Navigate to the project directory:**
   ```powershell
   cd C:\Users\Public\swarthmore-transit-finder
   ```

2. **Create a virtual environment:**
   ```powershell
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   If you get an execution policy error, run:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **Install required packages:**
   ```powershell
   pip install -r requirements.txt
   ```

## Configuration

✅ **CONFIGURED:** The application is now configured with the correct Swarthmore Transit Finder parameters!

The form fields have been mapped to the actual CGI parameters:
- **Endpoint:** `https://astro.swarthmore.edu/transits/print_transits.cgi`
- **Parameters:** All form fields now use the correct names from the Swarthmore form

The application is ready to use without further configuration.

## Usage

1. **Start the Flask application:**
   ```powershell
   python app.py
   ```

2. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

3. **Fill in the form:**
   - **Observing Location:** Enter your observatory name or coordinates
   - **Target Constraints:** Optionally specify RA/Dec or target name
   - **Time Parameters:** Select timezone, date, and time range
   - **Observing Constraints:** Set magnitude and transit depth limits

4. **Click "Find Transits"** to query the database

5. **View Results:** Transit events will be displayed in a table below the form

## Form Parameters

### Location
- **Observatory Name or Coordinates:** e.g., "Swarthmore, PA" or "39.9N 75.3W 50m"

### Target Constraints (Optional)
- **RA (Right Ascension):** Format HH:MM:SS (e.g., "12:34:56")
- **Dec (Declination):** Format ±DD:MM:SS (e.g., "+12:34:56")
- **Target Name:** Specific exoplanet system (e.g., "WASP-12")

### Time Parameters
- **Time Zone:** Select from common time zones
- **Start Date:** Base date for transit search
- **Days Forward:** Number of days to search forward (default: 3)
- **Days Backward:** Number of days to also search backward (default: 0)
- **Baseline Hours:** Hours before/after transit for baseline observation (default: 1)

### Observing Constraints
- **Maximum Magnitude:** Faintest target to include (e.g., 14.5)
- **Minimum Transit Depth (%):** Smallest transit depth (e.g., 0.5)
- **Minimum Elevation:** Minimum altitude above horizon in degrees (default: 30)

## Troubleshooting

### Common Issues

1. **"No transit events found"**
   - Try relaxing your constraints (higher magnitude limit, lower depth threshold)
   - Check that your location is specified correctly
   - Verify the date and time range

2. **"Request failed" error**
   - Ensure you have internet connectivity
   - Verify the endpoint URL is correct in `app.py`
   - Check if the Swarthmore website is accessible

3. **Parsing errors**
   - The HTML structure may have changed
   - Update the `parse_swarthmore_response()` function to match current HTML structure

4. **Module not found errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt` again

## Development

To modify the application:

- **Backend logic:** Edit `app.py`
- **Frontend interface:** Edit `templates/index.html`
- **Dependencies:** Update `requirements.txt`

## API Endpoints

- `GET /` - Main web interface
- `POST /query` - Submit query and get results (returns JSON)
- `GET /api/timezones` - Get list of available timezones (returns JSON)

## Notes

- This is a web scraping tool that relies on the structure of the Swarthmore Transit Finder website
- If the website changes its structure, the parsing logic may need updates
- Consider implementing caching to reduce repeated queries
- The application runs in debug mode by default (disable for production use)

## Credits

- Data source: [Swarthmore Exoplanet Transit Database](https://astro.swarthmore.edu/transits/)
- Based on the [TAPIR project](https://github.com/elnjensen/Tapir) by Eric Jensen

## License

This tool is for educational and research purposes. Please respect the Swarthmore Transit Finder's terms of use.
