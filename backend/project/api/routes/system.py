from flask_jwt_extended import jwt_required, get_jwt_identity
from project import db
from flask import Blueprint, jsonify, url_for


system_bp = Blueprint('system_bp', __name__)

@system_bp.route('/health', methods=['GET'])
def check_health():
  # TODO:
  return jsonify({ 'msg': 'OK' }), 200

@system_bp.route('/test')
def home():
    # This JS needs to handle opening the popup and listening for the token
    # from Trello's postMessage.
    return f'''
        Hello!
        <br><button onclick="connectTrello()">Connect Trello (Client Flow - Test)</button>
        <p>To test Trello: Click 'Connect Trello', authorize in the popup. The popup should close, and this page will receive the token via postMessage.</p>
        <script>
            let trelloPopup = null;

            function connectTrello() {{
                fetch("{url_for('trello_auth_bp.trello_connect_initiate')}", {{
                  method: 'GET',
                        headers: {{
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0ODk2Mjc3NiwianRpIjoiYTBkZTlhODktYmE4OS00MWNmLThmODYtMDAxODVlMjI1MjJhIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3NDg5NjI3NzYsImNzcmYiOiJhNzIzZDgzZC0xMmE3LTRkNmItYmQ3ZS1mMThjNWQyZTIwZWMifQ.SWWxt30tiYiyFLrGBFn1I3I1KTz32U17TVDvAfWxFaA'
                        }},
                }})
                    .then(response => response.json())
                    .then(data => {{
                        if (data.authorization_url) {{
                            // Open the Trello authorization URL in a new window (popup)
                            trelloPopup = window.open(data.authorization_url, "TrelloAuth", "width=600,height=700");
                        }} else {{
                            alert("Error initiating Trello connection: " + (data.error || "Unknown error"));
                        }}
                    }})
                    .catch(error => {{
                        console.error("Error initiating Trello connection:", error);
                        alert("Error initiating Trello connection. See console.");
                    }});
            }}

            window.addEventListener('message', (event) => {{
                // IMPORTANT: Check event.origin in production to ensure message is from Trello
                // Example: if (event.origin !== "https://trello.com") return;
                // Trello's postMessage will send the token directly as event.data (it won't be an object)
                
                console.log("Message received:", event);

                if (event.source === trelloPopup && event.data && typeof event.data === 'string' && event.data.length > 40) {{ 
                    // Basic check that it might be a Trello token string
                    // Trello postMessage directly sends the token string, not an object.
                    const trelloToken = event.data;
                    console.log("Trello Token Received via postMessage:", trelloToken);

                    // Now send this token to your backend to save it
                    fetch("{url_for('trello_auth_bp.trello_save_token')}", {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0ODk2Mjc3NiwianRpIjoiYTBkZTlhODktYmE4OS00MWNmLThmODYtMDAxODVlMjI1MjJhIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3NDg5NjI3NzYsImNzcmYiOiJhNzIzZDgzZC0xMmE3LTRkNmItYmQ3ZS1mMThjNWQyZTIwZWMifQ.SWWxt30tiYiyFLrGBFn1I3I1KTz32U17TVDvAfWxFaA'
                            // Add CSRF token header if your Flask app uses Flask-WTF or similar
                        }},
                        body: JSON.stringify({{ token: trelloToken }})
                    }})
                    .then(response => response.json())
                    .then(saveResponse => {{
                        if (saveResponse.msg) {{
                             console.log("Trello connection saved: " + JSON.stringify(saveResponse.connectionDetails));
                            // Update UI with new connection
                        }} else {{
                             console.error("Error saving Trello token: " + (saveResponse.error || "Unknown error"));
                        }}
                    }})
                    .catch(error => {{
                        console.error("Error saving Trello token:", error);
                    }});

                    if (trelloPopup) {{
                        trelloPopup.close();
                        trelloPopup = null;
                    }}
                }} else if (event.data && event.data.type === 'githubSuccess') {{ // For existing GitHub flow
                     console.log("GitHub Message received from popup:", event.data);
                     alert('GitHub connected! Details: ' + JSON.stringify(event.data.connectionDetails));
                }}
            }});
        </script>
    '''