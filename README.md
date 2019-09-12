# Coding Challenge App

A skeleton flask app to use for a coding challenge.

## Install:

You can use a virtual environment (conda, venv, etc):
```
conda env create -f environment.yml
source activate user-profiles
```

Or just pip install from the requirements file
``` 
pip install -r requirements.txt
```

## Running the code

### Spin up the service

# start up local server
```bash
$ export FLASK_APP=run.py
$ flask run
```

#### Using Pip

```bash
$ python3.6 -m venv /path/to/venv
$ . venv/bin/activate
$ pip install -r requirements.txt
```

### Making Requests

```
curl -i "http://127.0.0.1:5000/health-check"

curl -i "http://127.0.0.1:5000/v1/get-profile-data?github_usernames=phlogistonjohn&bitbucket_usernames=phlogistonjohn"
```

API base url --> (by default, http://127.0.0.1:5000)

# Endpoints usage examples

- Get summary object for a single GitHub user:
    ```bash
    $ curl <base url>/v1/get-profile-data?github_usernames=<GitHubUsername> -v
    ```
- Get aggregated results of both the GitHub user and Bitbucket user:
    ```bash
    $ curl <base url>/v1/get-profile-data?github_usernames=<GitHubUsername>&bitbucket_usernames=<BitBucketUsername> -v
    ```

### Run the Tests

Run the following command in your virtual environment:

```bash
$ pytest -v
```
