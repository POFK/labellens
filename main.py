#!/usr/bin/env python
# coding=utf-8
from app import app, db
from app.models import User

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

if __name__ == "__main__":
#   app.run(host='0.0.0.0', port=10299)
    app.run()
