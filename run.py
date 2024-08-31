from app import create_app, db
from config import DevConfig

if __name__ == "__main__":
    app = create_app(DevConfig)
    with app.app_context():
        db.create_all()
    app.run(port=8000, debug=True)
    """
    Config https for facebook login - not secure
    app.run(port=8000, debug=True, ssl_context=('cert.pem', 'key.pem'))
    """ 

