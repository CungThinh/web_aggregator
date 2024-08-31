from . import oauth
from decouple import config

google = oauth.register(
        name='google',
        client_id=config('GOOGLE_CLIENT_ID'),
        client_secret=config('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid profile email'}
        )

github = oauth.register(
    name='github',
    client_id=config('GITHUB_CLIENT_ID'),
    client_secret=config('GITHUB_CLIENT_SECRET'),
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri=config('GITHUB_REDIRECT_URI'),
    client_kwargs={'scope': 'user:email'},
)

facebook = oauth.register(
    name='facebook',
    client_id=config('FACEBOOK_CLIENT_ID'),
    client_secret=config('FACEBOOK_CLIENT_SECRET'),
    authorize_url='https://www.facebook.com/v10.0/dialog/oauth',
    access_token_url='https://graph.facebook.com/v10.0/oauth/access_token',
    client_kwargs={'scope': 'email public_profile'},
)