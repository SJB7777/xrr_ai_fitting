from .app import app
from app import layout

def run():
    app.run(port=8050, debug=True)