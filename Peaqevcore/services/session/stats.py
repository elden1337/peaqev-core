# import requests
# import json
# from dataclasses import dataclass

# @dataclass
# class StatsModel:
#     identifier: str
#     version: str
#     type: int
#     chargertype: str
#     locale: str
#     priceaware: bool

# class Api:
#     api_url = "https://jsonplaceholder.typicode.com/todos/1"
#     headers =  {"Content-Type":"application/json"}

#     def post(self, _postdata: StatsModel) -> None:        
#         requests.post(self.api_url, data=json.dumps(_postdata), headers=self.headers)
