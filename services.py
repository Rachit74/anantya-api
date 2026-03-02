
# Temporary list for testing
id_list = [
    'AF-DL-001',
]

existing_ids = set(id_list)

# aliases map for AF-XXX-XXX format id, move to file later
city_aliases_map = {
    # Metro Cities
    'delhi': 'DEL',
    'new delhi': 'DEL',
    'mumbai': 'BOM',
    'bombay': 'BOM',
    'kolkata': 'CCU',
    'calcutta': 'CCU',
    'chennai': 'MAA',
    'madras': 'MAA',
    'bengaluru': 'BLR',
    'bangalore': 'BLR',
    'hyderabad': 'HYD',
    'ahmedabad': 'AMD',
    'pune': 'PUN',
    'jaipur': 'JAI',
    'lucknow': 'LKO',
    'kanpur': 'KNP',
    'nagpur': 'NAG',
    'indore': 'IDR',
    'bhopal': 'BHO',
    'visakhapatnam': 'VTZ',
    'vizag': 'VTZ',
    'patna': 'PAT',
    'vadodara': 'BDQ',
    'baroda': 'BDQ',
    'ludhiana': 'LUH',
    'agra': 'AGR',
    'nashik': 'ISK',
    'surat': 'STV',
    'ranchi': 'IXR',
    'raipur': 'RPR',
    'chandigarh': 'IXC',
    'coimbatore': 'CJB',
    'madurai': 'IXM',
    'varanasi': 'VNS',
    'meerut': 'MRT',
    'rajkot': 'RAJ',
    'jodhpur': 'JDH',
    'amritsar': 'ATQ',
    'allahabad': 'PRY',
    'prayagraj': 'PRY',
    'gwalior': 'GWL',
    'vijayawada': 'VGA',
    'guwahati': 'GAU',
    'mysuru': 'MYQ',
    'mysore': 'MYQ',
    'tiruchirappalli': 'TRZ',
    'trichy': 'TRZ',
    'kochi': 'COK',
    'cochin': 'COK',
    'thiruvananthapuram': 'TRV',
    'trivandrum': 'TRV',
    'mangaluru': 'IXE',
    'mangalore': 'IXE',
    'bhubaneswar': 'BBI',
    'dehradun': 'DED',
    'jamshedpur': 'IXW',
    'shimla': 'SLV',
    'srinagar': 'SXR',
    'aurangabad': 'IXU',
    'udaipur': 'UDR',
    'dibrugarh': 'DIB',
    'imphal': 'IMF',
    'agra': 'AGR',
    'aizawl': 'AJL',
    'itanagar': 'HGI',
    'panaji': 'GOI',
    'goa': 'GOI',
    'silchar': 'IXS',
    'gangtok': 'PYG',
    'tirupati': 'TIR',
    'hubli': 'HBX',
    'dharwad': 'HBX',
    'belagavi': 'IXG',
    'belgaum': 'IXG',
    'kolhapur': 'KLH',
    'salem': 'SXV',
    'warangal': 'WGC',
    'noida': 'NOI',
    'gurgaon': 'GGN',
    'gurugram': 'GGN',
    'faridabad': 'FBD'
}

city_counter_map = {}

"""
gen_af_id -> generate anantya foundation id
will generate unique id specific to anantya foundation
will make sure no id dublication
"""
def gen_af_id(city: str):
    """
    city: str -> format is of type -> City, Localit or City
    we get city out of the proper input, eg:- Delhi
    then do Delhi.tolower() and get the alise of of that map
    generate an id like AF-DEL-001
    check if id list contains that id, if yes then increase the number by 1, so AF-DEL-002
    """
    if not city or not isinstance(city, str):
        raise ValueError("Invalid city input")
    
    # extract city name
    city_name = city.split(",")[0].strip().lower()

    # get aliase code
    if city_name not in city_aliases_map:
        city_code = 'XXX'

    city_code = city_aliases_map[city_name]

    # init counter if not present
    if city_code not in city_counter_map:
        # Find max existing sequence for this city
        max_seq = 0
        prefix = f"AF-{city_code}-"

        for existing_id in existing_ids:
            if existing_id.startswith(prefix):
                seq = int(existing_id.split("-")[-1])
                max_seq = max(max_seq, seq)

        city_counter_map[city_code] = max_seq

    # Step 4: Generate next ID
    while True:
        city_counter_map[city_code] += 1
        new_id = f"AF-{city_code}-{city_counter_map[city_code]:03d}"

        if new_id not in existing_ids:
            existing_ids.add(new_id)
            return new_id


