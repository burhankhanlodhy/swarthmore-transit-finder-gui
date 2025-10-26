"""
Swarthmore Transit Finder Web Interface
A Flask web app to query observable exoplanet transits
"""
from flask import Flask, render_template, request, jsonify
from typing import Dict, Any, Optional, Tuple, List
import requests
import pandas as pd
from datetime import datetime
import sys
import os
import math

app = Flask(__name__)

# Precession constants (approximate values for simplified conversion)
# Note: For precise calculations, astropy library is recommended
PRECESSION_RA_MEAN = 3.075  # seconds of time per year (mean precession)
PRECESSION_RA_CORRECTION = 1.336  # correction factor for declination
PRECESSION_DEC_RATE = 20.0  # arcseconds per year (approximate)
JULIAN_YEAR_DAYS = 365.25  # Days in a Julian year

def j2000_to_jnow(ra_j2000_str: str, dec_j2000_str: str) -> Tuple[str, str]:
    """
    Convert J2000 coordinates to JNow (current epoch)
    
    Uses astropy for accurate coordinate conversion following IAU standards.
    If astropy is not available, falls back to simplified approximation.
    
    Args:
        ra_j2000_str: RA in format "HH:MM:SS.SS"
        dec_j2000_str: Dec in format "+DD:MM:SS.S" or "-DD:MM:SS.S"
    
    Returns:
        Tuple of (ra_jnow_str, dec_jnow_str)
    """
    try:
        # Try using astropy for accurate conversion
        try:
            from astropy.coordinates import SkyCoord
            from astropy.time import Time
            import astropy.units as u
            
            # Parse J2000 coordinates
            coord_j2000 = SkyCoord(
                ra=ra_j2000_str, 
                dec=dec_j2000_str, 
                unit=(u.hourangle, u.deg),
                frame='icrs',
                obstime='J2000'
            )
            
            # Convert to current epoch (FK5 at current time)
            current_time = Time.now()
            coord_jnow = coord_j2000.transform_to('fk5')
            coord_jnow.obstime = current_time
            
            # Format back to strings
            ra_jnow_str = coord_jnow.ra.to_string(unit=u.hour, sep=':', precision=2, pad=True)
            dec_jnow_str = coord_jnow.dec.to_string(unit=u.deg, sep=':', precision=1, pad=True, alwayssign=True)
            
            print(f"✓ Astropy conversion: {ra_j2000_str} {dec_j2000_str} → {ra_jnow_str} {dec_jnow_str}")
            return ra_jnow_str, dec_jnow_str
            
        except ImportError:
            print("⚠ Astropy not available, using simplified precession approximation")
            # Fall back to simplified calculation
            pass
        
        # Simplified precession calculation (fallback)
        # Parse RA (hours:minutes:seconds to degrees)
        ra_parts = ra_j2000_str.strip().split(':')
        ra_hours = float(ra_parts[0])
        ra_mins = float(ra_parts[1]) if len(ra_parts) > 1 else 0
        ra_secs = float(ra_parts[2]) if len(ra_parts) > 2 else 0
        ra_j2000_deg = (ra_hours + ra_mins/60 + ra_secs/3600) * 15  # Convert hours to degrees
        
        # Parse Dec (degrees:arcminutes:arcseconds)
        dec_str = dec_j2000_str.strip()
        sign = -1 if dec_str[0] == '-' else 1
        dec_parts = dec_str.lstrip('+-').split(':')
        dec_deg = abs(float(dec_parts[0]))
        dec_arcmin = float(dec_parts[1]) if len(dec_parts) > 1 else 0
        dec_arcsec = float(dec_parts[2]) if len(dec_parts) > 2 else 0
        dec_j2000_deg = sign * (dec_deg + dec_arcmin/60 + dec_arcsec/3600)
        
        # Calculate years since J2000.0 (2000-01-01 12:00 TT)
        now = datetime.now()
        j2000_date = datetime(2000, 1, 1, 12, 0, 0)
        years_since_j2000 = (now - j2000_date).days / JULIAN_YEAR_DAYS
        
        # Simplified precession approximation
        # Mean precession rates (rough approximation)
        
        # RA precession: approximately 3.075 + 1.336*sin(α)*tan(δ) seconds of time per year
        ra_correction_sec = (PRECESSION_RA_MEAN + 
                            PRECESSION_RA_CORRECTION * math.sin(math.radians(ra_j2000_deg)) * 
                            math.tan(math.radians(dec_j2000_deg))) * years_since_j2000
        ra_jnow_deg = ra_j2000_deg + (ra_correction_sec / 3600) * 15  # Convert seconds to degrees
        
        # Dec precession: approximately 20 arcsec per year
        dec_correction_arcsec = PRECESSION_DEC_RATE * years_since_j2000 * math.cos(math.radians(ra_j2000_deg))
        dec_jnow_deg = dec_j2000_deg + (dec_correction_arcsec / 3600)
        
        # Normalize RA to 0-360 range
        ra_jnow_deg = ra_jnow_deg % 360
        
        # Convert back to HMS and DMS format
        ra_jnow_hours = ra_jnow_deg / 15
        ra_h = int(ra_jnow_hours)
        ra_m = int((ra_jnow_hours - ra_h) * 60)
        ra_s = ((ra_jnow_hours - ra_h) * 60 - ra_m) * 60
        ra_jnow_str = f"{ra_h:02d}:{ra_m:02d}:{ra_s:05.2f}"
        
        dec_sign = '+' if dec_jnow_deg >= 0 else '-'
        dec_abs = abs(dec_jnow_deg)
        dec_d = int(dec_abs)
        dec_m = int((dec_abs - dec_d) * 60)
        dec_s = ((dec_abs - dec_d) * 60 - dec_m) * 60
        dec_jnow_str = f"{dec_sign}{dec_d:02d}:{dec_m:02d}:{dec_s:04.1f}"
        
        print(f"✓ Simplified conversion: {ra_j2000_str} {dec_j2000_str} → {ra_jnow_str} {dec_jnow_str}")
        return ra_jnow_str, dec_jnow_str
        
    except Exception as e:
        print(f"✗ Conversion error: {e}")
        # If conversion fails, return original values
        return ra_j2000_str, dec_j2000_str

def parse_swarthmore_response(html_content: str) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    """
    Parse the HTML response from Swarthmore Transit Finder
    
    Args:
        html_content: HTML response from Swarthmore CGI
        
    Returns:
        Tuple of (results_list, error_message)
        - results_list: List of dictionaries with transit data, or None if error
        - error_message: Error description string, or None if successful
    """
    try:
        # Extract tables from HTML
        tables = pd.read_html(html_content)
        if not tables:
            return None, "No transit events found for the specified criteria."
        
        # The main results table is typically the first or second table
        # You may need to adjust this based on actual response structure
        df = tables[0] if len(tables) > 0 else None
        
        if df is not None and not df.empty:
            # Convert DataFrame to list of dictionaries for JSON serialization
            results = df.to_dict('records')
            
            # Clean up the Name column - remove extra text after planet name
            for row in results:
                # Look for Name column and clean it
                for key in list(row.keys()):
                    if 'name' in key.lower() and row[key]:
                        name_value = str(row[key])
                        # Extract just the planet name (before "Finding charts:")
                        if 'Finding charts:' in name_value:
                            row[key] = name_value.split('Finding charts:')[0].strip()
                        elif 'Info:' in name_value:
                            row[key] = name_value.split('Info:')[0].strip()
                        # Also remove any HTML/markdown links
                        if '[' in name_value:
                            row[key] = name_value.split('[')[0].strip()
                    
                    # Parse and clean up transit time format
                    if 'start' in key.lower() and 'mid' in key.lower() and 'end' in key.lower():
                        time_value = str(row[key])
                        # Format: "00:02 01:02— 02:36 —04:09 05:10 ±0:00"
                        # Parse: baseline_start ingress— mid —egress baseline_end ±uncertainty
                        if '—' in time_value and ':' in time_value:
                            parts = time_value.replace('±', '').split()
                            if len(parts) >= 5:
                                try:
                                    baseline_start = parts[0]
                                    ingress = parts[1].replace('—', '')
                                    mid = parts[2]
                                    egress = parts[3].replace('—', '')
                                    baseline_end = parts[4]
                                    
                                    # Create readable format (additional columns for Best Transit)
                                    row['Baseline Start'] = baseline_start
                                    row['Transit Ingress'] = ingress
                                    row['Mid-Transit'] = mid
                                    row['Transit Egress'] = egress
                                    row['Baseline End'] = baseline_end
                                    
                                    # Keep original column for table display
                                except:
                                    pass
                    
                    # Parse observability percentage format
                    if '% of transit' in key.lower() and row[key]:
                        obs_value = str(row[key])
                        # Format: "100% (100%) 22:53—03:28"
                        if '%' in obs_value:
                            try:
                                parts = obs_value.split()
                                if len(parts) >= 1:
                                    visibility = parts[0]  # e.g., "100%"
                                    row['Transit Visibility'] = visibility
                                    if len(parts) >= 3 and '—' in parts[2]:
                                        time_range = parts[2]
                                        start_end = time_range.split('—')
                                        if len(start_end) == 2:
                                            row['Observation Start'] = start_end[0]
                                            row['Observation End'] = start_end[1]
                                    # Keep original column for table display
                            except:
                                pass
                    
                    # Clean up elevation format
                    if 'elev' in key.lower() and 'start' in key.lower() and row[key]:
                        elev_value = str(row[key])
                        # Format: "75° 82°, 72°, 58° 46°"
                        if '°' in elev_value:
                            try:
                                parts = elev_value.replace('°', '').replace(',', '').split()
                                if len(parts) >= 5:
                                    row['Elev @ Baseline Start'] = f"{parts[0]}°"
                                    row['Elev @ Ingress'] = f"{parts[1]}°"
                                    row['Elev @ Mid-Transit'] = f"{parts[2]}°"
                                    row['Elev @ Egress'] = f"{parts[3]}°"
                                    row['Elev @ Baseline End'] = f"{parts[4]}°"
                                    # Keep original column for table display
                            except:
                                pass
            
            # Add JNow coordinates if J2000 coordinates exist
            for row in results:
                # Look for combined "RA & Dec (J2000)" column or separate columns
                coord_str = None
                coord_key = None
                
                for key in row.keys():
                    key_lower = key.lower()
                    # Match "RA & Dec (J2000)" combined format
                    if 'ra' in key_lower and 'dec' in key_lower and 'j2000' in key_lower:
                        coord_key = key
                        coord_str = str(row[key])
                        break
                
                # Parse and convert coordinates
                if coord_str and ':' in coord_str:
                    # Format is typically: "HH:MM:SS.SS +DD:MM:SS.SS"
                    parts = coord_str.strip().split()
                    if len(parts) >= 2:
                        ra_j2000 = parts[0]
                        dec_j2000 = parts[1]
                        
                        # Convert to JNow
                        ra_jnow, dec_jnow = j2000_to_jnow(ra_j2000, dec_j2000)
                        
                        # Add JNow columns
                        row['RA (JNow)'] = ra_jnow
                        row['Dec (JNow)'] = dec_jnow
                        row['RA & Dec (JNow)'] = f"{ra_jnow} {dec_jnow}"
            
            return results, None
        else:
            return None, "No transit events found."
    except Exception as e:
        return None, f"Error parsing response: {str(e)}"

def query_swarthmore(params: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    """
    Send query to Swarthmore Transit Finder
    
    Form fields discovered from https://astro.swarthmore.edu/transits/
    Submits to: print_transits.cgi
    
    Args:
        params: Dictionary of query parameters
        
    Returns:
        Tuple of (html_response, error_message)
    """
    # Base URL - using the actual CGI endpoint
    base_url = "https://astro.swarthmore.edu/transits/print_transits.cgi"
    
    # Build the query parameters using actual form field names
    # Key fix: Don't send 'timezone' param when using observatory_string (it contains timezone)
    query_params = {
        # Target selection (default to NASA Exoplanet Archive)
        'single_object': params.get('single_object', '0'),  # 0 = use target list
        
        # For single object queries (if enabled)
        'target': params.get('target_name', ''),
        'ra': params.get('ra', ''),
        'dec': params.get('dec', ''),
        
        # Observatory location (includes timezone in the string)
        'observatory_string': params.get('location', ''),
        'use_utc': '0',  # 0 = use local time, 1 = use UTC
        # NOTE: Don't send 'timezone' separately - it's in observatory_string
        
        # Date window
        'start_date': params.get('date', 'today'),
        'days_to_print': params.get('days_forward', '1'),  # Days forward
        'days_in_past': params.get('days_back', '0'),  # Days backward
        
        # Elevation constraints
        'minimum_start_elevation': params.get('min_elevation', '30'),
        'minimum_end_elevation': params.get('min_elevation', '30'),
        'and_vs_or': 'or',  # Combine elevation constraints with OR (default)
        
        # Hour angle constraints (optional, ±12 = no constraint)
        'minimum_ha': params.get('min_ha', '-12'),
        'maximum_ha': params.get('max_ha', '12'),
        
        # Baseline observation time
        'baseline_hrs': params.get('baseline_hrs', '1'),  # Hours before/after for baseline
        'show_unc': '1',  # Show uncertainties
        
        # Space observing (ignore elevation/day-night if 1)
        'space': params.get('space', '0'),
        
        # Target constraints
        'minimum_depth': params.get('depth_min', ''),  # In parts per thousand (ppt)
        'maximum_V_mag': params.get('mag_max', ''),  # Maximum V magnitude
        'target_string': params.get('target_string', ''),  # Name filter
        
        # Output format
        'print_html': '1',  # 1 = HTML table, 0 = CSV
        'twilight': '-12',  # Sun altitude for day/night definition (astronomical twilight)
        'max_airmass': params.get('max_airmass', '2.4'),  # For airmass plots
        
        # Aladin finder chart FOV settings
        'showFov': '0',  # Show detector outline
        'fovWidth': '',
        'fovHeight': '',
        'fovPA': '',
    }
    
    # Remove empty parameters
    query_params = {k: v for k, v in query_params.items() if v != ''}
    
    try:
        print(f"Querying: {base_url}")
        print(f"Parameters: {query_params}")
        response = requests.get(base_url, params=query_params, timeout=30)
        print(f"Status Code: {response.status_code}")
        response.raise_for_status()
        return response.text, None
    except requests.RequestException as e:
        return None, f"Request failed: {str(e)}"

@app.route('/')
def index():
    """Render the main form page"""
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    """Handle form submission and query Swarthmore"""
    try:
        # Hardcoded location - Rockwood Observatory
        observatory_string = '31.55;-99.383333;CST6CDT;Rockwood Observatory, TX'
        
        # Convert date from yyyy-mm-dd to mm-dd-yyyy format (or use 'today')
        date_input = request.form.get('date', '')
        if date_input:
            try:
                # Parse yyyy-mm-dd format from HTML date input
                date_obj = datetime.strptime(date_input, '%Y-%m-%d')
                # Convert to mm-dd-yyyy format Swarthmore expects
                formatted_date = date_obj.strftime('%m-%d-%Y')
            except:
                formatted_date = 'today'
        else:
            formatted_date = 'today'
        
        params = {
            'location': observatory_string,
            'ra': request.form.get('ra', ''),
            'dec': request.form.get('dec', ''),
            # Don't send timezone separately - it's in observatory_string
            'date': formatted_date,
            'days_forward': request.form.get('days_forward', '3'),
            'days_back': request.form.get('days_back', '0'),
            'mag_max': request.form.get('mag_max', ''),
            'depth_min': request.form.get('depth_min', ''),
            'min_elevation': request.form.get('min_elevation', '30'),
            'target_name': request.form.get('target_name', ''),
            'target_string': request.form.get('target_string', ''),
            'single_object': request.form.get('single_object', '0'),
            'baseline_hrs': request.form.get('baseline_hrs', '1'),
        }
        
        # Query Swarthmore
        html_response, error = query_swarthmore(params)
        
        if error:
            return jsonify({'success': False, 'error': error}), 400
        
        # Parse response
        results, parse_error = parse_swarthmore_response(html_response)
        
        if parse_error:
            return jsonify({'success': False, 'error': parse_error}), 400
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results) if results else 0
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/timezones')
def get_timezones():
    """Return list of common timezones"""
    common_timezones = [
        'America/New_York',
        'America/Chicago',
        'America/Denver',
        'America/Los_Angeles',
        'America/Phoenix',
        'America/Anchorage',
        'Pacific/Honolulu',
        'Europe/London',
        'Europe/Paris',
        'Europe/Berlin',
        'Asia/Tokyo',
        'Asia/Shanghai',
        'Australia/Sydney',
        'UTC',
    ]
    return jsonify(common_timezones)

if __name__ == '__main__':
    # Use environment variable for debug mode (default: False for security)
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Bind to localhost only for security (use 0.0.0.0 only if needed)
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', '5000'))
    
    print(f"Starting Flask app on {host}:{port} (debug={debug_mode})")
    app.run(debug=debug_mode, host=host, port=port)
