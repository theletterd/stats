import sys
import os


CURRENT_FILE = os.path.abspath(__file__)
CURRENT_DIR = os.path.dirname(CURRENT_FILE)

# Add project top-dir to path (since it has no __init__.py)
sys.path.append(CURRENT_DIR)

from statsapp import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
