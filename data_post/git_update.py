def auto_commit(content="data", comment="'data daily auto update'", add=False):
    """
    this function commit and push changes to the github repository
    :param content: string, directory or file name
    :param comment: string, the commit comments
    :param add: boolean, whether or not allow adding new files
    """
    import subprocess as cmd
    # add files if allowed
    if add is True:
        to_add = "git commit ./" + content
        cmd.run(to_add, check=True, shell=True)
    else:
        pass
    # then try to commit updated files
    try:
        to_commit = "git commit ./" + content + " -m " + comment
        cmd.run(to_commit, check=True, shell=True)
    # pass if nothing to commit
    except:
        pass

    # push the changes to remote repository
    cmd.run("git push -u origin master -f", check=True, shell=True)

