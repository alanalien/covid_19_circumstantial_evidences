import os
import subprocess as cmd
import sys
sys.path.append('/Users/wildgoose/PycharmProjects/covid_19_CE')

from data_post import git_update as update


os.chdir('/Users/wildgoose/PycharmProjects/covid_19_CE')

cmd.run('python data_get/all_data_get.py', shell=True)
cmd.run('python altair_viz/viz_gen.py', shell=True)

update.auto_commit()
