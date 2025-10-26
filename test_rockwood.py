"""
Test different parameter combinations to find what works
"""
import requests

def test_rockwood():
    """Test Rockwood Observatory query"""
    base_url = "https://astro.swarthmore.edu/transits/print_transits.cgi"
    
    # Try the exact format that worked before
    params = {
        'single_object': '0',
        'observatory_string': '31.55;-99.383333;CST6CDT;Rockwood Observatory, TX',
        'use_utc': '0',
        'start_date': 'today',  # Try 'today' instead of specific date
        'days_to_print': '1',
        'days_in_past': '0',
        'minimum_start_elevation': '30',
        'minimum_end_elevation': '30',
        'and_vs_or': 'or',
        'baseline_hrs': '1',
        'show_unc': '1',
        'print_html': '1',
        'twilight': '-12',
        'max_airmass': '2.4',
    }
    
    print("Test 1: Minimal parameters with 'today'")
    print(f"Parameters: {params}\n")
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Success! Response length: {len(response.text)} characters")
            if '<table' in response.text.lower():
                row_count = response.text.lower().count('<tr')
                print(f"✅ Found table with ~{row_count} rows")
            with open('test_rockwood.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("✅ Saved to test_rockwood.html")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text[:500])
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Try with minimum_depth and maximum_V_mag
    params2 = params.copy()
    params2['minimum_depth'] = '2'
    params2['maximum_V_mag'] = '12'
    
    print("Test 2: With magnitude and depth filters")
    print(f"Added: minimum_depth=2, maximum_V_mag=12\n")
    
    try:
        response = requests.get(base_url, params=params2, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Success with filters!")
        else:
            print(f"❌ Failed with filters")
            print(response.text[:500])
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == '__main__':
    test_rockwood()
