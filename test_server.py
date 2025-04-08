import requests
import json

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