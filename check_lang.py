import os
from app import create_app

app = create_app()
print("BABEL_TRANSLATION_DIRECTORIES =", app.config.get("BABEL_TRANSLATION_DIRECTORIES"))
print("LANGUAGES =", app.config.get("LANGUAGES"))
print("mo exists =", os.path.exists(
    os.path.join(app.config.get("BABEL_TRANSLATION_DIRECTORIES", ""),
                 "hi", "LC_MESSAGES", "messages.mo")))

from flask_babel import force_locale, gettext
with app.test_request_context():
    with force_locale("hi"):
        print("Dashboard ->", gettext("Dashboard"))