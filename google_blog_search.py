from googlesearch import search
import openai
import requests
from bs4 import BeautifulSoup

client = openai.Client()


urls = search("RPGツクール", tld="jp", lang="ja", stop=255)

for url in urls:
    print(url)
    got = requests.get(url)

    # BS4
    soup = BeautifulSoup(got.text, "html.parser")

    bodytext = soup.find("body").get_text().replace("\n", "")

    print(bodytext)

    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "あなたは渡されたテキストが個人（会社でも）ブログかどうかを判断するAIです。"},
            {"role": "system", "content": "判断した結果は、0.0~1.0の間の数値で表してください。"},
            {"role": "user", "content": bodytext[0:1920]},
        ],
        model="gpt-4",
        max_tokens=2048,
    )
    print(completion.choices[0].message)
    # とりあえず1回だけ
    break
