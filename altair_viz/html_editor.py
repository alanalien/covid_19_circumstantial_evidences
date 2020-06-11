from bs4 import BeautifulSoup
from datetime import datetime

# read altair generated html
with open('altair_viz/new_viz.html', 'r') as my_page:
    viz_soup = BeautifulSoup(my_page, features='lxml')
# read in formerly-set html layout
with open('temp/base_html.html', 'r') as my_page:
    index_soup = BeautifulSoup(my_page, features='lxml')

# get the script part from viz html
my_script = viz_soup.body.script

# them replace base html's script tag with it
index_soup.body.script.replace_with(my_script)
# insert today's time to footer
time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
index_soup.footer.span.insert(0, time_now)

# write the new soup to index.html
with open('index.html', 'w') as new_html:
    new_html.write(str(index_soup))


print('\n\n\n ################## new_viz.html has been modified ################## \n\n\n')

