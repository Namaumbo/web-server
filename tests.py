import  requests

res = requests.get('https://api.github.com',headers)

print(res.headers)