"""
Quick test script to verify Swarthmore Transit Finder query works
"""
import requests
from datetime import datetime

def test_query():
    """Test a simple query to Swarthmore"""
    base_url = "https://astro.swarthmore.edu/transits/print_transits.cgi"
    
    # Simple test parameters - looking for transits from Swarthmore
    # Observatory string format: latitude;longitude;timezone;name
    params = {
        'single_object': '0',  # 0 = NASA Exoplanet Archive
        'observatory_string': '39.9071;-75.35555;EST5EDT;Peter van de Kamp Observatory, Swarthmore College, PA',
        'use_utc': '0',
        'timezone': 'America/New_York',
        'start_date': 'today',
        'days_to_print': '3',
        'days_in_past': '0',
        'minimum_start_elevation': '30',
        'minimum_end_elevation': '30',
        'and_vs_or': 'or',  # lowercase 'or', not 'AND'
        'baseline_hrs': '1',
        'show_unc': '1',
        'print_html': '1',
        'twilight': '-12',
        'max_airmass': '2.4',
    }
    
    print("Testing Swarthmore Transit Finder query...")
    print(f"URL: {base_url}")
    print(f"Parameters: {params}\n")
    
    try:
        # Try POST with form data instead of GET with query params
        response = requests.post(base_url, data=params, timeout=30)
        response.raise_for_status()
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response Length: {len(response.text)} characters")
        
        # Check if we got HTML table results
        if '<table' in response.text.lower():
            print("✅ HTML table found in response")
            # Count how many rows (approximate)
            row_count = response.text.lower().count('<tr')
            print(f"✅ Approximate table rows: {row_count}")
        else:
            print("⚠️  No HTML table found - check response format")
        
        # Save response for inspection
        output_file = "test_response.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"\n✅ Full response saved to: {output_file}")
        print("   Open this file in a browser to see the results")
        
        return True
        
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == '__main__':
    test_query()
