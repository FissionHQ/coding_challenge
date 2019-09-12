import requests
from collections import defaultdict
from app import profile_exceptions
import abc

__all__ = (
          'HostService',
          'Bitbucket',
          'GitHub',
)

class HostService(abc.ABC):
    """Abstract base class that acts as interface"""
    base_url = NotImplemented

    def __init__(self, username):
        self.summaryObj = {}
        self.username = username
        self._session = requests.Session()

    @property
    @abc.abstractmethod
    def repositories_per_topic(self):
        """It returns repositories per topic of given user."""

    @property
    @abc.abstractmethod
    def forked_public_repos_count(self):
        """It returns count of forked and public repositories of given user."""

    @property
    @abc.abstractmethod
    def validate_username_url(self):
        """This property is used to validate the given url which includes username."""

    @property
    @abc.abstractmethod
    def open_issues_count(self):
        """This property is used to get the count of open issues."""

    @property
    @abc.abstractmethod
    def repositories_per_language(self):
        """It gives count of repositories with respect to languages user used."""

    @property
    @abc.abstractmethod
    def original_public_repos_count(self):
        """It returns count of original public repositories."""

    @property
    @abc.abstractmethod
    def stars_count(self):
        """It gives count of stars that user given to other repositories."""

    @property
    @abc.abstractmethod
    def received_star_count(self):
        """It gives count of stars that user got to his/her own repositories."""

    @abc.abstractmethod
    def get_next_link(self, response):
        """It's used to get next link of pagination."""
        pass

    def res_handler(self, response, acceptable_status_codes=(200,)):
        if response.status_code not in acceptable_status_codes:
            if response.status_code == 403:
                raise Exception('Error from HostService')
            else:
                raise profile_exceptions.APIError(f'Error response from hostservice while accessing {response.request.url}: {response.status_code}')
        return response

    def validate_username(self):
        response = self.res_handler(self._session.head(self.validate_username_url), (200, 404))
        if response.status_code == 404:
            raise profile_exceptions.ProfileNotFoundError(f'{self.username} profile do not exists')
        return True


class Bitbucket(HostService):
    base_url = 'https://api.bitbucket.org/2.0'

    @property
    def original_public_repos_count(self):
        return len([repo for repo in self.public_repos if not repo.get('parent')])

    @property
    def validate_username_url(self):
        return f'{self.base_url}/users/{self.username}'

    @property
    def forked_public_repos_count(self):
        return len([repo for repo in self.public_repos if repo.get('parent')])

    @property
    def stars_count(self):
        return 0

    @property
    def open_issues_count(self):
        try:
            open_issues_count = self.summaryObj['open_issues_count']
        except KeyError:
            for repo in self.public_repos:
                try:
                    if repo['has_issues']:
                        open_issues_count = sum(self.res_handler(self._session.get(repo['links']['issues']['href'], params={'fields': 'size', 'q': 'state="open"'})).json()['size'])
                except:
                    open_issues_count = 0
            self.summaryObj['open_issues_count'] = open_issues_count
        return open_issues_count

    @property
    def received_star_count(self):
        return 0

    @property
    def public_repos(self):
        '''Used to get public repositories of profile'''
        try:
            public_repos = self.summaryObj['public_repos']
        except KeyError:
            public_repos = []
            next_url = f'{self.base_url}/repositories/{self.username}'
            while next_url:
                response = self.res_handler(self._session.get(next_url, params={'pagelen': 100}))
                public_repos.extend(response.json()['values'])
                next_url = self.get_next_link(response)
            self.summaryObj['public_repos'] = public_repos
        return public_repos

    @property
    def repositories_per_language(self):
        languages = defaultdict(int)
        for repo in self.public_repos:
            languages[repo.get('language') or 'UNKNOWN'] += 1
        return languages

    @property
    def repositories_per_topic(self):
        return {}

    def get_next_link(self, response):
        try:
            return response.json()['next']
        except KeyError:
            return None


class GitHub(HostService):
    """Git hub summary"""
    base_url = 'https://api.github.com'

    @property
    def star_repo(self):
        '''Used to get starred repositories'''
        try:
            star_repo = self.summaryObj['star_repo']
        except KeyError:
            star_repo = []
            next_url = f'{self.base_url}/users/{self.username}/starred'
            while next_url:
                response = self.res_handler(self._session.get(next_url))
                star_repo.extend(response.json())
                next_url = self.get_next_link(response)
            self.summaryObj['star_repo'] = star_repo
        return star_repo

    @property
    def repositories_per_topic(self):
        topics = defaultdict(int)
        for repo in self.public_repos:
            for topic in repo.get('topics', ()):
                topics[topic] += 1

        return topics

    @property
    def forked_public_repos_count(self):
        return len([repo for repo in self.public_repos if repo['fork']])

    @property
    def count_followers(self):
        try:
            count_followers = self.summaryObj['count_followers']
        except KeyError:
            count_followers = 0
            next_url = f'{self.base_url}/users/{self.username}/followers'
            while next_url:
                rs = self.res_handler(self._session.get(next_url, params={'per_page': 100}))
                count_followers += len(rs.json())
                next_url = self.get_next_link(rs)
            self.summaryObj['count_followers'] = count_followers

        return count_followers

    @property
    def validate_username_url(self):
        '''To validate url using given user name'''
        return f'{self.base_url}/users/{self.username}'

    @property
    def public_repos(self):
        ''' Used to get public repositories'''
        try:
            public_repos = self.summaryObj['public_repos']
        except KeyError:
            public_repos = []
            next_url = f'{self.base_url}/users/{self.username}/repos'
            while next_url:
                response = self.res_handler(
                    self._session.get(next_url, headers={'Accept': 'application/vnd.github.mercy-preview+json'}))
                public_repos.extend(response.json())
                next_url = self.get_next_link(response)
            self.summaryObj['public_repos'] = public_repos
        return public_repos

    @property
    def open_issues_count(self):
        return sum(repo['open_issues_count'] for repo in self.public_repos)

    @property
    def repositories_per_language(self):
        languages = defaultdict(int)
        for repo in self.public_repos:
            languages[repo.get('language') or 'UNKNOWN'] += 1
        return languages

    @property
    def original_public_repos_count(self):
        return len([repo for repo in self.public_repos if not repo['fork']])

    @property
    def stars_count(self):
        '''count of stars'''
        return len(self.star_repo)

    @property
    def received_star_count(self):
        '''Count of stars received.'''
        return sum(repo['stargazers_count'] for repo in self.public_repos)

    def get_next_link(self, response):
        try:
            return response.links['next']['url']
        except KeyError:
            return None

