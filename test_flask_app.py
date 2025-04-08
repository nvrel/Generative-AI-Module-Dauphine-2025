from flask import Flask, request, jsonify, render_template  # type: ignore
import requests
import json

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("test_index.html")


@app.route("/index.html")
def index_html():
    return render_template("index.html")


# Dummy function to simulate getting car details
def get_car_details(departure, destination):
    # Always return the specified message
    return {
        "message": "I cannot answer to this question yet but it will come soon!"
    }


@app.route("/get_car", methods=["GET"])
def get_car():
    # Always return the specified message regardless of input parameters
    return jsonify({
        "message": "I cannot answer to this question yet but it will come soon!"
    })


def test_generate_tweet():
    # Test data
    test_data = {
        "prompt": "Test prompt",
        "company": "Amazon"
    }
    
    try:
        # Make request to the local Flask server
        response = requests.post(
            'http://localhost:5000/api/generate_tweet',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        # Print response status
        print(f"Status Code: {response.status_code}")
        
        # Print response content
        print("\nResponse Content:")
        print(json.dumps(response.json(), indent=2))
        
        # Check if request was successful
        if response.status_code == 200:
            print("\n✅ Server is working correctly!")
        else:
            print("\n❌ Server returned an error status code")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to the server. Make sure the Flask server is running.")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")


if __name__ == "__main__":
    print("Testing Flask server...")
    test_generate_tweet()
