import csv
import requests


page = 1

with open('films.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Title','Year'])

    url = input("Please enter the watchlist URL")
    api_url = (
        "https://mubi.com/services/api/wishes?user_id={user_id}&page={page}&per_page=24"
    )
    user_id = url.split("/")[-2]

    while(True):
        data = requests.get(api_url.format(user_id=user_id, page = page)).json()
        if(len(data) == 0):
            break
        for x in data:
            title = x["film"]["title"]
            year =  x["film"]["year"]
            # print(data)
            writer.writerow([title, year])
            
        page = page +1
    
