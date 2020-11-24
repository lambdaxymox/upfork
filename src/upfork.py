import os
import os.path
import subprocess
import sys


class Repository:
    def __init__(self, name, origin_url, remote_urls):
        self.name = name
        self.origin_url = origin_url
        self.remote_urls = remote_urls



def is_git_repo(name):
    owd = os.getcwd()
    ret = False
    if os.path.isdir(name):
        os.chdir(name)
        result = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            ret = True
        else:
            ret = False    
    else:
        ret = False

    os.chdir(owd)

    return ret


def get_url_by_label(label):
    result = subprocess.run(
        ['git', 'remote', 'get-url', label], 
        capture_output=True, 
        text=True
    )
    if result.returncode == 0:
        return result.stdout.rstrip()
    else:
        raise ValueError(f'The git repository does not have a URL named {label}')


def remote_url_labels():
    result = subprocess.run(
        ['git', 'remote'],
        capture_output=True,
        text=True
    )
    remote_labels = result.stdout.rstrip().split('\n')

    return remote_labels


def remote_urls(labels, exclude=['origin']):
    urls = {}
    for label in (label for label in labels if label not in exclude):
        try:
            url = get_url_by_label(label)
        except ValueError:
            url = ''

        urls[label] = url

    return urls
 

def scan_repo_root(repository_root):
    owd = os.getcwd()
    os.chdir(repository_root)
    repositories = dict(
        repository_root = repository_root,
        repositories = {}
    )
    for name in (name for name in os.listdir('.') if is_git_repo(name)):
        os.chdir(name)
        try:
            origin_url = get_url_by_label('origin')
        except ValueError:
            origin_url = ''
        
        labels = remote_url_labels()
        urls = remote_urls(labels)

        repo = Repository(name, origin_url, urls)
        repositories['repositories'][name] = repo
        
        os.chdir('..')

    os.chdir(owd)

    return repositories


def usage():
    return 'USAGE: upfork [list | update-local | update-remote] /path/to/git/repository/forks/'


def main():
    if len(sys.argv) < 2:
        sys.exit(usage())

    repo_root = sys.argv[1]
    
    if not os.path.exists(repo_root):
        sys.exit(f'Path does not exist: {repo_root}')
                         
    repos = scan_repo_root(repo_root)
    for repo in repos['repositories'].values():
        repo_path = os.path.join(repo_root, repo.name)
        print(f'REPO: {repo_path}')
        print(f'ORIGIN: {repo.origin_url}')
        print(f'MYORIGIN: {repo.remote_urls}')

    print(len(repos['repositories']))


if __name__ == 'main':
    main()
else:
    main()

