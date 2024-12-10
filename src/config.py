import os

repository_owner = os.environ['GITHUB_REPOSITORY_OWNER']
repository_owner_type = os.environ['INPUT_REPOSITORY_OWNER_TYPE']

server_url = os.environ['GITHUB_SERVER_URL']
is_enterprise = True if os.environ.get('INPUT_ENTERPRISE_GITHUB') == 'True' else False
dry_run = True if os.environ.get('INPUT_DRY_RUN') == 'True' else False

gh_token = os.environ['INPUT_GH_TOKEN']
project_number = int(os.environ['INPUT_PROJECT_NUMBER'])
api_endpoint = os.environ['GITHUB_GRAPHQL_URL']

comments_issue_number = 0 if os.environ.get('INPUT_COMMENTS_ISSUE_NUMBER') == 'False' else int(os.environ.get('INPUT_COMMENTS_ISSUE_NUMBER'))
comments_issue_repo = False if os.environ.get('INPUT_COMMENTS_ISSUE_REPO') == 'False' else os.environ.get('INPUT_COMMENTS_ISSUE_REPO')
