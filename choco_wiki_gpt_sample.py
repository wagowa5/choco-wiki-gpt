import openai
import json
import requests
import ScrapBoxClient

# APIキーを設定する
#openai.organization = 
openai.api_key = "YOUR_TOKEN"
#openai.Model.list()


# ScrapBoxのAPIクライアント
scrapboxApi = ScrapBoxClient.ScrapboxAPI("chottomemo-public")

# 全文検索
#search_results = api.full_text_search("your_query")
#print(search_results)

# プロジェクト情報を取得
#project_info = api.get_project_info()
#print(project_info)


# GPT Test
user_prompt = "「連撃の真髄」の倍率表をください"
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0613",
    messages=[{"role": "user", "content": user_prompt}],
    functions=[
        {
            "name": "get_page_text",
            "description": "wikiから情報を取得する",
            "parameters": {
                "type": "object",
                "properties": {
                    "pagename": {
                        "type": "string",
                        "description": "ページの名前",
                    }
                },
                "required": ["pagename"],
            },
        }
    ],
    function_call="auto",
)

print(response)


message = response["choices"][0]["message"]
if message.get("function_call"):
    function_name = message["function_call"]["name"]
    # MEMO: 本来は JSON パースに失敗した場合を考慮します
    arguments = json.loads(message["function_call"]["arguments"])
    print()
    print("function_name: " + str(function_name))
    print("arguments: " + str(arguments))
    print(arguments.get("location"))
    print(arguments.get("unit", "fahrenheit"))
    print()

    if function_name != "":
        print("call:" + function_name + "(" + 'arguments.get("pagename")' + ")")
        # TODO ここ
        data = scrapboxApi.get_page_text(arguments.get("pagename"))
        print(data)
        
        if(data[1]):
          texts = [line['text'] for line in data[0]['lines']]

          for text in texts:
            print(text)
          function_response = str(text)
        else:
          function_response = str(data[0])

        #eval(function_name + "(" + 'arguments.get("pagename")' + ")")
        print(function_response)
        print()
    else:
        raise Exception(f"invalid function name: {function_name}")

    # 関数結果と過去のチャット履歴を送る
    second_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {"role": "user", "content": user_prompt},
            message,
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            },
        ],
    )
    print(second_response)

    print(second_response["choices"][0]["message"]["content"])
