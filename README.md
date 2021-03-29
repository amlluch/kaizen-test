IAM Username: kaizen_user

IAM Password: HocWDC1cfh3HMXc]3

Login URL: https://608738265803.signin.aws.amazon.com/console

# The Kaizen blog

Hi there! And welcome to the technical test stage of the interview process for becoming a Kaizen Backend Software Engineer!

Normally at this point, you should already be aware of what will be expected of you over the next few hours.

So let's jump straight in!

## Overview

We want you to create the REST API and backend resources of a web application that will be used as an "internal blog". The objective of the platform is to let Kaizen employees share updates and add comments to those updates through a single-page web UI, as shown below:

![Example](The%20Kaizen%20Blog.jpg)

Users don't have to be authenticated. Anyone within the organisation can access this webapp and post updates and comments. They just have to enter their name and the message they want to post. (And optionally an image for updates if they want to)

Users can also delete comments. Again, it doesn't matter whether they posted the comment they want to delete or not, here any user is able to delete any comment, there is no concept of authentication or ownership. However, what we'll want in a situation where a comment is deleted, is to send an email to alert administrators about it.

Below is the full list of requirements. We recommend you to start by documenting the technical architecture you plan on implementing before doing any actual work. (Last section of this document)

## Requirements

Requirement | User Story | Importance | Acceptance Criteria
------------ | ------------- | ------------- | -------------
Technical documentation | A developer/administrator wants to be able to understand how the web application is built | CRITICAL | Sufficient technical documentation available
Add basic update | A user wants to be able to post a basic update | CRITICAL | Given I'm on the Kaizen Blog, When I enter my username and the update I want to share, and click on the "Post!" button, Then my update is published and displayed at the top of the list
Add update with image | A user wants to be able to post an update with an image | MEDIUM | Given I'm on the Kaizen Blog, When I am in the process of posting an update, Then I can add a picture to it that will be displayed below the text of the update
View updates | A user wants to be able to view all updates | CRITICAL | Given I'm on the Kaizen Blog, When I browse through the page, Then I can view all updates sorted with the newest update first. When I am looking at a particular update, Then I can see the author, date, text and optional picture of the update
Add comment | A user wants to be able to add a comment to an update | CRITICAL | Given I'm on the Kaizen Blog, When I enter my username, comment and click on "Comment!", right below an update, Then my comment is published and displayed below all other comments for this update
View comments | A user wants to be able to view all comments on each update | CRITICAL | Given I'm on the Kaizen Blog, When I browse through the page, Then I can view all comments for all updates sorted with the oldest comment first. When I am looking at a particular comment, Then I can see the author, date, text, and a "Delete" button
Delete comment | A user wants to be able to delete a comment | HIGH | Given I'm on the Kaizen Blog, When I click on the "Delete" button next to a comment, Then I get prompted to confirm my action. When I confirm that I want to delete the comment, Then the comment is deleted and not displayed on the page anymore
Comment deletion notification | An administrator wants to get notified when a user deletes a comment | HIGH | Given I'm an administrator, When a user deletes a comment, Then I receive an email notification telling me which comment was deleted
Logging | An administrator wants to be able to access logs of all actions performed by users | MEDIUM | Given I'm on the Kaizen Blog, When I perform any action, Then logs of that action are generated and saved in the backend
Backend security | An administrator wants to be able to trust that the webapp has been coded securely | HIGH | AWS services permissioned following the principle of least privilege
IP whitelisting | An administrator wants to be able to launch the stack with IP whitelisting configured | MEDIUM | Given I'm an administrator, When I launch the stack, Then I can specify an IP address that will be the only location from where users are able to access the Kaizen Blog
Like | A user want to be able to "like" updates | LOW | Given I'm on the Kaizen Blog, When I am looking at a particular update, Then I can "like" that update. When I "like" an update, then the count of likes for that update is increased by 1 and displayed next to the update

## Constraints
### Allowed Services

* Amazon Certificate Manager (ACM)
* API Gateway V2
* Cloud9
* CloudFormation
* CloudWatch
* DynamoDB
* Identity and Access Management (IAM)
* Key Management Service (KMS)
* Lambda
* Secrets Manager
* Security Token Service (STS)
* Simple Email Service (SES)
* Simple Notification Service (SNS)
* Simple Queue Service (SQS)
* Simple Storage Service (S3)
* States (Step Functions)
* Systems Manager (SSM)
* Web Application Firewall (WAF)

### Sandbox Limits
#### IAM

* Cannot modify your IAM user or any already existing role/policy
* Cannot use or set up SSO

## Technical architecture

### Infrastructure

The architecture is as follows:

![Example](Gateway%20API%20architecture.jpeg)

![Example](Admin%20Email%20architecture.jpeg)

Two dynamodb tables are used and are indexed by the created_at field. The images will be uploaded to a separate endpoint that will store them in an s3 bucket.

When a comment is deleted, an SNS message will be sent. A lambda function subscribed to the Topic will receive the message and send an email to the administrator.

For IP whitelisting, a resource policy as follows will be used:
```angular2html
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "execute-api:Invoke",
  "Resource": "execute-api:/*/*/*",
  "Condition": {
    "NotIpAddress": {
      "aws:SourceIp": ["sourceIpOrCIDRBlock", "sourceIpOrCIDRBlock"]
       }
    }
}
```
### Python code
#### Setup
1. Install dependencies:

```bash
$ poetry install
```

2. Setup pre-commit hooks before committing:

```bash
$ poetry run pre-commit install
```
#### Testing
```bash
$ poetry run pytest
```
#### Libraries used
This job makes extensive use of dependency injection. I know it is not very common in Python but nevertheless I think it is a great idea, and I love it. For this purpose I will use the `kink` library

For data input and data validation I use `marshmallow` combined with `dataclasses`. This way we ensure that all input data is valid and that the classes are consistent.

All tests are performed with `pytest. First I develop the whole application locally and test it with tests. Once everything is working, then I deploy to AWS.

I use `pre-commit` for development along with `flake8`, `black` and `isort`. I also use `mypy` for typing hints.
