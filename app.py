from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.boxofficemojo.com/year/world/')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('div', attrs={'class':'a-section imdb-scroll-table-inner'})
table_all = table.find_all('td', attrs={'class','a-text-right mojo-header-column mojo-truncate mojo-field-type-rank mojo-sort-column'})

row_length = len(table_all)

money_elements = table.find_all('td', attrs='a-text-right mojo-field-type-money')
if len(money_elements) >= 3:
    worldwide = money_elements[0].text.strip()
    domestic = money_elements[1].text.strip()
    foreign = money_elements[2].text.strip()

temp = [] #initiating a list 

for i in range(0, row_length):
#insert the scrapping process here
    
    # Get Rank
    rank = table.find_all('td', attrs='a-text-right mojo-header-column mojo-truncate mojo-field-type-rank mojo-sort-column')[i].text.strip()

    # Get Release Group
    release_group = table.find_all('td', attrs='a-text-left mojo-field-type-release_group')[i].text.strip()

    # Get Worldwide
    worldwide = money_elements[i*3].text.strip().replace('$', '')

    # Get Domestic
    domestic = money_elements[i*3 + 1].text.strip().replace('$', '')

    # Get Domestic
    foreign = money_elements[i*3 + 2].text.strip().replace('$', '')
    
    temp.append((rank, release_group, worldwide, domestic, foreign))

temp = temp[::-1]

#change into dataframe
data = pd.DataFrame(temp, columns = ('Rank', 'Release Group', 'Worldwide', 'Domestic', 'Foreign'))

#insert data wrangling here
data = data.replace(',','', regex=True)
data[['Domestic','Foreign']] = data[['Domestic','Foreign']].replace({'-': '0'}, regex=True)
data['Rank'] = data['Rank'].astype('int64')
data['Worldwide'] = data['Worldwide'].astype('int64')
data['Domestic'] = data['Domestic'].astype('int64')
data['Foreign'] = data['Foreign'].astype('int64')

data_top10 = data.sort_values('Rank').head(10)

data_top10['Domestic Percentage'] = data_top10['Domestic'] / data_top10['Worldwide'] * 100
data_top10['Foreign Percentage'] = data_top10['Foreign'] / data_top10['Worldwide'] * 100

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'US$ {data_top10["Worldwide"].sum().round(2):,}' #be careful with the " and ' 

	# generate plot number 1
	# ax = data.plot(figsize = (20,9))
	colors = ['skyblue', 'coral']
	data_top10.plot(x="Release Group", y=["Domestic", "Foreign"], kind="bar", stacked=True, color=colors)
	plt.title("2024 Top 10 Box Office Earnings")
	plt.ylabel("Earnings (in $ Billions)")
	plt.xticks(rotation=45, ha='right')
	plt.tight_layout()
	plt.show() 
	
	# Rendering plot number 1
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# Generate plot number 2
	colors = ['skyblue', 'coral']
	data_top10.plot(x="Release Group", y=["Domestic Percentage", "Foreign Percentage"], kind="bar", stacked=True, color=colors)
	plt.title(" 2024 Top 10 Box Office Earnings (Domestic vs Foreign %)")
	plt.ylabel("Percentage of Earnings")
	plt.xticks(rotation=45, ha='right')
	plt.tight_layout()
	plt.show()
	
	# Rendering plot number 2
	# Do not change this
	figfile2 = BytesIO()
	plt.savefig(figfile2, format='png', transparent=True)
	figfile2.seek(0)
	figdata_png2 = base64.b64encode(figfile2.getvalue())
	plot_result2 = str(figdata_png2)[2:-1]
	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result,
        plot_result2=plot_result2
		)


if __name__ == "__main__": 
    app.run(debug=True)