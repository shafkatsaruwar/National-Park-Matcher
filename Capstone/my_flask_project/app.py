from flask import Flask, render_template, request, redirect, url_for, session
import requests
import os
import secrets

app = Flask(__name__)
api_key = 'a4EChWUjEwl5EKCrweIX0jakxf3Tttxw9gT6elgd'
google_api_key = "AIzaSyC-qIECy3rEBGRUmv8CvW04Wzx9e0S1z8E"
app.secret_key = secrets.token_hex(16)

def fetch_activities():
    url = "https://developer.nps.gov/api/v1/activities"
    headers = {"Accept": "application/json"}
    params = {"api_key": api_key}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        return []

def fetch_states():
    url = "https://developer.nps.gov/api/v1/parks"
    headers = {"Accept": "application/json"}
    params = {"api_key": api_key, "limit": 100}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        parks = response.json().get('data', [])
        states = list(set(state for park in parks for state in park.get('states', '').split(',')))
        states = sorted(states)
        
        territories = ['AS', 'GU', 'MP', 'PR', 'VI', 'DC'] 
        for territory in territories:
            if territory not in states:
                states.append(territory)
        states = sorted(states) 
        
        return states
    else:
        return []
        
def fetch_park_details(parkCode):
    url = f"https://developer.nps.gov/api/v1/parks?parkCode={parkCode}&api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        park = response.json().get('data', [])[0]  # Assuming there's at least one park returned
        return park
    else:
        return None
        
def get_directions_to_park(park_latitude, park_longitude):
    origin = "Boston,MA"
    destination = f"{park_latitude},{park_longitude}"
    api_key = "AIzaSyC-qIECy3rEBGRUmv8CvW04Wzx9e0S1z8E"
    url = "https://maps.googleapis.com/maps/api/directions/json"

    params = {
        "origin": origin,
        "destination": destination,
        "key": api_key
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        directions = response.json()
        return directions
    else:
        return None

@app.route('/')
def index():
    activities = fetch_activities()
    states = fetch_states()
    return render_template('index.html', activities=activities, states=states)

@app.route('/search_results', methods=['GET'])
def search_results():
    selected_state = request.args.get('state')
    selected_activity = request.args.get('activity')
    user_location = request.args.get('user_location', '')  # Capture the user's location

    if selected_state:
        return redirect(url_for('state_parks', state_code=selected_state, user_location=user_location))
    elif selected_activity:
        activity_name = next((activity['name'] for activity in fetch_activities() if activity['id'] == selected_activity), "Selected Activity")
        return redirect(url_for('activity_parks', activity_id=selected_activity, activity_name=activity_name, user_location=user_location))
    else:
        return render_template('error.html', message='Please select either a state or an activity.')

@app.route('/state_parks/<state_code>')
def state_parks(state_code):
    user_location = request.args.get('user_location', 'Boston,MA')  
    url = "https://developer.nps.gov/api/v1/parks"
    headers = {"Accept": "application/json"}
    params = {"api_key": api_key, "stateCode": state_code}
    response = requests.get(url, headers=headers, params=params)  
    parks = []  

    if response.status_code == 200:
        parks = response.json().get('data', [])

    return render_template('state_parks.html', state=state_code, parks=parks, user_location=user_location)

@app.route('/activity_parks/<activity_id>/<activity_name>')
def activity_parks(activity_id, activity_name):
    user_location = request.args.get('user_location', 'Boston,MA')
    url = "https://developer.nps.gov/api/v1/activities/parks"
    headers = {"Accept": "application/json"}
    params = {"api_key": api_key, "id": activity_id}
    response = requests.get(url, headers=headers, params=params)
    parks = []

    if response.status_code == 200:
        activities_data = response.json().get('data', [])
        for activity in activities_data:
            if activity['id'] == activity_id:
                parks.extend(activity.get('parks', []))
                break

    return render_template('activity_parks.html', activity_name=activity_name, parks=parks, user_location=user_location)

@app.route('/park_details/<parkCode>')
def park_details(parkCode):
    park = fetch_park_details(parkCode)
    user_location = request.args.get('user_location', 'Boston,MA')  # Fallback to 'Boston,MA' if not provided

    if not park:
        return render_template('error.html', message='Could not fetch park details.')

    if 'latitude' in park and 'longitude' in park:
        destination = f"{park['latitude']},{park['longitude']}"
        directions_url = f"https://www.google.com/maps/dir/?api=1&origin={user_location}&destination={destination}"
        park['directionsUrl'] = directions_url
    else:
        park['directionsUrl'] = "#"

    return render_template('park_details.html', park=park, user_location=user_location)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
