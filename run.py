import os
from decouple import config
from beauty import create_app

app = create_app()

if __name__ == "__main__":
    # Runs in debug mode locally, but defaults to False when hosted
    debug_mode = config('FLASK_DEBUG', default=True, cast=bool)
    app.run(debug=debug_mode)