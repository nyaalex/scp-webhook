# SCP Webhook
A basic Discord webhook integration for rising new SCP articles, powered by [Crom](https://crom.avn.sh/). Essentially it notifies a channel whenever a recent article has hit some threshold rating. I built this as I enjoy reading the SCP wiki, though I do not check it particularly regularly. Full disclosure this was whipped up in an afternoon, so use at your own risk.

# Usage
Setting up a Discord webhook is easy enough and there are plenty of tutorials out there for that, for this project you will need to do the following:

1. Install the `requests` python library, either globally or within a virtual environment.
2. Fill out the [example config file](/example-config.ini) with your webhook URL, alongside any desired changes to the configuration.
3. Rename the file to `config.ini` and ensure it is in the same directory as your `main.py`.
4. Set up some automation to run the script periodically.

Step 4 is left as an exercise to the reader. Personally, I use cron to run the script daily at 8am. _Please_, if you do use this project, do not run the script much more than once per day. Popular articles aren't always coming out that fast, and I'm sure the Crom team don't want to have to deal with any accidental DoS-ing from the impatience.

Let me know if there are any issues!
