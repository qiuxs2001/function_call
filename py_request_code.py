import requests

if __name__ == '__main__':
    uri = "https://img-s.msn.cn/tenant/amp/entityid/AA1I53Wy.img?w=534&h=282&m=6"

    response = requests.get(uri)

    if response.status_code == 200:
        with open('image.jpg', 'wb') as f:
            f.write(response.content)
    else:
        print('Error: ', response.status_code)