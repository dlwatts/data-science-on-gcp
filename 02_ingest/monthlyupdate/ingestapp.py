
# [START app]
import os
import logging
import ingest_flights

import flask


# [start config]
app = flask.Flask(__name__)
# Configure this environment variable via app.yaml
CLOUD_STORAGE_BUCKET = os.environ['CLOUD_STORAGE_BUCKET']
#
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
# [end config]

@app.route('/')
def welcome():
         return '<html><a href="ingest">ingest next month</a> flight data</html>'

@app.route('/ingest')
def ingest_next_month():
    try:
         # verify that this is a cron job request
         is_cron = flask.request.headers['X-Appengine-Cron']
         logging.info('Received cron request {}'.format(is_cron))

         # next month
         bucket = CLOUD_STORAGE_BUCKET
         year, month = ingest_flights.next_month(bucket)
         status = 'scheduling ingest of year={} month={}'.format(year, month)
         logging.info(status)

         # ingest ...
         gcsfile = ingest_flights.ingest(year, month, bucket)
         status = 'successfully ingested={}'.format(gcsfile)
         logging.info(status)

    except ingest_flights.DataUnavailable:
         status = 'File for {}-{} not available yet ...'.format(year, month)
         logging.info(status)

    except KeyError as e:
         status = '<html>Sorry, this capability is accessible only by the Cron service, but I got a KeyError for {} -- try invoking it from <a href="{}"> the GCP console / AppEngine / taskqueues </a></html>'.format(e, 'http://console.cloud.google.com/appengine/taskqueues?tab=CRON')
         logging.info('Rejected non-Cron request')

    return status

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END app]
