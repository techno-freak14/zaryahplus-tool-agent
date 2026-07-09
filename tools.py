import datetime
import requests

# TOOL 1: Zakat Calculator
def calculate_zakat(savings: float, gold_grams: float, silver_grams: float = 0.0) -> str:
    """
    Calculates the Zakat owed based on cash savings, gold, and silver.
    Assumes standard Nisab values (approximate generic evaluation values).
    """
    # Approximate current market prices per gram 
    gold_price_per_gram = 80.0  
    silver_price_per_gram = 1.0   
    
    # Calculate total asset worth
    total_assets = savings + (gold_grams * gold_price_per_gram) + (silver_grams * silver_price_per_gram)
    
    # Nisab thresholds (Standard: 85g gold or 595g silver)
    gold_nisab_threshold = 85 * gold_price_per_gram
    
    if total_assets >= gold_nisab_threshold:
        zakat_owed = total_assets * 0.025  # 2.5% Zakat rate
        return f"Total assets calculated: ${total_assets:,.2f}. You are above the Nisab threshold (${gold_nisab_threshold:,.2f}). Total Zakat owed is: ${zakat_owed:,.2f}."
    else:
        return f"Total assets calculated: ${total_assets:,.2f}. This is below the Nisab threshold (${gold_nisab_threshold:,.2f}). No Zakat is due."

# TOOL 2: Prayer Times Lookup
def get_prayer_times(city: str, country: str = "") -> str:
    """
    Fetches the 5 daily prayer times for a specified city using a real public API.
    """
    try:
        url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country={country}"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return f"Error: Could not retrieve prayer times for '{city}'. Please verify the city name."
            
        data = response.json()
        timings = data['data']['timings']
        date_info = data['data']['date']['gregorian']['date']
        
        return (
            f"Prayer times for {city.title()} on {date_info}:\n"
            f"- Fajr: {timings['Fajr']}\n"
            f"- Dhuhr: {timings['Dhuhr']}\n"
            f"- Asr: {timings['Asr']}\n"
            f"- Maghrib: {timings['Maghrib']}\n"
            f"- Isha: {timings['Isha']}"
        )
    except Exception as e:
        return f"Failed to connect to the prayer times service: {str(e)}"

# TOOL 3: Date Converter (Hijri <-> Gregorian)
def convert_date(date_str: str, to_hijri: bool = True) -> str:
    """
    Converts dates between Gregorian and Hijri calendars using a real public API.
    Input format: 'DD-MM-YYYY'
    """
    try:
        # Validate format roughly
        parts = date_str.split('-')
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            return "Error: Invalid date format. Please use 'DD-MM-YYYY' (e.g., '25-12-2026')."

        # Corrected endpoints for the Aladhan API
        endpoint = "gToH" if to_hijri else "hToG"
        url = f"https://api.aladhan.com/v1/{endpoint}?date={date_str}"
        
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return f"Error: Failed to convert date. Check if the date provided is valid."
            
        data = response.json()
        
        if to_hijri:
            hijri = data['data']['hijri']
            return f"Gregorian date {date_str} converts to Hijri: {hijri['day']} {hijri['month']['en']} {hijri['year']} AH ({hijri['date']})."
        else:
            gregorian = data['data']['gregorian']
            return f"Hijri date {date_str} converts to Gregorian: {gregorian['day']} {gregorian['month']['en']} {gregorian['year']} AD ({gregorian['date']})."
            
    except Exception as e:
        return f"Failed to connect to the date conversion service: {str(e)}"

# TOOL 4: Quran Reference Lookup
def lookup_quran_verse(reference: str) -> str:
    """
    Retrieves a specific Quranic verse text and its source using its reference (e.g., '2:255' or '1:1').
    """
    try:
        # Expecting format 'surah:ayah'
        if ":" not in reference:
            return "Error: Please provide the reference in 'Surah:Ayah' format (e.g., '2:255')."
            
        url = f"https://api.alquran.cloud/v1/ayah/{reference}/editions/quran-uthmani,en.asad"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return f"Error: Could not find a verse matching reference '{reference}'. Please check the chapter and verse numbers."
            
        data = response.json()
        
        # The API returns an array of editions if requested this way
        editions = data['data']
        arabic_text = editions[0]['text']
        english_text = editions[1]['text']
        surah_name = editions[0]['surah']['englishName']
        surah_num = editions[0]['surah']['number']
        ayah_num = editions[0]['numberInSurah']
        
        return (
            f"Source: Holy Quran ({surah_name} {surah_num}:{ayah_num})\n"
            f"Arabic: {arabic_text}\n"
            f"English Translation: {english_text}"
        )
    except Exception as e:
        return f"Failed to connect to the Quran lookup service: {str(e)}"