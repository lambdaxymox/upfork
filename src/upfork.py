import collections
import os
import os.path
import subprocess
import sys


Repository  = collections.namedtuple('Repository', ['name', 'origin', 'myorigin'])

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


def get_git_url_by_name(name):
    result = subprocess.run(
        ['git', 'remote', 'get-url', name], 
        capture_output=True, 
        text=True
    )
    if result.returncode == 0:
        return result.stdout.rstrip()
    else:
        raise ValueError(f'The git repository does not have a URL named {name}')


def scan_repo_root(repo_root):
    owd = os.getcwd()
    os.chdir(repo_root)
    repos = dict(
        repo_root = repo_root,
        repos = {}
    )
    for name in (name for name in os.listdir('.') if is_git_repo(name)):
        os.chdir(name)
        try:
            origin_url = get_git_url_by_name('origin')
        except ValueError:
            origin_url = ''
        
        try:
            myorigin_url = get_git_url_by_name('myorigin')
        except ValueError:
            myorigin_url = ''

        repo = Repository(name, origin_url, myorigin_url)
        repos['repos'][name] = repo
        
        os.chdir('..')

    os.chdir(owd)

    return repos


def usage():
    return 'USAGE: upfork /path/to/git/repository/forks/'


def main():
    if len(sys.argv) < 2:
        sys.exit(usage())

    repo_root = sys.argv[1]
    
    if not os.path.exists(repo_root):
        sys.exit(f'Path does not exist: {repo_root}')
    
    repos = scan_repo_root(repo_root)
    for repo in repos['repos'].values():
        repo_path = os.path.join(repo_root, repo.name)
        print(f'REPO: {repo_path}')
        print(f'ORIGIN: {repo.origin}')
        print(f'MYORIGIN: {repo.myorigin}')

    print(len(repos['repos']))


if __name__ == 'main':
    main()
else:
    main()

