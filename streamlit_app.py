import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
from io import StringIO

st.title("Evidence-Based Jet Lag Protocol Generator")
st.write("Generate personalized jet lag protocols based on circadian rhythm research")

# Direct flights only database (verified routes)
COMMON_FLIGHTS = {
    "US Domestic": {
        "New York (JFK) → Los Angeles (LAX)": {
            "dep_city": "New York", "dep_tz": "US/Eastern", "dest_city": "Los Angeles", "dest_tz": "US/Pacific",
            "duration": 6.5, "common_times": ["06:00", "08:00", "11:00", "14:00", "17:00", "20:00"]
        },
        "Los Angeles (LAX) → New York (JFK)": {
            "dep_city": "Los Angeles", "dep_tz": "US/Pacific", "dest_city": "New York", "dest_tz": "US/Eastern",
            "duration": 5.5, "common_times": ["07:00", "08:00", "11:00", "14:00", "17:00", "22:00"]
        },
        "New York (JFK) → San Francisco (SFO)": {
            "dep_city": "New York", "dep_tz": "US/Eastern", "dest_city": "San Francisco", "dest_tz": "US/Pacific",
            "duration": 6.5, "common_times": ["06:00", "09:00", "12:00", "15:00", "18:00"]
        },
        "San Francisco (SFO) → New York (JFK)": {
            "dep_city": "San Francisco", "dep_tz": "US/Pacific", "dest_city": "New York", "dest_tz": "US/Eastern",
            "duration": 5.5, "common_times": ["07:00", "10:00", "13:00", "16:00", "22:00"]
        }
    },
    "Transatlantic": {
        "New York (JFK) → London (LHR)": {
            "dep_city": "New York", "dep_tz": "US/Eastern", "dest_city": "London", "dest_tz": "Europe/London",
            "duration": 7.0, "common_times": ["21:30", "22:00", "22:30", "23:00"]
        },
        "London (LHR) → New York (JFK)": {
            "dep_city": "London", "dep_tz": "Europe/London", "dest_city": "New York", "dest_tz": "US/Eastern",
            "duration": 8.0, "common_times": ["09:00", "10:00", "11:00", "14:00", "16:00"]
        },
        "New York (JFK) → Paris (CDG)": {
            "dep_city": "New York", "dep_tz": "US/Eastern", "dest_city": "Paris", "dest_tz": "Europe/Paris",
            "duration": 7.5, "common_times": ["22:00", "23:00"]
        },
        "Paris (CDG) → New York (JFK)": {
            "dep_city": "Paris", "dep_tz": "Europe/Paris", "dest_city": "New York", "dest_tz": "US/Eastern",
            "duration": 8.5, "common_times": ["10:00", "12:00", "14:00"]
        }
    },
    "Transpacific": {
        "Los Angeles (LAX) → Tokyo (NRT)": {
            "dep_city": "Los Angeles", "dep_tz": "US/Pacific", "dest_city": "Tokyo", "dest_tz": "Asia/Tokyo",
            "duration": 12.0, "common_times": ["11:00", "16:00"]
        },
        "Tokyo (NRT) → Los Angeles (LAX)": {
            "dep_city": "Tokyo", "dep_tz": "Asia/Tokyo", "dest_city": "Los Angeles", "dest_tz": "US/Pacific",
            "duration": 10.0, "common_times": ["16:00", "17:00"]
        },
        "San Francisco (SFO) → Tokyo (NRT)": {
            "dep_city": "San Francisco", "dep_tz": "US/Pacific", "dest_city": "Tokyo", "dest_tz": "Asia/Tokyo",
            "duration": 11.0, "common_times": ["13:00", "15:00"]
        },
        "Tokyo (NRT) → San Francisco (SFO)": {
            "dep_city": "Tokyo", "dep_tz": "Asia/Tokyo", "dest_city": "San Francisco", "dest_tz": "US/Pacific",
            "duration": 9.5, "common_times": ["15:00", "17:00"]
        }
    },
    "Hawaii & Other": {
        "New York (JFK) → Honolulu (HNL)": {
            "dep_city": "New York", "dep_tz": "US/Eastern", "dest_city": "Honolulu", "dest_tz": "Pacific/Honolulu",
            "duration": 11.0, "common_times": ["08:00"]
        },
        "Los Angeles (LAX) → Honolulu (HNL)": {
            "dep_city": "Los Angeles", "dep_tz": "US/Pacific", "dest_city": "Honolulu", "dest_tz": "Pacific/Honolulu",
            "duration": 6.0, "common_times": ["08:00", "10:00", "14:00", "16:00", "22:00"]
        },
        "Honolulu (HNL) → Los Angeles (LAX)": {
            "dep_city": "Honolulu", "dep_tz": "Pacific/Honolulu", "dest_city": "Los Angeles", "dest_tz": "US/Pacific",
            "duration": 5.5, "common_times": ["07:00", "09:00", "13:00", "15:00", "21:00"]
        },
        "Los Angeles (LAX) → Sydney (SYD)": {
            "dep_city": "Los Angeles", "dep_tz": "US/Pacific", "dest_city": "Sydney", "dest_tz": "Australia/Sydney",
            "duration": 15.0, "common_times": ["22:30"]
        },
        "Sydney (SYD) → Los Angeles (LAX)": {
            "dep_city": "Sydney", "dep_tz": "Australia/Sydney", "dest_city": "Los Angeles", "dest_tz": "US/Pacific",
            "duration": 13.5, "common_times": ["11:00"]
        }
    }
}

# Input method selection
input_method = st.radio("Choose input method:", ["Select Common Flight", "Custom Travel Details"])

if input_method == "Select Common Flight":
    st.header("Select Common Flight")
    
    # Flight category selection
    category = st.selectbox("Flight Category", list(COMMON_FLIGHTS.keys()))
    
    # Flight route selection
    route = st.selectbox("Flight Route", list(COMMON_FLIGHTS[category].keys()))
    
    flight_info = COMMON_FLIGHTS[category][route]
    
    # Display flight info
    st.write(f"**Route:** {route}")
    st.write(f"**Duration:** {flight_info['duration']} hours")
    
    # Departure time selection
    departure_time_str = st.selectbox("Departure Time", flight_info['common_times'])
    departure_time = datetime.strptime(departure_time_str, "%H:%M").time()
    
    # Date selection
    departure_date = st.date_input("Departure Date")
    
    # Extract flight details
    departure_city = flight_info['dep_city']
    destination_city = flight_info['dest_city']
    departure_tz = flight_info['dep_tz']
    destination_tz = flight_info['dest_tz']
    flight_duration = flight_info['duration']
    
    # Calculate arrival time
    dep_datetime = datetime.combine(departure_date, departure_time)
    arrival_datetime = dep_datetime + timedelta(hours=flight_duration)
    arrival_date = arrival_datetime.date()
    arrival_time = arrival_datetime.time()

else:
    st.header("Custom Travel Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Departure")
        departure_city = st.text_input("Departure City", "New York")
        departure_tz = st.selectbox("Departure Timezone", [
            "US/Eastern", "US/Central", "US/Mountain", "US/Pacific",
            "Europe/London", "Europe/Paris", "Europe/Rome", "Asia/Tokyo",
            "Asia/Shanghai", "Asia/Dubai", "Australia/Sydney", "Pacific/Honolulu"
        ], index=0)
        
        departure_date = st.date_input("Departure Date")
        departure_time = st.time_input("Departure Time", value=datetime.strptime("09:00", "%H:%M").time())
    
    with col2:
        st.subheader("Destination")
        destination_city = st.text_input("Destination City", "Honolulu")
        destination_tz = st.selectbox("Destination Timezone", [
            "US/Eastern", "US/Central", "US/Mountain", "US/Pacific",
            "Europe/London", "Europe/Paris", "Europe/Rome", "Asia/Tokyo",
            "Asia/Shanghai", "Asia/Dubai", "Australia/Sydney", "Pacific/Honolulu"
        ], index=11)
        
        arrival_date = st.date_input("Arrival Date")
        arrival_time = st.time_input("Arrival Time", value=datetime.strptime("14:00", "%H:%M").time())
    
    flight_duration = st.number_input("Flight Duration (hours)", min_value=1.0, max_value=20.0, value=11.0, step=0.5)

season = st.selectbox("Season (affects daylight hours)", ["Winter", "Spring", "Summer", "Fall"])

def calculate_time_difference(dep_tz_str, dest_tz_str, dep_datetime):
    """Calculate time difference between timezones at specific date/time"""
    dep_tz = pytz.timezone(dep_tz_str)
    dest_tz = pytz.timezone(dest_tz_str)
    
    # Localize the departure time
    dep_localized = dep_tz.localize(dep_datetime)
    
    # Convert to destination timezone
    dest_time = dep_localized.astimezone(dest_tz)
    
    # Calculate the difference in hours
    time_diff = (dest_time.utcoffset() - dep_localized.utcoffset()).total_seconds() / 3600
    
    return int(time_diff)

def get_light_hours(season):
    """Get appropriate light exposure hours based on season"""
    if season == "Winter":
        return (10, 16)  # 10 AM to 4 PM
    elif season == "Spring":
        return (8, 18)   # 8 AM to 6 PM
    elif season == "Summer":
        return (7, 20)   # 7 AM to 8 PM
    else:  # Fall
        return (9, 17)   # 9 AM to 5 PM

def format_time(dt):
    """Format datetime to HH:MM AM/PM"""
    return dt.strftime("%I:%M %p").lstrip('0')

def convert_time_to_destination(dt, dep_tz_str, dest_tz_str):
    """Convert time from departure timezone to destination timezone"""
    dep_tz = pytz.timezone(dep_tz_str)
    dest_tz = pytz.timezone(dest_tz_str)
    
    # Localize to departure timezone
    dep_localized = dep_tz.localize(dt, is_dst=None)
    
    # Convert to destination timezone
    dest_time = dep_localized.astimezone(dest_tz)
    
    return dest_time.replace(tzinfo=None)

def generate_protocol(dep_city, dest_city, dep_tz, dest_tz, dep_date, dep_time, arr_date, arr_time, season, flight_duration):
    """Generate complete jet lag protocol"""
    
    # Create departure datetime
    dep_datetime = datetime.combine(dep_date, dep_time)
    arr_datetime = datetime.combine(arr_date, arr_time)
    
    # Calculate time difference
    time_diff = calculate_time_difference(dep_tz, dest_tz, dep_datetime)
    is_eastward = time_diff > 0
    abs_time_diff = abs(time_diff)
    
    # Get light exposure hours
    light_start, light_end = get_light_hours(season)
    
    protocol_data = []
    
    # 3 Days Before Departure - Baseline
    baseline_bedtime = (dep_datetime - timedelta(days=3)).replace(hour=22, minute=0)
    baseline_bedtime_dest = convert_time_to_destination(baseline_bedtime, dep_tz, dest_tz)
    
    protocol_data.append([
        "3 Days Before Departure", "Normal bedtime", 
        format_time(baseline_bedtime), format_time(baseline_bedtime_dest),
        "Maintain normal schedule baseline", "Normal light exposure", "None", "Normal meal timing"
    ])
    
    # 2 Days Before Departure
    day2_wake = (dep_datetime - timedelta(days=2)).replace(hour=8, minute=0)
    
    if is_eastward:
        # Eastward: go to bed 1 hour earlier, morning light, avoid evening light
        day2_light = day2_wake.replace(hour=8, minute=0)
        day2_bedtime = day2_wake.replace(hour=21, minute=0)  # 9 PM (1 hour earlier than 10 PM)
        light_instruction = f"Natural sunlight {light_start}-{light_start+2} AM (no sunglasses)"
        avoid_light = "Sunglasses after 7 PM"
        shift_direction = "earlier"
    else:
        # Westward: go to bed 1 hour later, afternoon light, avoid morning light  
        day2_light = day2_wake.replace(hour=max(light_start, 14), minute=0)  # Afternoon light
        day2_bedtime = day2_wake.replace(hour=23, minute=0)  # 11 PM (1 hour later than 10 PM)
        light_instruction = f"Natural sunlight {light_start}-{light_end} depending on season (no sunglasses)"
        avoid_light = "Sunglasses 6-10 AM"
        shift_direction = "later"
    
    day2_wake_dest = convert_time_to_destination(day2_wake, dep_tz, dest_tz)
    day2_light_dest = convert_time_to_destination(day2_light, dep_tz, dest_tz)
    day2_bedtime_dest = convert_time_to_destination(day2_bedtime, dep_tz, dest_tz)
    
    protocol_data.extend([
        ["2 Days Before Departure", "Wake-up", 
         format_time(day2_wake), format_time(day2_wake_dest),
         "Wake at usual time", avoid_light, "1 mg melatonin 1 hr after waking", "Normal breakfast"],
        ["2 Days Before Departure", "Light exposure", 
         format_time(day2_light), format_time(day2_light_dest),
         "30 min natural sunlight exposure", light_instruction, "None", "Normal lunch/dinner"],
        ["2 Days Before Departure", "Bedtime shift", 
         format_time(day2_bedtime), format_time(day2_bedtime_dest),
         f"Go to bed 1 hour {shift_direction}", 
         f"Dim lights after {day2_bedtime.hour-2} PM", "None", "Light snack if needed"]
    ])
    
    # 1 Day Before Departure
    if is_eastward:
        day1_wake = (dep_datetime - timedelta(days=1)).replace(hour=7, minute=0)  # 1 hour earlier
        day1_light = day1_wake.replace(hour=7, minute=30)
        day1_bedtime = day1_wake.replace(hour=20, minute=0)  # 8 PM (another hour earlier)
        avoid_light = "Sunglasses after 6 PM"
    else:
        day1_wake = (dep_datetime - timedelta(days=1)).replace(hour=9, minute=0)  # 1 hour later
        day1_light = day1_wake.replace(hour=max(light_start, 15), minute=0)
        # Handle midnight properly
        bedtime_hour = 0  # 12 AM
        day1_bedtime = (day1_wake + timedelta(days=1)).replace(hour=bedtime_hour, minute=0)
        avoid_light = "Sunglasses 7-11 AM"
    
    day1_wake_dest = convert_time_to_destination(day1_wake, dep_tz, dest_tz)
    day1_light_dest = convert_time_to_destination(day1_light, dep_tz, dest_tz)
    day1_bedtime_dest = convert_time_to_destination(day1_bedtime, dep_tz, dest_tz)
    
    protocol_data.extend([
        ["1 Day Before Departure", "Wake-up", 
         format_time(day1_wake), format_time(day1_wake_dest),
         f"Wake 1 hour {shift_direction} than yesterday", avoid_light, "1 mg melatonin 1 hr after waking", "Normal breakfast"],
        ["1 Day Before Departure", "Light exposure", 
         format_time(day1_light), format_time(day1_light_dest),
         "30 min natural sunlight exposure", light_instruction, "None", "Normal lunch/dinner"],
        ["1 Day Before Departure", "Bedtime shift", 
         format_time(day1_bedtime), format_time(day1_bedtime_dest),
         f"Go to bed another hour {shift_direction}", 
         f"Dim lights after {(day1_bedtime.hour-2)%24} PM", "None", "Light snack if needed"]
    ])
    
    # Day of Departure
    early_wake = dep_datetime.replace(hour=max(5, dep_datetime.hour-3), minute=30)
    early_wake_dest = convert_time_to_destination(early_wake, dep_tz, dest_tz)
    
    # Calculate fasting duration properly
    dest_breakfast_time = arr_datetime + timedelta(hours=12)  # Next morning at destination
    dest_breakfast_time = dest_breakfast_time.replace(hour=7, minute=0)
    fast_duration = (dest_breakfast_time - early_wake).total_seconds() / 3600
    
    exercise_time = early_wake + timedelta(minutes=30)
    exercise_dest = convert_time_to_destination(exercise_time, dep_tz, dest_tz)
    
    airport_time = dep_datetime - timedelta(hours=1, minutes=45)
    airport_dest = convert_time_to_destination(airport_time, dep_tz, dest_tz)
    
    boarding_time = dep_datetime - timedelta(minutes=45)
    boarding_dest = convert_time_to_destination(boarding_time, dep_tz, dest_tz)
    
    takeoff_dest = convert_time_to_destination(dep_datetime, dep_tz, dest_tz)
    
    protocol_data.extend([
        ["Day of Departure", "Early wake", 
         format_time(early_wake), format_time(early_wake_dest),
         "Early wake to build sleep pressure", "Sunglasses immediately", "None", f"Begin {fast_duration:.1f}-hour fast"],
        ["Day of Departure", "Exercise", 
         format_time(exercise_time), format_time(exercise_dest),
         "Moderate workout avoid caffeine", "Avoid bright lights", "None", "Water only no caffeine"],
        ["Day of Departure", "Airport", 
         format_time(airport_time), format_time(airport_dest),
         "Set watch to destination time", "Sunglasses maintained", "Prep supplements", "Water + electrolytes"],
        ["Day of Departure", "Boarding", 
         format_time(boarding_time), format_time(boarding_dest),
         "Board with sleep kit", "Eye mask ready", "1 mg melatonin + 400 mg phosphatidylserine immediately upon boarding", "Decline meal service"],
        ["Day of Departure", "Takeoff", 
         format_time(dep_datetime), format_time(takeoff_dest),
         "Close window shade immediately", "Complete darkness", "None", "Continue fasting"]
    ])
    
    # In-flight strategy based on direction and duration
    if not is_eastward and abs_time_diff >= 4:  # Westward with significant difference
        nap_start = dep_datetime + timedelta(minutes=15)
        nap_end = nap_start + timedelta(minutes=30)
        nap_start_dest = convert_time_to_destination(nap_start, dep_tz, dest_tz)
        nap_end_dest = convert_time_to_destination(nap_end, dep_tz, dest_tz)
        
        protocol_data.extend([
            ["Day of Departure", "Strategic nap", 
             format_time(nap_start), format_time(nap_start_dest),
             "30-minute strategic nap", "Total darkness", "None", "Continue fasting"],
            ["Day of Departure", "Nap end", 
             format_time(nap_end), format_time(nap_end_dest),
             "Wake and stay awake", "Keep dark if still destination night", "None", "Hydrate 8 oz/hour"]
        ])
    
    # Break fast calculation
    dest_breakfast_dep_time = convert_time_to_destination(dest_breakfast_time, dest_tz, dep_tz)
    protocol_data.append([
        "Day of Departure", "Break fast", 
        format_time(dest_breakfast_dep_time), format_time(dest_breakfast_time),
        "Align with destination morning", "Gradual light as destination sunrise", "None", f"Light breakfast ({fast_duration:.1f} hr fast total)"
    ])
    
    # Arrival
    arr_dest_time = convert_time_to_destination(arr_datetime, dep_tz, dest_tz)
    protocol_data.append([
        "Day of Departure", "Arrival", 
        format_time(arr_datetime), format_time(arr_dest_time),
        f"Land in {dest_city}", "Immediate 30 min natural sunlight (no sunglasses)", "None", "Light snack"
    ])
    
    # Evening at destination
    dest_evening = arr_datetime.replace(hour=20, minute=0)
    if dest_evening <= arr_datetime:
        dest_evening += timedelta(days=1)
    dest_evening_dep = convert_time_to_destination(dest_evening, dest_tz, dep_tz)
    
    dest_bedtime_prep = dest_evening + timedelta(hours=1, minutes=30)
    dest_bedtime_prep_dep = convert_time_to_destination(dest_bedtime_prep, dest_tz, dep_tz)
    
    dest_bedtime = dest_bedtime_prep + timedelta(hours=1)
    dest_bedtime_dep = convert_time_to_destination(dest_bedtime, dest_tz, dep_tz)
    
    protocol_data.extend([
        ["Arrival Day", "Evening routine", 
         format_time(dest_evening_dep), format_time(dest_evening),
         "Begin evening routine", "Start dimming lights", "None", "Light dinner"],
        ["Arrival Day", "Bedtime prep", 
         format_time(dest_bedtime_prep_dep), format_time(dest_bedtime_prep),
         "Pre-sleep routine keep cool", "Dim environment", "1 mg melatonin + 300 mg phosphatidylserine", "No food 3 hrs before bed"],
        ["Arrival Day", "Bedtime", 
         format_time(dest_bedtime_dep), format_time(dest_bedtime),
         "Sleep at local time", "Complete darkness", "None", "None"]
    ])
    
    # Day 1 at destination
    next_day = dest_bedtime + timedelta(days=1)
    
    # Handle common issues by direction
    if not is_eastward:  # Westward - early wake issue
        early_wake_next = next_day.replace(hour=4, minute=0)
        early_wake_next_dep = convert_time_to_destination(early_wake_next, dest_tz, dep_tz)
        
        protocol_data.append([
            "Day 1 Destination", "Predicted early wake", 
            format_time(early_wake_next_dep), format_time(early_wake_next),
            "Stay in bed stay dark no screens", "No light until target time", "None", "No food until breakfast"
        ])
    
    target_wake_next = next_day.replace(hour=6, minute=0)
    target_wake_next_dep = convert_time_to_destination(target_wake_next, dest_tz, dep_tz)
    
    evening_next = next_day.replace(hour=21, minute=30)
    evening_next_dep = convert_time_to_destination(evening_next, dest_tz, dep_tz)
    
    bedtime_next = next_day.replace(hour=22, minute=30)
    bedtime_next_dep = convert_time_to_destination(bedtime_next, dest_tz, dep_tz)
    
    sleep_aid = "50 mg trazodone if early waking issues" if not is_eastward else "Sleep aid if difficulty falling asleep"
    
    protocol_data.extend([
        ["Day 1 Destination", "Target wake", 
         format_time(target_wake_next_dep), format_time(target_wake_next),
         "Wake at desired local time", "30 min morning sun immediately (no sunglasses)", "None", "Breakfast at local time"],
        ["Day 1 Destination", "Evening routine", 
         format_time(evening_next_dep), format_time(evening_next),
         "Consistent routine", "Dim lights 2 hrs before bed", "1 mg melatonin if needed", "Light dinner no late snacks"],
        ["Day 1 Destination", "Bedtime", 
         format_time(bedtime_next_dep), format_time(bedtime_next),
         "Maintain schedule", "Complete darkness", sleep_aid, "None"]
    ])
    
    return protocol_data, time_diff, is_eastward, abs_time_diff

if st.button("Generate Jet Lag Protocol"):
    try:
        protocol_data, time_diff, is_eastward, abs_time_diff = generate_protocol(
            departure_city, destination_city, departure_tz, destination_tz,
            departure_date, departure_time, arrival_date, arrival_time, season,
            flight_duration if input_method == "Custom Travel Details" else COMMON_FLIGHTS[category][route]['duration']
        )
        
        # Create DataFrame
        columns = ["Phase", "Time of Day", f"{departure_city} Time", f"{destination_city} Time", 
                  "Optimized Protocol", "Light Management", "Supplements", "Meal Strategy"]
        df = pd.DataFrame(protocol_data, columns=columns)
        
        # Display results
        direction_text = "eastward" if is_eastward else "westward"
        st.success(f"Protocol generated for {abs_time_diff}-hour {direction_text} travel")
        
        if abs_time_diff < 3:
            st.warning("⚠️ Time difference is less than 3 hours. Minimal jet lag expected - this protocol may be overkill.")
        
        # Display protocol
        st.subheader("Your Personalized Jet Lag Protocol")
        st.dataframe(df, use_container_width=True)
        
        # Download CSV
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_string = csv_buffer.getvalue()
        
        st.download_button(
            label="Download Protocol as CSV",
            data=csv_string,
            file_name=f"jetlag_protocol_{departure_city}_{destination_city}_{departure_date}.csv",
            mime="text/csv"
        )
        
        # Show summary
        st.subheader("Protocol Summary")
        direction = "Eastward (Phase Advance)" if is_eastward else "Westward (Phase Delay)"
        st.write(f"**Direction:** {direction}")
        st.write(f"**Time Difference:** {abs_time_diff} hours")
        st.write(f"**Expected Adjustment Rate:** {'~57 min/day' if is_eastward else '~92 min/day'}")
        st.write(f"**Strategy:** {'Go to bed/wake earlier each day' if is_eastward else 'Go to bed/wake later each day'}")
        st.write(f"**Light Exposure:** {'Morning light, avoid evening' if is_eastward else 'Afternoon/evening light, avoid morning'}")
        
        if input_method == "Select Common Flight":
            st.write(f"**Flight Duration:** {COMMON_FLIGHTS[category][route]['duration']} hours")
        
    except Exception as e:
        st.error(f"Error generating protocol: {str(e)}")
        st.write("Please check your inputs and try again.")

st.markdown("---")
st.markdown("**Note:** This protocol is based on circadian rhythm research. Consult healthcare providers before using supplements.")
st.markdown("**Disclaimer:** For educational purposes only. Individual responses may vary.")