from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # SECURITY ISSUE: Running in debug mode
    # SECURITY ISSUE: Exposing on all interfaces
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=True
    )
