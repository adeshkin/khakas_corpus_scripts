from bs4 import BeautifulSoup

html_content = """
<b>КИЗІН 1.</b> задний;<b> аттың кизін азағы </b>задние ноги лошади;<b> кизін терпектер </b>задние колёса<i> (телеги);
</i><span variant="smallcaps"> 2.</span> назад; <b>кизін</b><span variant="smallcaps"> <b></b></span><b>одырарға</b> садиться назад.
"""

soup = BeautifulSoup(html_content, 'html.parser')

for span in soup.find_all("span", variant="smallcaps"):
    span.unwrap()

cleaned_text = str(soup)
print(cleaned_text)