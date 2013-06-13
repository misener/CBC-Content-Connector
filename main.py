import os
import urllib

import webapp2
import jinja2


from google.appengine.api import urlfetch
import json
import re
import logging
import urllib

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

class MainHandler(webapp2.RequestHandler):
    def get(self):
        program = urllib.quote(self.request.get('program', default_value="Spark"))
    	number_of_results = self.request.get('results', default_value="10")

        url = "https://feed.theplatform.com/f/h9dtGB/r3VD0FujBumK?form=json&range=1-%s&sort=pubDate|desc&byCustomValue={show}{%s}" % (number_of_results, program)

        r = json.loads(urlfetch.fetch(url, deadline=20).content)

        # audioclip id=2381497597&mediaid=2381497585

        audioclips = []

        for entry in r['entries']:
            title = entry['title']

            audioclipIDurl = entry['media$content'][0]['plfile$releases'][0]['id']
            audioclipID = re.search(r'\d{10}', audioclipIDurl).group()

            mediaIDurl = entry['media$content'][0]['plfile$releases'][0]['plrelease$mediaId']
            mediaID = re.search(r'\d{10}', mediaIDurl).group()

            audioclips.append((audioclipID, mediaID, title))


        template_values = {
            'audioclips': audioclips,
            'program': urllib.unquote(program),
            'results': number_of_results,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainHandler)], debug=False)