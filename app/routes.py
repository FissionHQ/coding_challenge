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
    """Brings profile summary from both bitbucket and github"""
    profiles = []

    profile_obj = {
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
    if request_args.get('github_usernames'):
        delimiter = request_args.get('username_delimiter', ',')

        usernames = {username.strip() for username in request_args['github_usernames'].split(delimiter)}
        for username in usernames:
            profile = GitHub(username)
            profile.validate_username()
            profiles.append(profile)

    if request_args.get('bitbucket_usernames'):
        delimiter = request_args.get('username_delimiter', ',')

        usernames = {username.strip() for username in request_args['bitbucket_usernames'].split(delimiter)}
        for username in usernames:
            profile = Bitbucket(username)
            profile.validate_username()
            profiles.append(profile)

    for profile in profiles:
        profile_obj['public_repos']['original'] += profile.original_public_repos_count
        profile_obj['stars_given'] += profile.stars_count
        profile_obj['open_issues'] += profile.open_issues_count
        profile_obj['stars_received'] += profile.received_star_count
        profile_obj['public_repos']['forked'] += profile.forked_public_repos_count
        profile_obj['languages'].update(profile.repositories_per_language.keys())
        profile_obj['topics'].update(profile.repositories_per_topic.keys())
    profile_obj['topics'] = tuple(profile_obj['topics'])
    profile_obj['languages'] = tuple(profile_obj['languages'])
    return flask.jsonify(profile_obj)
