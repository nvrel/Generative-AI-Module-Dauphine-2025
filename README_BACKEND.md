# Tweet Generator Backend

This is a simple Flask backend for the Tweet Generator application. It provides an API endpoint for generating tweets based on user input.

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Run the Flask application:

```bash
python app.py
```

The application will be available at http://127.0.0.1:5000/

## API Endpoints

### Generate Tweet

- **URL**: `/api/generate_tweet`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "prompt": "Your prompt here",
    "company": "Company name"
  }
  ```
- **Response**:
  ```json
  {
    "tweet": "Generated tweet text"
  }
  ```

## Frontend Integration

The backend is designed to work with the frontend located in the `templates` directory. The frontend makes a POST request to the `/api/generate_tweet` endpoint with the user's prompt and selected company.

## CORS Support

The backend has CORS enabled, allowing it to be accessed from different frontend applications if needed. 