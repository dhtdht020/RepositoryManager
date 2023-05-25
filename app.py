from flask import Flask

import config
import helpers
import index
from admin.routes import admin
from api.routes import api
from hbb.routes import hbb
from models import db, login, StatusLogsModel
from scheduler import scheduler, socketio
from setup.routes import setup

app = Flask(__name__)
socketio.init_app(app)


# Configuration
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Register blueprints
app.register_blueprint(admin)
app.register_blueprint(api)
app.register_blueprint(hbb)
app.register_blueprint(setup)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = config.secret_key
db.init_app(app)
login.init_app(app)
login.login_view = 'admin.login'


# Register scheduler jobs
scheduler.add_job(index.update, 'interval', hours=24, replace_existing=True, id='index_update',
                  args=[])
scheduler.start()


# before first request
with app.app_context():
    db.create_all()
    index.initialize()

    # clear all status logs
    for log in StatusLogsModel.query.all():
        db.session.delete(log)
    db.session.commit()
    helpers.log('Started Repository Manager!', 'success')

app.jinja_env.globals.update(index=index.get)


@app.route('/')
def hello_world():  # put application's code here
    return 'Open Shop Channel Repository Manager'


if __name__ == '__main__':
    app.run()
