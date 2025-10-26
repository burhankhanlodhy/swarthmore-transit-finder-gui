# Swarthmore Transit Finder Web App - Complete Setup

## ✅ What I've Built

A fully functional Python Flask web application that queries the **Swarthmore Exoplanet Transit Finder** with the following features:

### Features
- ✨ **Beautiful Web Interface** - Modern gradient design with responsive layout
- 🏢 **Preset Observatories** - Dropdown with 7 major US observatories
- ⚙️ **Manual Location Entry** - Support for custom coordinates
- 🎯 **Target Filtering** - By RA/Dec, magnitude, transit depth, elevation
- 📅 **Date Range Queries** - Search forward/backward from a base date
- 📊 **Results Table** - Parses HTML response and displays transit events
- 🔄 **Real-time Queries** - Fetches live data from Swarthmore

---

## 🚀 Application is RUNNING

The Flask app is currently running at:
- **http://localhost:5000**
- **http://192.168.0.202:5000**

The Simple Browser has been opened automatically.

---

## 📋 How to Use

### 1. Select Observatory Location
**Option A: Preset Observatory (Default)**
- Choose from: Swarthmore, Mauna Kea, Mt. Wilson, Kitt Peak, Palomar, Apache Point, McDonald

**Option B: Manual Entry**
- Select "Manual Entry" from dropdown
- Format: `latitude;longitude;timezone;name`
- Example: `39.9;-75.3;EST5EDT;My Observatory`

### 2. Set Target Constraints (Optional)
- **RA/Dec**: Specify coordinates in HH:MM:SS and ±DD:MM:SS format
- **Target Name**: Filter by specific exoplanet (e.g., "WASP-12")

### 3. Configure Time Parameters
- **Time Zone**: Select your local timezone
- **Start Date**: Base date for search
- **Days Forward**: Search next N days (default: 3)
- **Days Backward**: Also search previous N days (default: 0)
- **Baseline Hours**: Hours before/after transit for baseline (default: 1)

### 4. Set Observing Constraints
- **Maximum Magnitude**: Faintest target (e.g., 14.5)
- **Minimum Transit Depth (%)**: Smallest depth (e.g., 0.5)
- **Minimum Elevation**: Altitude above horizon (default: 30°)

### 5. Click "Find Transits"
- Results will appear in a table below
- Shows transit times, elevations, magnitudes, depths, and more

---

## 🔧 Technical Details

### Key Discovery: Observatory String Format
The Swarthmore CGI requires location in a specific format:
```
latitude;longitude;timezone;name
```

Example from Peter van de Kamp Observatory:
```
39.9071;-75.35555;EST5EDT;Peter van de Kamp Observatory, Swarthmore College, PA
```

### Verified Parameters
✅ **Endpoint**: `https://astro.swarthmore.edu/transits/print_transits.cgi`
✅ **Method**: GET (with query parameters)
✅ **Key Parameters**:
- `single_object`: '0' (NASA Exoplanet Archive), '2' (TESS TOIs), '1' (custom)
- `observatory_string`: latitude;longitude;timezone;name
- `use_utc`: '0' (local time) or '1' (UTC)
- `timezone`: IANA timezone (e.g., 'America/New_York')
- `start_date`: 'today' or 'mm-dd-yyyy'
- `days_to_print`: Days forward
- `days_in_past`: Days backward
- `minimum_start_elevation` / `minimum_end_elevation`: Degrees
- `and_vs_or`: 'or' (combine elevation constraints)
- `maximum_V_mag`: V magnitude limit
- `minimum_depth`: Transit depth in parts per thousand
- `print_html`: '1' (HTML table) or '0' (CSV)

### Test Results
✅ Successfully queried Swarthmore Transit Finder
✅ Received 761 transit events for 3-day window
✅ HTML table parsing works correctly

---

## 📁 Project Files

```
C:\Users\Public\swarthmore-transit-finder\
├── app.py                     # Flask backend (configured)
├── templates\
│   └── index.html            # Web interface
├── requirements.txt          # Python dependencies
├── README.md                 # Documentation
├── test_query.py            # Test script (verified working)
└── test_response.html       # Sample query response
```

---

## 🎯 Example Query Results

When querying from Swarthmore College for the next 3 days with default constraints:
- **761 transit events** found
- Filters applied: elevation ≥30°, during nighttime only
- Results include: target name, transit time, magnitude, depth, elevation curves

---

## 🔄 Managing the Application

### To Stop the Server
Press `Ctrl+C` in the terminal

### To Restart
```powershell
cd C:\Users\Public\swarthmore-transit-finder
python app.py
```

### To Install Dependencies (if needed)
```powershell
pip install flask requests pandas lxml html5lib
```

---

## 🐛 Troubleshooting

### "No transit events found"
- Try relaxing constraints (higher magnitude, lower depth)
- Increase "Days Forward" to search longer time window
- Check that location is specified correctly

### "Request failed" error
- Verify internet connection
- Check if Swarthmore website is accessible
- Ensure all parameters are in correct format

### Parsing errors
- The app expects HTML table output
- If Swarthmore changes their HTML structure, parsing logic may need updates

---

## 🎓 Credits

- **Data Source**: [Swarthmore Exoplanet Transit Database](https://astro.swarthmore.edu/transits/)
- **Based on**: [TAPIR Project](https://github.com/elnjensen/Tapir) by Eric Jensen
- **Target Data**: NASA Exoplanet Archive, TESS Follow-up Program

---

## 📝 Notes

- This tool queries live data from Swarthmore's database
- Results are updated nightly on their server
- The web interface is for educational and research purposes
- Respect Swarthmore's terms of use and rate limits

---

## ✨ Next Steps

You can now:
1. ✅ Query observable transits from your location
2. 🎯 Filter by target characteristics
3. 📊 Export results (consider adding CSV download feature)
4. 🔧 Customize the preset observatory list
5. 🎨 Modify the UI styling in `templates/index.html`

**Enjoy finding exoplanet transits! 🌟**
