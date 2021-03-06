import pexpect
import argparse
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


class Credentials:
    def __init__(self, username, password):
        self.username = username
        self.password = password


class Command:
    def __init__(self, name, repository_root, username='', password=''):
        self.name = name
        self.repository_root = repository_root
        self.credentials = Credentials(username, password)

    def is_list(self):
        return self.name == 'list'

    def is_update_local(self):
        return self.name == 'update-local'

    def is_update_remote(self):
        return self.name == 'update-remote'



def is_git_repo(name):
    old_working_dir = os.getcwd()
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

    os.chdir(old_working_dir)

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
    old_working_dir = os.getcwd()
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

    os.chdir(old_working_dir)

    return RepositorySet(repository_root, repositories)


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
        
    old_working_dir = os.getcwd()
    os.chdir(repository_set.repository_root)
    for repository in repository_set.repositories.values():
        os.chdir(repository.name)
        result = git_pull()
        if result.returncode == 0:
            print(f'The repository `{repository.name}` has been updated successfully.')
        else:
            print(f'An error occurred in updating the repository `{repository.name}`')
            print(f'{result.stderr}')
            print(f'{result.stdout}')

        os.chdir(os.path.pardir)

    os.chdir(old_working_dir)


def run_update_remote(repository_set, credentials):
    def git_push(label):
        return pexpect.run(
            f'git push {label} --all', 
            withexitstatus=1, 
            events={
                '(?i)Username for': f'{credentials.username}\n', 
                '(?i)Password for': f'{credentials.password}\n'
            }
        )
        
    old_working_dir = os.getcwd()
    os.chdir(repository_set.repository_root)
    for repository in repository_set.repositories.values():
        os.chdir(repository.name)
        for label, remote_url in repository.remote_urls.items():
            command_output, exit_status = git_push(label)
            if exit_status == 0:
                print(
                    f'The remote copy of repository of `{repository.name}` with ' 
                    f'the name `{label}` and the URL `{remote_url}` has been '
                    f'updated successfully.'
                )
            else:
                print(
                    f'An error occurred in updating the remote copy of the '
                    f'repository `{repository.name}` to the URL named `{label}` at URL `{remote_url}`.'
                )
                print(command_output)

        os.chdir(os.path.pardir)

    os.chdir(old_working_dir)


def run_command(command, repository_set):
    if command.is_list():
        run_list(repository_set)
    elif command.is_update_local():
        run_update_local(repository_set)
    elif command.is_update_remote():
        run_update_remote(repository_set, command.credentials)
    else:
        raise ValueError(f'The command name `{command.name}` is not a valid command.')


def arg_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        title='subcommands', 
        description='valid subcommands', 
        help='subcommand help'
    )

    # Subparser for the list command.
    parser_list = subparsers.add_parser(
        'list', 
        help='Search a directory for git repositories'
    )
    parser_list.add_argument(
        'path', type=str,
        help='The path to the git repository directory'
    )

    # Subparser for the update-local command.
    parser_update_local = subparsers.add_parser(
        'update-local', 
        help='Update the local copies of each git repository'
    )
    parser_update_local.add_argument(
        'path', type=str,
        help='The path to the git repository directory'
    )

    # Subparser for the update-remote command.
    parser_update_remote = subparsers.add_parser(
        'update-remote', 
        help='Update the remote copies of each git repository'
    )
    parser_update_remote.add_argument(
        '-u', '--username',
        help='Username for remote git repositories'
    )
    parser_update_remote.add_argument(
        '-p', '--password',
        help='Password or personal access token for remote git repositories'
    )
    parser_update_remote.add_argument(
        'path', type=str,
        help='The path to the git repository directory'
    )

    return parser


def parse_args(args): 
    command_args = arg_parser().parse_args(args[1:])
    if args[1] == 'list':
        path = command_args.path
        return Command(args[1], path)
    elif args[1] == 'update-local':
        path = command_args.path
        return Command(args[1], path)
    elif args[1] == 'update-remote':
        username = command_args.username
        password = command_args.password
        path = command_args.path
        return Command(args[1], path, username, password)
    else:
        raise ValueError(f'The argument `{args[1]}` is not a valid command name.')


def usage():
    return ''.join((
        'USAGE:\n',
        'List the git repositories in a directory\n',
        '`upfork list /path/to/git/repository/forks/`\n',
        'Update the local copies of the git repositories in a directory\n',
        '`upfork update-local /path/to/git/repository/forks/`\n',
        'Update the remote copies of the git repositories in a directory\n',
        '`upfork update-remote /path/to/git/repository/forks/`\n'
    ))


def main():
    if len(sys.argv) < 3:
        sys.exit(usage())

    try:
        command = parse_args(sys.argv)
    except:
        sys.exit(usage())

    if not os.path.exists(command.repository_root):
        sys.exit(f'Path does not exist: {command.repository_root}')
                         
    repository_set = scan_repository_root(command.repository_root)
    run_command(command, repository_set)

