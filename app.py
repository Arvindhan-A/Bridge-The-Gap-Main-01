#!/usr/bin/env python3
import os
from btg import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config.get('DEBUG', False), port=int(os.environ.get('PORT', 2296)))
