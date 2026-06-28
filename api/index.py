import os
import sys

# Add the parent directory to the path so we can import the btg package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from btg import create_app

app = create_app()

# For Vercel serverless functions
if __name__ == '__main__':
    app.run()
