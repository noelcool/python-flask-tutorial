import os
from flask import Flask


def create_app(test_config=None):
    import sys
    from os import path
    _path = path.dirname(path.dirname(path.abspath(__file__)))
    sys.path.append(_path)
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flask.sqlite')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from flaskr import db
    db.init_app(app)

    from flaskr import auth
    app.register_blueprint(auth.bp)  # authentication blueprint

    @app.route('/hello')
    def hello():
        return 'Hello World'

    from flaskr import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port='5000', debug=True)
