
# Chatbots using GPT from OpenAI and knowledge based on news articles

A project for the master thesis. This project uses:
* Python 3.10
* OpenAI API
* news articles of Bild.de and Spiegel.de

This project contains 3 parts: bild-gpt, spiegel-gpt and plain-gpt. All folders contain the scrapy project to scrape the news articles and the chatbot file to start the chatbot based on the specific news articles which were scraped by the scrapy spider.

## Deployment
Each project (not the plain-gpt) has 2 parts: the chatbot and the scraper for downloading the training data.
Therefore, we first want to crawl/scrape the needed articles from the online archive and save these articles in the folder where our chatbot will later find its training data.
After this is done, we want to feed chatbot with our pdf articles.

But first some pre-installments:
1. Create a virtual environment:
```bash
python -m venv /path/to/new/virtual/environment/venv
```

2. Start virtual environment
```bash
source venv/bin/activate
```

3. Install packages from `requirements.txt` by running :
```bash
pip install -r requirements.txt
```

### Scrapy
1. Go to the scrapy project directory e.g. `bild_archive_scraper`:
```bash
cd bild_archive_scraper
```

2. Start the scraper for the spider `bild-spider` / `spiegel-spider`:
```
scrapy crawl <spider-name>
```
Now there should be a folder named `training_set`. To filter these pdfs, there is a file in the `utils` folder to filter all the pdf files by searching for specific keywords. If needed, please run this file and modify the folder paths.

### Chatbot with OpenAI model
1. Add your OpenAI API key in the file `config.py`. For that duplicate the file `configTEMPLATE.py` and rename it to `config.py`: 
```bash
os.environ["OPENAI_API_KEY"] = 'YOUR API KEY'
```

2. Start deployment in terminal with following command:
```bash
python <file-name>.py
```
This will execute the `<file-name>.py` file with python and start the Gradio interface in your browser.
* Running on local URL:  http://127.0.0.1:7860

## Good2know

### Python basics

#### Create requirements.txt
```bash
pip install pipreqs
pipreqs /Users/username/projects/<name>-gpt
```

#### Activate venv
```bash
source venv/bin/activate
```

#### Deactivate venv
```bash
deactivate
```

#### List modules and packages in requirements.txt
```bash
pip freeze > requirements.txt
```

#### Install from requirements.txt
```bash
pip install -r requirements.txt
```


### Scrapy shell
Use the scrapy shell to test or debug things in your terminal.

#### Start scrapy shell with target URL:
```bash
scrapy shell 'YOUR TARGET URL'
```

#### Select elements using CSS with response object:
```bash
response.css("title")
```
_Example Output:_ `[<Selector query='descendant-or-self::title' data='<title>Quotes to Scrape</title>'>]`

```bash
response.css("title::text").getall()
```
_Example Output:_ `['Quotes to Scrape']`

```bash
response.css("title::text").get()
```
_Example Output:_ `'Quotes to Scrape'`

```bash
response.css("title::text")[0].get()
```
_Example Output:_ `'Quotes to Scrape'`

#### Using RegEx:

```bash
response.css("title::text").re(r"Quotes.*")
['Quotes to Scrape']

response.css("title::text").re(r"Q\w+")
['Quotes']

response.css("title::text").re(r"(\w+) to (\w+)")
['Quotes', 'Scrape']
```

#### Using XPaths:
```bash
response.xpath("//title")
[<Selector query='//title' data='<title>Quotes to Scrape</title>'>]
```

For this project we want all article links that are listed in the archive page. For each article the link can be found in the link tag of an article tag. To get a list of all links we use the xpath to the `href` of the link tag:
```bash
response.xpath('/html/body/div/div/div[3]/main/section/div/div[2]/section/ul/li/article/a/@href').getall()
```

#### Exit scrapy shell
```bash
exit()
```
 
## Authors

- [@kmnhngyn](https://www.github.com/kmnhngyn)

