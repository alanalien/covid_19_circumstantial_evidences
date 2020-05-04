import subprocess as cmd

# commit changed files on data directory
cmd.run("git commit ./data -m 'data daily auto update'", check=True, shell=True)
# push the changes to remote repository
cmd.run("git push -u origin master -f", check=True, shell=True)