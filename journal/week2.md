# Week 2 — Distributed Tracing

## Required Homework

## #1 HONEYCOMB 

I created a Honeycomb account and an environment. I used the environment's API Key to connect my Cruddur application data with Honeycomb.
I set the Honeycomb API Key as an environment variable in Gitpod using the below commands

```
export HONEYCOMB_API_KEY="<your API key>"
gp env HONEYCOMB_API_KEY="<your API key>"
```
Declared my API Key in the OTEL variable in the `docker-compose.yml` file:
```
OTEL_SERVICE_NAME: 'backend-flask'
      OTEL_EXPORTER_OTLP_ENDPOINT: "https://api.honeycomb.io"
      OTEL_EXPORTER_OTLP_HEADERS: "x-honeycomb-team=${HONEYCOMB_API_KEY}"
```

I followed the honeycomb documentation for Python and also Jessica's advice on how to run the queries in Honeycomb.
 
 **Trace spans in Honeycomb**

![](assets/honeycomb_trace.jpg)

## #2 AWS X-RAY
Amazon provides us another service called X-RAY which is helpful to trace requests of microservices. Analyzes and Debugs application running on distributed environment. I created segements and subsegments by following the instructional videos. 

- To get your application traced in AWS X-RAY you need to install aws-xray-sdk module. You can do this by running the below command.
```
pip install aws-xray-sdk
```
But in our bootcamp project we had added this module in our `requirements.txt` file and installed. 

- Created our own Sampling Rule name 'Cruddur'. This code was written in `aws/json/xray.json` file
```
{
  "SamplingRule": {
      "RuleName": "Cruddur",
      "ResourceARN": "*",
      "Priority": 9000,
      "FixedRate": 0.1,
      "ReservoirSize": 5,
      "ServiceName": "Cruddur",
      "ServiceType": "*",
      "Host": "*",
      "HTTPMethod": "*",
      "URLPath": "*",
      "Version": 1
  }
}
```
- **To create a new group for tracing and analyzing errors and faults in a Flask application.**
```
FLASK_ADDRESS="https://4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
aws xray create-group \
   --group-name "Cruddur" \
   --filter-expression "service(\"$FLASK_ADDRESS\")"
```
The above code is useful for setting up monitoring for a specific Flask service using AWS X-Ray. It creates a group that can be used to visualize and analyze traces for that service, helping developers identify and resolve issues more quickly.

Then run this command to get the above code executed 
```
aws xray create-sampling-rule --cli-input-json file://aws/json/xray.json
```
- **Install Daemon Service**
Then I had to add X-RAY Daemon Service for that I added this part of code in my `docker-compose.yml` file.
```
 xray-daemon:
    image: "amazon/aws-xray-daemon"
    environment:
      AWS_ACCESS_KEY_ID: "${AWS_ACCESS_KEY_ID}"
      AWS_SECRET_ACCESS_KEY: "${AWS_SECRET_ACCESS_KEY}"
      AWS_REGION: "us-east-1"
    command:
      - "xray -o -b xray-daemon:2000"
    ports:
      - 2000:2000/udp
```
Also added Environment Variables :
```
   AWS_XRAY_URL: "*4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}*"
   AWS_XRAY_DAEMON_ADDRESS: "xray-daemon:2000"
```

## My X-RAY Error 
When I was creatigna sampling rule then at te end after setting all the things when I had to run the last coomand `aws xray create-sampling-rule --cli-input-json file://aws/json/xray.json` to create a sampling rule I faced `Error parsing parameter` and `Error2: No such file or directory found`. 

![]()

## Solved X-RAY Error

So, I was in the wrong directory (frontend-react-js) while performing this task. I **changed my directory to `backend-flask`** and it was working all good. 

## AWS X-RAY Subsegments
There was a problem faced while creating subsegments in AWS X-RAY. But then one of our bootcamper (Olga Timofeeva) tried to figure it out and that somewhat helped. So we added `capture` method to get subsgements and closed the segment in the end by using `end-subsegment`. Below is the code that we added additionally to bring subsegments.
```
@app.route("/api/activities/<string:activity_uuid>", methods=['GET'])
@xray_recorder.capture('activities_show')
def data_show_activity(activity_uuid):
  data = ShowActivity.run(activity_uuid=activity_uuid)
  return data, 200
```
After adding I got subsegments 
![]()

## #3 CloudWatch
To use CloudWatch I installed `watchtower` package using pip. The environment variables were set in `docker-compose.yml` file as usual.

```
      AWS_DEFAULT_REGION: "${AWS_DEFAULT_REGION}"
      AWS_ACCESS_KEY_ID: "${AWS_ACCESS_KEY_ID}"
      AWS_SECRET_ACCESS_KEY: "${AWS_SECRET_ACCESS_KEY}"
```

**Configured LOGGER using the below code**
```
# Configuring Logger to Use CloudWatch
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
cw_handler = watchtower.CloudWatchLogHandler(log_group='cruddur')
LOGGER.addHandler(console_handler)
LOGGER.addHandler(cw_handler)
LOGGER.info("some message")
```
```
@app.after_request
def after_request(response):
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    LOGGER.error('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)
    return response
```
Logs were traced by Cloudwatch while working on week-2 homework
![](assets/cloudwatch_logs.jpg)

## #4 ROLLBAR
Installed `blinker` and `rollbar` packages. Set the environment variables for the Rollbar access token.

```
export ROLLBAR_ACCESS_TOKEN=""
gp env ROLLBAR_ACCESS_TOKEN=""
```
**Initialization code for Rollbar**

```
import rollbar
import rollbar.contrib.flask
from flask import got_request_exception
```
```
rollbar_access_token = os.getenv('ROLLBAR_ACCESS_TOKEN')
@app.before_first_request
def init_rollbar():
    """init rollbar module"""
    rollbar.init(
        # access token
        rollbar_access_token,
        # environment name
        'production',
        # server root directory, makes tracebacks prettier
        root=os.path.dirname(os.path.realpath(__file__)),
        # flask already sets up logging
        allow_logging_basic_config=False)

    # send exceptions from `app` to rollbar, using flask's signal system.
    got_request_exception.connect(rollbar.contrib.flask.report_exception, app)
```
```@app.route('/rollbar/test')
def rollbar_test():
    rollbar.report_message('Hello World!', 'warning')
    return "Hello World!"
```

## Rollbar Error
I am facing an issue while sending data to my Rollbar account. If you look at the below image, there is no GET request sent to Rollbar(connectivity issue).
![](assets/rollbar_connection.png)


I tried to solve it but no luck. There's a deafult project in our rollbar account called `FirstPorject`, so I created another project called `AWSBootcamp`. This gave me an option to choose `items` tab but it wasn't receiving any data.

![](assets/rollbar_error.png)

**Rollback keeps waiting for my data**
![](assets/rollbar_project.png)

## #5 Watched Pricing and Security Consideration Videos
- **Security** : Got to know about the Observability and Monitoring tools and how they are useful for our project, security maintainence and debugging purpose. Also attended the quiz. Here's the link for Ashish's video : https://www.youtube.com/watch?v=bOf4ITxAcXc&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=31 
- **Pricing** : In Chirag's pricing video, I examined the pricing models of Honeycomb, X-Ray, CloudWatch, and Rollbar. Through this exploration, I learned about the free-tier services offered by Amazon and the monthly capacity they provide. It's worth noting that pricing for these services as it varies by region.
