import git

repo = git.Repo('.')

commits = list(repo.iter_commits('master'))
names = map(lambda x: x.parents, commits)

print names
