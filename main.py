import os
from configparser import ConfigParser
from datetime import datetime, timedelta

import requests as r
import json

URL = 'https://apiv1.crom.avn.sh/graphql'

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.ini')

# Query is nothing too fancy, and thanks to the Crom team for supporting a nice friendly language like GraphQL. All
# we're doing is grabbing every post from the last 30 days with a score over the threshold. Right now I'm making the
# assumption that no more than 100 "good" articles can be posted in one month, though I would be happy to be proven
# wrong.
QUERY = '''
query pages {
  pages(sort: {key: CREATED_AT, order: DESC}, first: 100, filter: {
    wikidotInfo: {
      rating: {gte: RATING_THRESHOLD}
      createdAt: {gt: "DATE_AFTER"}
    }
    url : {
      startsWith: "SCP_URL"
    }
  }) {
    edges {
      node {
        url
        alternateTitles {
          title
        }
        wikidotInfo {
          createdBy {
            name
          }
          title
          rating
          tags
        }
      }
    }
  }
}
'''


def main():
    config = ConfigParser()
    config.read(CONFIG_FILE)

    headers = {
        "User-Agent": "SCP Webhook by @Nyaalex on GitHub"
    }
    date = (datetime.today() - timedelta(days=30)).isoformat()
    query = ((QUERY.replace('DATE_AFTER', date)
              .replace('RATING_THRESHOLD', config['Config']['RatingThreshold']))
             .replace('SCP_URL', config['Config']['SCPUrl']))

    res = r.post(URL, json={"query": query}, headers=headers)
    articles = json.loads(res.text)

    # The idea with the previous articles is that I obviously don't want to spam the chat with the same messages,
    # so we need to stop repeats. However, I do not want hundreds of SCPs in a config file. My solution is to assume
    # that as long as we ignore everything posted last time we won't get repeats. This means that the only articles
    # that will be considered are those that match the filter, setting a hard limit of 100 in the config file. The
    # one limitation to this approach is that if, within a 30-day period, an article hits the threshold,
    # gets down-voted below, then makes its way back up, then it will be repeated. I believe this is a rare enough
    # occurance as to just accept it.
    prev_articles = config['PreviousArticles']['Articles'].split(';')
    found_articles = []
    for edge in articles['data']['pages']['edges']:

        article = edge['node']

        title = article["wikidotInfo"]["title"]
        found_articles.append(title)

        # If we have posted this recently we can skip it
        if title in prev_articles:
            continue

        if article["alternateTitles"]:
            title += ' - '
            title += article["alternateTitles"][0]["title"]

        title += f' (+{article["wikidotInfo"]["rating"]})'
        title += f' by {article["wikidotInfo"]["createdBy"]["name"]}'
        # Format is "title - alternate title (+score) by Author"

        description = f'[Link to article]({article["url"]})'

        # So neither Marvin nor the Crom discord bot typically show tags. Personally I quite like to know a little of
        # what I'm in for, especially if it's a canon/hub I'm not familiar with. I might add an option to turn them off
        # as they can introduce minor spoilers... I'll think on it.
        description += '\nTags: ' + ', '.join(article["wikidotInfo"]["tags"])

        data = {
            'embeds': [
                {
                    "description": description,
                    "title": title,
                }
            ]
        }

        url = config['Config']['WebhookUrl']

        r.post(url, json=data)

    config['PreviousArticles']['Articles'] = ';'.join(found_articles)
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)


if __name__ == '__main__':
    main()
