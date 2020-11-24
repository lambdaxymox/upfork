import os
import os.path
import subprocess
import sys


class RepositorySet:
    def __init__(self, repository_root, repositories):
        self.repository_root = repository_root
        self.repositories = repositories


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
 

def scan_repository_root(repository_root):
    repositories = {}
    owd = os.getcwd()
    os.chdir(repository_root)
    for name in (name for name in os.listdir(repository_root) if is_git_repo(name)):
        os.chdir(name)
        try:
            origin_url = get_url_by_label('origin')
        except ValueError:
            origin_url = ''
        
        labels = remote_url_labels()
        urls = remote_urls(labels)

        repository = Repository(name, origin_url, urls)
        repositories[name] = repository
        
        os.chdir('..')

    os.chdir(owd)

    return RepositorySet(repository_root, repositories)


def usage():
    return 'USAGE: upfork list /path/to/git/repository/forks/'


class Command:
    def __init__(self, command, repository_root):
        self.command = command
        self.repository_root = repository_root


def parse_args(args):
    if args[1] == 'list':
        return Command(args[1], args[2])
    else:
        raise ValueError()


def main():
    if len(sys.argv) < 3:
        sys.exit(usage())

    command = parse_args(sys.argv)
    repository_root = command.repository_root

    if not os.path.exists(repository_root):
        sys.exit(f'Path does not exist: {repository_root}')
                         
    repos = scan_repository_root(repository_root)
    for repo in repos.repositories.values():
        repo_path = os.path.join(repository_root, repo.name)
        print(f'REPO: {repo_path}')
        print(f'ORIGIN: {repo.origin_url}')
        print(f'MYORIGIN: {repo.remote_urls}')

    print(len(repos.repositories))


if __name__ == 'main':
    main()
else:
    main()

