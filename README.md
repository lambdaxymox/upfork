# Upfork

## Introduction
**upfork** is a python program for automatically batch updating git repository forks.

## Getting Started
To use **upfork**, fork this repository. You have two options to use it.
If you want to run the script from the git repository, enter

```
python -m upfork <action> <parameters> </path/to/git/repository/folder>
```

where `<action>` is either `list`, `update-local`, or `update-remote`.

Alternatively, you can build and install **upfork** using a build tool such 
as **pep517** as follows

```
python -m pep517.build .
pip install .
```

and the call the program directly via

```
upfork <action> <parameters> </path/to/git/repository/folder>
```

## Usage
**upfork** has three available commands. The **list** command searches a directory 
for git repositories. The **update-local** command synchronizes local forks with 
the most recent version. The **update-remote** command synchronizes the remote 
copy of a fork with the updated local copy of a fork.

## Workflows
There are several major workflows this program is intended for.

### Finding Git Repositories
Use the **list** command to discover git repositories in a directory.

```
upfork list /path/to/git/repository/directory
```

### Update All Local Copies Of Git Repositories
Use the **update-local** command to update local copies of git repositories in 
a directory.

```
upfork update-local /path/to/git/repository/directory
```

### Update All Remote Copies Of Git Repositories
Use a combination of the **update-local** command and the **update-remote** 
command to synchronize local forks and remote forks with the original source 
repository.

```
upfork update-local /path/to/git/repository/directory
upfork update-remote --username USERNAME --password PASSWORD_OR_PERSONAL_ACCESS_TOKEN /path/to/git/repository/directory
```
