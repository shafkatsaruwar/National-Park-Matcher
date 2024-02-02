from flask import Flask, render_template, request
import requests

app = Flask(__name__)

def fetch_states(api_key):
    # NPS API endpoint to get a list of parks/states
    url = "https://developer.nps.gov/api/v1/parks"

    #Make request to NPS API to get the list of parks
    headers = {"Accept": "application/json"}
    params = {"api_key": api_key, "limit": 55}
    response = requests.get(url, headers=headers, params=params)

    # API response
    if response.status_code == 200:
        parks = response.json().get('data', [])
        # Extract unique states from the list of parks
        states = list(set(state for park in parks for state in park.get('states', '').split(',')))
        # Alphabetizes the list of states
        states = sorted(states)
        return states
    else:
        return []

def fetch_activities(api_key):
    # NPS API endpoint to get a list of activities
    url = "https://developer.nps.gov/api/v1/activities/parks"

    # Make request to NPS API to get the list of activities
    headers = {"Accept": "application/json"}
    params = {"api_key": api_key}
    response = requests.get(url, headers=headers, params=params)

    # Process API response
    if response.status_code == 200:
        activities = response.json().get('data', [])
        return activities
    else:
        return []

@app.route('/')
def index():
    # Karina API Key
    api_key = 'a4EChWUjEwl5EKCrweIX0jakxf3Tttxw9gT6elgd'

    # Fetch and pass available states and activities to the template
    states = fetch_states(api_key)
    activities = fetch_activities(api_key)
    return render_template('index.html', states=states, activities=activities)

@app.route('/search')
def search():
    # Karina API Key
    api_key = 'a4EChWUjEwl5EKCrweIX0jakxf3Tttxw9gT6elgd'

    # Get selected state and activity from the request parameters
    selected_state = request.args.get('state', '')
    selected_activity = request.args.get('activity', '')

    # Fetch parks based on the selected state and activity
    url = "https://developer.nps.gov/api/v1/parks"
    headers = {"Accept": "application/json"}
    params = {"api_key": api_key, "stateCode": selected_state.upper(), "activity": selected_activity}
    response = requests.get(url, headers=headers, params=params)

    # Process API response
    if response.status_code == 200:
        parks = response.json().get('data', [])
        return render_template('search_results.html', state_name=selected_state, activity_name=selected_activity, parks=parks)
    else:
        # Handle error, for example, redirect to an error page
        return render_template('error.html', message='Failed to fetch parks for the specified state and activity')

@app.route('/state_parks/<state_code>')
def state_parks(state_code):
    # Replace 'YOUR_API_KEY' with your actual NPS API key
    api_key = 'a4EChWUjEwl5EKCrweIX0jakxf3Tttxw9gT6elgd'

    # NPS API endpoint to get parks for the specified state
    url = "https://developer.nps.gov/api/v1/parks"
    headers = {"Accept": "application/json"}
    params = {"api_key": api_key, "stateCode": state_code.upper()}  # Convert state code to uppercase
    response = requests.get(url, headers=headers, params=params)

    # Process API response
    if response.status_code == 200:
        parks = response.json().get('data', [])
        return render_template('state_parks.html', state_name=state_code, parks=parks)
    else:
        # Handle error, for example, redirect to an error page
        return render_template('error.html', message='Failed to fetch parks for the specified state')

@app.route('/activity_parks/<activity_name>')
def activity_parks(activity_name):
    # Replace 'YOUR_API_KEY' with your actual NPS API key
    api_key = 'a4EChWUjEwl5EKCrweIX0jakxf3Tttxw9gT6elgd'

    # NPS API endpoint to get parks for the specified activity
    url = "https://developer.nps.gov/api/v1/activities/parks"
    headers = {"Accept": "application/json"}
    params = {"api_key": api_key, "activity": activity_name}
    response = requests.get(url, headers=headers, params=params)

    # Process API response
    if response.status_code == 200:
        parks = response.json().get('data', [])
        return render_template('activity_parks.html', activity_name=activity_name, parks=parks)
    else:
        # Handle error, for example, redirect to an error page
        return render_template('error.html', message='Failed to fetch parks for the specified activity')

if __name__ == '__main__':
    app.run(debug=True)

