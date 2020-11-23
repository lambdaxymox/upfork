import subprocess
import sys
import os
import os.path


def get_git_url_by_name(name):
    result = subprocess.run(['git', 'remote', 'get-url', f'{name}'])
    if result.returncode > 0:
        return result.stdout
    else:
        raise ValueError(f'The git repository does not have a URL named {name}')

def usage():
    return 'USAGE: upfork /path/to/git/repository/forks/'

def main():
    if len(sys.argv) < 2:
        sys.exit(usage())

    repo_path = sys.argv[1]
    
    if not os.path.exists(repo_path):
        sys.exit(f'Path does not exist: {repo_path}')
    
    print(f'Entering path {repo_path}')
    os.chdir(repo_path)
    for path in (path for path in os.listdir('.') if os.path.isdir(path)):
        os.chdir(path)
        try:
            origin_url = get_git_url_by_name('origin')
        except ValueError:
            print(f'The git repository {path} does not have URL \'origin\'.')
            origin_url = ''
        
        try:
            myorigin_url = get_git_url_by_name('myorigin')
        except ValueError:
            print(f'The git repository {path} does not have URL \'myorigin\'.')
            myorigin_url = ''

        print(f'ORIGIN: {origin_url}')
        print(f'MYORIGIN: {myorigin_url}')
        os.chdir('..')

    print('DONE!')
        



if __name__ == '__main__':
    main()

