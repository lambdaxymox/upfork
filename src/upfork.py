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


class Command:
    def __init__(self, command, repository_root, username='', password=''):
        self.command = command
        self.repository_root = repository_root
        self.useranme = username
        self.password = password

    def is_list(self):
        return self.command == 'list'

    def is_update_local(self):
        return self.command == 'update-local'

    def is_update_remote(self):
        return self.command == 'update-remote'


def is_git_repo(name):
    owd = os.getcwd()
    ret = None
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

    assert ret is not None
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
        
        os.chdir(os.path.pardir)

    os.chdir(owd)

    return RepositorySet(repository_root, repositories)


def usage():
    return ''.join((
        'USAGE:\n',
        'List the git repositories in a directory\n',
        '`upfork list /path/to/git/repository/forks/`\n',
        'Update the local copies of the git repositories in a directory\n',
        '`upfork update-local /path/to/git/repository/forks/`\n',
        'Update the remote copies of the git repositories in a directory\n',
        '`upfork update-remote --username=USERANME --password=PASSWORD /path/to/git/repository/forks/`\n'
    ))


def parse_args(args):
    if args[1] == 'list':
        return Command(args[1], args[2])
    elif args[1] == 'update-local':
        return Command(args[1], args[2])
    elif args[1] == 'update-remote':
        raise NotImplementedError
    else:
        raise ValueError(f'The argument `{args[1]}` is not a valid command name.')


def run_list(repository_set):
    print(f'Found {len(repository_set.repositories)} Git repositories in `{repository_set.repository_root}`\n')
    for repo in repository_set.repositories.values():
        repo_path = os.path.join(repository_set.repository_root, repo.name)
        print(f'Repository: {repo_path}')
        print(f'Origin: {repo.origin_url}')
        print(f'Remote URLs: {repo.remote_urls}\n')



def run_update_local(repository_set):
    def git_pull():
        return subprocess.run(
            ['git', 'pull', 'origin'], 
            capture_output=True, 
            text=True
        )
        
    owd = os.getcwd()
    os.chdir(repository_set.repository_root)
    for repository in repository_set.repositories:
        os.chdir(repository.name)
        result = git_pull()
        if result.returncode != 0:
            print(f'An error occurred in updating {repository.name}')
            print(f'{result.stderr}')
            print(f'{result.stdout}')

        os.chdir(os.path.pardir)

    os.chdir(owd)


def run_update_remote(repository_set, credentials):
    raise NotImplementedError


def run_command(command, repository_set):
    if command.is_list():
        run_list(repository_set)
    elif command.is_update_local():
        run_update_local(repository_set)
    elif command.is_update_remote():
        run_update_remote(
            repository_set, dict(
                username=command.username, 
                password=command.password
            )
        )
    else:
        raise ValueError(f'The command name `{command.command}` is not a valid command name.')


def main():
    if len(sys.argv) < 3:
        sys.exit(usage())

    command = parse_args(sys.argv)

    if not os.path.exists(command.repository_root):
        sys.exit(f'Path does not exist: {command.repository_root}')
                         
    repository_set = scan_repository_root(command.repository_root)
    run_command(command, repository_set)


if __name__ == '__main__':
    main()
else:
    main()

