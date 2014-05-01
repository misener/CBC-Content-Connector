import os
import urllib
import webapp2
import jinja2
import json
import re
import logging
from google.appengine.api import urlfetch

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

class MainHandler(webapp2.RequestHandler):
    def get(self):
        program = self.request.get('program', default_value="Spark")
    	number_of_results = self.request.get('results', default_value="5")

        params = urllib.urlencode(
            { 'form': 'json',
              'range': '1-%s' % number_of_results,
              'sort': 'added|desc',
              'pretty': 'true',
              'byCustomValue': '{show}{%s}' % program })

        url = 'http://feed.theplatform.com/f/h9dtGB/r3VD0FujBumK?%s' % params

        logging.info(url)

        r = json.loads(urlfetch.fetch(url, deadline=20).content)

        # logging.info(r)

        audioclips = []

        for entry in r['entries']:
            title = entry['title']

            audioclipIDurl = entry['media$content'][0]['plfile$releases'][0]['id']
            audioclipID = re.search(r'\d{10}', audioclipIDurl).group()

            mediaIDurl = entry['media$content'][0]['plfile$releases'][0]['plrelease$mediaId']
            mediaID = re.search(r'\d{10}', mediaIDurl).group()

            metrics = entry['plmedia$metrics']

            # logging.info(metrics)

            audioclips.append((audioclipID, mediaID, title, metrics))


        # Grab standalone player clips (with YoSpace IDs)
        # For radio shows, this is pretty much always the only release
        # turning it off November 1, 2013


        # standaloneplayerclips = []

        # for entry in r['entries']:
        #     title = entry['title']
        #     metrics = entry['plmedia$metrics']

        #     for content in entry['media$content']:

        #         for release in content['plfile$releases']:
        #             audioclipIDurl = release['id']
        #             audioclipID = re.search(r'\d{10}', audioclipIDurl).group()

        #             mediaIDurl = release['plrelease$mediaId']
        #             mediaID = re.search(r'\d{10}', mediaIDurl).group()

        #             if 'pl1$yospaceID' in release:
        #                 standaloneplayerclips.append((audioclipID, mediaID, title, metrics))


        template_values = {
            'audioclips': audioclips,
            'program': program,
            'results': number_of_results,
            # 'standaloneplayerclips': standaloneplayerclips
            }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainHandler)], debug=False)