from pathlib import Path
from googlesearch import search, get_tbs
import openai
import requests
from bs4 import BeautifulSoup
import json
import argparse
import time
import datetime


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("WORD", help="Search word")
    parser.add_argument("-s", "--start", help="Start Index of search", default=0)
    parser.add_argument("-l", "--limit", help="Limit of search", default=20)
    args = parser.parse_args()
    word = args.WORD

    client = openai.Client()

    urls = search(
        f'"{word}" ブログ',
        tld="jp",
        lang="ja",
        start=int(args.start),
        stop=(int(args.start) + int(args.limit)),
        pause=1.0,
        country="ja",
        tbs=get_tbs(
            datetime.date(datetime.date.today().year, 1, 1),
            datetime.date(datetime.date.today().year, 12, 31),
        ),
    )

    if not Path(f"./dist/{word}.tsv").exists():
        with open(f"./dist/{word}.tsv", mode="w") as f:
            f.write("url\tpoint\n")

    for i, url in enumerate(urls):
        time.sleep(0.1)
        print(f"{i+1}/{args.limit} {url}")
        # print(url)
        got = ""
        try:
            got = requests.get(url, timeout=10)
        except:
            continue

        # BS4
        soup = BeautifulSoup(got.text, "html.parser")

        bodytext = soup.find("body").get_text().replace("\n", "")

        if bodytext == "":
            bodytext = "error"
            continue

        # print(bodytext)

        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "あなたは渡されたテキストが個人（会社でも）ブログかどうかを判断するAIです。"},
                {"role": "system", "content": "判断した結果は、0.0~1.0の間の数値で表してください。"},
                {
                    "role": "system",
                    "content": "'エラー'や'error'や'空白'が渡された場合は、0.0を出力してください。",
                },
                {"role": "system", "content": "JSON{like_blog_or_not: 0.5}"},
                {"role": "user", "content": bodytext[0:1920]},
            ],
            model="gpt-4-1106-preview",
            max_tokens=2048,
            response_format={"type": "json_object"},
            timeout=60,
        )
        # print(completion.choices[0].message)
        point_dump = completion.choices[0].message.model_dump()

        # print(point_dump)

        pointJ = json.loads(point_dump["content"])
        point = pointJ["like_blog_or_not"]
        print(point)
        with open(f"./dist/{word}.tsv", mode="a") as f:
            f.write(f"{url}\t{point}\n")


main()
