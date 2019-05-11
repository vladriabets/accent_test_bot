# accent_test_bot
Telegram bot that runs psychological accentuation test

To run this bot you need to:
- create a virtualenv
- install dependencies from **requirements.txt** using pip
- create an environment variable TOKEN and set it equal to your bot's token, that BotFather gave you

After that you can run the bot like a Flask app ot deploy it on Heroku like I did it.
To deploy it on Heroku you already have a **Procfile** with nessesary settings.
While deploying it I had a problem that was solved by setting a variable WEB_CONCURRENCY=1 on Heroku environment.

**Hello.py** is an app with the bot logic itself.
**Models.py** contain the model for a database.
Text files **questions** and **description** contain text for the messages that bot may send. And **answers** contain column number for each question to add points to.
