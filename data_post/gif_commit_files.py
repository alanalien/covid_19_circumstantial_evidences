import subprocess as cmd


# commit changed files on data directory
def auto_commit(content="data", comment="'data daily auto update'", add=True):
    to_commit = "git commit ./" + content + " -m " + comment
    cmd.run(to_commit, check=True, shell=True)
    # push the changes to remote repository
    cmd.run("git push -u origin master -f", check=True, shell=True)
    if add is True:
        cmd.run("git add .", check=True, shell=True)
    else:
        pass
