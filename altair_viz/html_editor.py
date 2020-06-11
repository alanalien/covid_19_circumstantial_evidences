from bs4 import BeautifulSoup

with open('index.html', 'r') as my_page:
    soup = BeautifulSoup(my_page, features='lxml')

# update style settings
my_head = soup.head
new_style = soup.new_tag('style')
new_style.string = "<style>.error {color: red;}body {margin: auto;background: #111111;}p {float: left;font-family: 'Helvetica';width: 500px;color: #FFFFFF;margin-top: 30px;margin-left: 55px;margin-bottom: 0px;}h1 {float: left;font-size: 52pt;font-weight: bold;font-family: 'Helvetica';color: #FFFFFF;margin-top: 25px;margin-left: 60px;margin-bottom: 0px;}#vis {margin: auto;}</style>"

soup.head.style.replace_with(new_style)

# print(soup.head)


# insert title and intro texts


