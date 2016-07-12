import os
import argparse
from git import Repo


git = os.environ.get("GIT_PYTHON_GIT_EXECUTABLE", 'git')


execute = lambda repo, params: repo.git.execute([git] + params.split())


def merge_squash(source, target, path):
    join = os.path.join
    repo = Repo(join(path))
    repo.heads[target].checkout()
    if is_merged(source, target, repo):
        drop_merge_commit(source, target, repo)
    repo.git.execute([git, 'merge', '--squash', source])


def is_merged(source, target, repo):
    repo.heads[target].checkout()
    branches = repo.git.branch("--merged").split()
    return source in branches


def drop_merge_commit(source, target, repo):
    repo.heads[target].checkout()
    command = 'log {} ^{} --ancestry-path --oneline'.format(target, source)

    merge_commit = execute(repo, command).split()[0]

    parent_commit = execute(repo, 'rev-list --parents -n 1 {}'.format(merge_commit)).split()[1]

    command = 'rev-list ^{} {}..HEAD --no-merges --reverse'.format(source, parent_commit)
    cherry_pick_commits = execute(repo, command).split()

    execute(repo, 'reset --hard {}'.format(parent_commit))
    [execute(repo, 'cherry-pick {}'.format(commit)) for commit in cherry_pick_commits]

    
if  __name__ ==  "__main__" :
    parser = argparse.ArgumentParser(description='Merge to branch with option squash')
    parser.add_argument('source', type=str, help='source branch')
    parser.add_argument('target', type=str, help='target branch')
    parser.add_argument('--path', type=str, help='path to git repo')

    args = parser.parse_args()
    merge(args.source, args.target, args.path)
