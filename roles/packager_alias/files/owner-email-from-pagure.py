#!/usr/bin/python -tt

"""
This script is ran as a cronjob and bastion.

Its goal is to generate all the <pkg>-owner email aliases we provide
"""

import requests

# TODO: Change me
pagure_url = 'http://127.0.0.1:5000'
pagure_group_url = pagure_url + '/api/0/group/{group}'
pagure_projects_url = pagure_url + '/api/0/projects'
pagure_projects = requests.get(pagure_projects_url).json()['projects']
project_to_email = {}

for project in pagure_projects:
    users = set(project['access_users']['owner']) | \
            set(project['access_users']['admin']) | \
            set(project['access_users']['commit'])
    groups = set()
    for group_kind in ('admin', 'commit'):
        for group in project['access_groups'][group_kind]:
            groups.add(group)

    for group in groups:
        group_members = requests.get(
            pagure_group_url.format(group=group)).json()['members']
        users = users | set(group_members)

    project_alias = '{0}-owner'.format(project['name'])
    # If there is a namespace, prefix the email with it plus a dash
    if project['namespace'] and project['namespace'] != 'rpms':
        project_alias = '{0}-{1}'.format(project['namespace'], project_alias)

    # Use the @fedoraproject.org email alias instead of looking their email up
    # in FAS
    project_to_email[project_alias] = \
        ['{0}@fedoraproject.org'.format(user) for user in users]

for project_alias, emails in project_to_email.items():
    print('{0}: {1}'.format(project_alias, ','.join(sorted(emails))))
