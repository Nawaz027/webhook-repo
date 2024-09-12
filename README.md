# Webhook Integration

## To Access the Frontend:
You can access the frontend of the application using this [GitHub repository](https://github.com/Nawaz027/webhook-frontend).

## Setup

1. **Create a new virtual environment**

    ```bash
    pip install virtualenv
    ```

2. **Create the virtual environment**

    ```bash
    virtualenv venv
    ```

3. **Activate the virtual environment**

    ```bash
    source venv/bin/activate
    ```

4. **Install the requirements**

    ```bash
    pip install -r requirements.txt
    ```

5. **Run the Flask application**

    In production, please use Gunicorn instead of the Flask development server:

    ```bash
    python run.py
    ```

6. **API Endpoint**

    The endpoint is available at:

    ```bash
    POST http://127.0.0.1:5000/webhook/receiver
    ```

## Additional Notes

Make sure to use this base setup to configure the Flask application. Integrate it with MongoDB (configuration is commented at `app/extensions.py`).
