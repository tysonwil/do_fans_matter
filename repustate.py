"""
Repustate Python API client.

Requirements:
- Python
- A json library (builtin or simplejson works fine)

Want to change it / improve it / share it? Go for it.

Feedback is appreciated at info@repustate.com

More documentation available at http://www.repustate.com/docs
"""
import base64
import urllib
import urllib2

try:
    # Different versions of Python call the json library different things.
    import json
except ImportError:
    import simplejson as json

class Repustate(object):

    url_template = (
        'http://api.repustate.com/%(version)s/%(key)s/%(function)s.json'
        )

    ppt_url = 'http://api.repustate.com/%(version)s/%(key)s/powerpoint/'

    def __init__(self, api_key, version='v2'):
        self.api_key = api_key
        self.version = version

    def _call_api(self, api_function, use_http_get=False, **params):
        params = dict((x, y) for x, y in params.iteritems() if y is not None)

        data = urllib.urlencode(params)

        url_args = dict(
            function=api_function,
            key=self.api_key,
            version=self.version,
        )

        if api_function == 'powerpoint':
            url = self.ppt_url % url_args
            response = urllib2.urlopen(url, data)
            # Return the ppt file as binary data.
            result = response.read()
        else:
            url = self.url_template % url_args

            if use_http_get:
                url = '%s?%s' % (url, data)
                response = urllib2.urlopen(url)
            else:
                response = urllib2.urlopen(url, data)

            result = json.load(response)

        return result

    def _call_natural_language(self, api_function, cloud=None, text=None, url=None, lang='en'):
        """
        Helper function for the NLP calls.
        """
        return self._call_api(api_function, cloud=cloud, text=text, url=url, lang=lang)

    def sentiment(self, text=None, url=None, lang='en'):
        """
        Retrieve the sentiment for a single URl or block of text.
        """
        return self._call_api('score', text=text, url=url, lang=lang)

    def bulk_sentiment(self, items=None, lang='en'):
        """
        Bulk score multiple pieces of text (not urls!).
        """
        items_to_score = {}

        for idx, item in enumerate(items):
            items_to_score['text%d' % idx] = item

        return self._call_api('bulk-score', lang=lang, **items_to_score)

    def clean_html(self, url=None):
        """
        Clean up a web page. It doesn't work well on home pages - it's designed for content pages.
        """
        return self._call_api('clean-html', use_http_get=True, url=url)
    
    def nouns(self, cloud=None, text=None, url=None, lang='en'):
        # Only English language for now.
        return self._call_natural_language('noun', cloud=cloud, text=text, url=url, lang=lang)

    def adjectives(self, cloud=None, text=None, url=None, lang='en'):
        return self._call_natural_language('adj', cloud=cloud, text=text, url=url, lang=lang)

    def verbs(self, cloud=None, text=None, url=None, lang='en'):
        return self._call_natural_language('verb', cloud=cloud, text=text, url=url, lang=lang)

    def ngrams(self, url=None, text=None, max=None, min=None, freq=None, stopwords=None, lang='en'):
        return self._call_api('ngrams', use_http_get=bool(url), text=text,
                              url=url, max=max, min=min, freq=freq,
                              stopwords=stopwords,
                              lang=lang,
                              )

    def date_extraction(self, text):
        """
        Convert english date indicators like "today", "tomorrow", "next week"
        into date strings like 2011-01-12.
        """
        return self._call_api('extract-dates', text=text)

    def powerpoint(self, report_title, author, images, titles, notes):
        """
        Given a sorted list of images, titles and notes, generate a simple powerpoint presentation.

        The length of each list must be the same.
        """
        kwargs = dict(
            title=report_title,
            author=author,
        )

        assert len(images) == len(titles) == len(notes), "The lists of images, titles, and notes supplied must all be the same length."

        for idx, (image, title, note) in enumerate(zip(images, titles, notes)):
            # We need to b64 encode the image.
            image_content = base64.b64encode(open(image).read())
            kwargs['slide_%d_image' % idx] = image_content
            kwargs['slide_%d_title' % idx] = title
            kwargs['slide_%d_notes' % idx] = note

        return self._call_api('powerpoint', **kwargs)

if __name__ == '__main__':
    """
    Sample usage of the client library. You'll have to change the api_key below
    to yours if you want to actually run this.
    """
    client = Repustate(api_key='56573aa5ca65584d17085451de98dc29ca079e4a', version='v2')

    # Score a single piece of text.
    score = client.sentiment(text='I hate food.')

    # Score multiple pieces of text.
    scores = client.bulk_sentiment(['I love candy', 'I hate fish', 'I want to go watch a movie'])

    # To make this example work, you'll have to have an image called 'test.jpg'
    # in this directory. A new power point presentation called "Test.ppt" will
    # be saved in the current directory.
    data = client.powerpoint('Test Report', 'Martin Ostrovsky', images=['test.jpg'], titles=['A test title'], notes=['What a pretty slide.'])
    fd = open('Test.ppt', 'w')
    fd.write(data)
    fd.close()