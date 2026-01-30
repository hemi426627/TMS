from os import environ
from Task_Management_System import app

if __name__ == "__main__":
    # Host & port
    HOST = "localhost"
    PORT = 5555

    # Optional: allow overriding with environment variables
    if "SERVER_HOST" in environ:
        HOST = environ["SERVER_HOST"]

    if "SERVER_PORT" in environ:
        try:
            PORT = int(environ["SERVER_PORT"])
        except ValueError:
            pass  # keep default 5555

    # Enable debug mode and hot reload
    app.run(
        host=HOST,
        port=PORT,
        debug=True,  # Flask debug mode
        use_reloader=True,  # Hot reload enabled
    )
