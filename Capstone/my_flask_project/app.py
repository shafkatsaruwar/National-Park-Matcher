from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)
api_key = 'a4EChWUjEwl5EKCrweIX0jakxf3Tttxw9gT6elgd'

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

@app.route('/')
def index():
    activities = fetch_activities()
    states = fetch_states()
    return render_template('index.html', activities=activities, states=states)

@app.route('/search_results', methods=['GET'])
def search_results():
    selected_state = request.args.get('state')
    selected_activity = request.args.get('activity')

    if selected_state:
        return redirect(url_for('state_parks', state_code=selected_state))
    elif selected_activity:
        # Fetch the activity name for displaying in the title
        activity_name = next((activity['name'] for activity in fetch_activities() if activity['id'] == selected_activity), "Selected Activity")
        return redirect(url_for('activity_parks', activity_id=selected_activity, activity_name=activity_name))
    else:
        return render_template('error.html', message='Please select either a state or an activity.')

@app.route('/state_parks/<state_code>')
def state_parks(state_code):
    url = "https://developer.nps.gov/api/v1/parks"
    headers = {"Accept": "application/json"}
    params = {"api_key": api_key, "stateCode": state_code}
    response = requests.get(url, headers=headers, params=params)
    parks = []

    if response.status_code == 200:
        parks = response.json().get('data', [])
    return render_template('state_parks.html', state=state_code, parks=parks)

@app.route('/activity_parks/<activity_id>/<activity_name>')
def activity_parks(activity_id, activity_name):
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

    return render_template('activity_parks.html', activity_name=activity_name, parks=parks)

@app.route('/park_details/<parkCode>')
def park_details(parkCode):
    url = f"https://developer.nps.gov/api/v1/parks?parkCode={parkCode}&api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        park = response.json().get('data', [])[0]
        return render_template('park_details.html', park=park)
    else:
        return render_template('error.html', message='Could not fetch park details.')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
