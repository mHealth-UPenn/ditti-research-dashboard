from datetime import datetime
import logging
import os
from waitress import serve
from aws_portal.app import create_app

app = create_app()

fstring = '[%(asctime)s] %(levelname)s in %(module)s.%(funcName)s: %(message)s'
mountpoint = os.getenv('FLASK_LOG_MOUNT', '')
now = datetime.strftime(datetime.now(), '%Y_%m_%d-%H_%M_%S')
logfile = '%s-logfile' % now
filename = os.path.join(mountpoint, logfile)

if app.config['ENV'] == 'development':
    logging.basicConfig(
        format=fstring,
        level=app.config['LOG_LEVEL']
    )

elif app.config['ENV'] == 'production':
    logging.basicConfig(
        filename=filename,
        format=fstring,
        level=app.config['LOG_LEVEL']
    )

if __name__ == '__main__':
    if app.config['ENV'] == 'development':
        app.run(debug=True)

    elif app.config['ENV'] == 'production':
        logger = logging.getLogger('waitress')
        serve(app, host='0.0.0.0', port=5000)
