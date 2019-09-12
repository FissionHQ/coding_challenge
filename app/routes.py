import logging

import flask
from flask import Response
from app.summary import Bitbucket, GitHub

app = flask.Flask("user_profiles_api")
logger = flask.logging.create_logger(app)
logger.setLevel(logging.INFO)


@app.route("/health-check", methods=["GET"])
def health_check():
    """
    Endpoint to health check API
    """
    app.logger.info("Health Check!")
    return Response("All Good!", status=200)


@app.route('/v1/get-profile-data', methods=['GET'])
def get_merged_profile_data():
    """
        Consolidates Bitbucket and Github repository summaries. 

        URI: /v1/get-profile-data

        Query Parameters: 
            * github_username : Specify the github handle of the organization or team.
            * bitbucket_username : Specify the bitbucket handle of the organization or team.

        Returns: Consolidated Profile object

        TODO: 
            * The response could contain separate objects for github profile and bitbuckety profile for better downstream usage. However in this 
            case we assume that we are simply dealing with an API which is consolidating the metrics and attributes exposed by both these systems.            
    """
    profiles = []

    profile_obj = {
        'github_handle' : '',
        'bitbucket_handle': '',
        'stars_received': 0,
        'open_issues': 0,
        'languages': set(),
        'stars_given': 0,
        'topics': set(),
        'public_repos': {
            'original': 0,
            'forked': 0
        }
    }

    request_args = flask.request.args

    github_handle = ''
    bitbucket_handle = ''
    
    if request_args.get('github_username'):
        github_handle = request_args['github_username']
        git_profile = GitHub(github_handle)
        git_profile.validate_username()
        profiles.append(git_profile)

    if request_args.get('bitbucket_username'):
        bitbucket_handle = request_args['bitbucket_username']
        bitbucket_profile = Bitbucket(bitbucket_handle)
        bitbucket_profile.validate_username()
        profiles.append(bitbucket_profile)

    for profile in profiles:
        profile_obj['public_repos']['original'] += profile.original_public_repos_count
        profile_obj['stars_given'] += profile.stars_count
        profile_obj['open_issues'] += profile.open_issues_count
        profile_obj['stars_received'] += profile.received_star_count
        profile_obj['public_repos']['forked'] += profile.forked_public_repos_count
        profile_obj['languages'].update(profile.repositories_per_language.keys())
        profile_obj['topics'].update(profile.repositories_per_topic.keys())

    profile_obj['github_handle'] = github_handle
    profile_obj['bitbucket_handle'] = bitbucket_handle
    profile_obj['topics'] = tuple(profile_obj['topics'])
    profile_obj['languages'] = tuple(profile_obj['languages'])
    
    return flask.jsonify(profile_obj)

