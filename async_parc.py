from bs4 import BeautifulSoup
import json
import asyncio
from aiohttp import ClientSession


tel_numbers = []

headers = {
    "accept": "*/*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
}


async def parcer_numbers(link):
    # открываем сессию делаем запрос по переданной ссылке link (страница с объявлениями).
    async with ClientSession() as session:
        async with session.get(link) as response:
            response = await response.text()
            soup = BeautifulSoup(response, "lxml")

            # на странице с автомобилями находим все ссылки, ведущие на страницу конкретного объявления каждого авто,
            # в адресе содержится индивидуальный номер автомобиля
            id_link = soup.find_all(class_="listing-item__link")

        # забираем индивидуальный номер авто и формируем ссылки для запроса на сервер
        for i in id_link:
            id_auto = i.get("href").split("/")
            link_with_id = f"https://api.av.by/offers/{id_auto[-1]}/phones"

            # забираем номер телефона из приходящего json
            async with session.get(link_with_id, headers=headers) as auto_json:
                js = await auto_json.text()
                js = json.loads(js)
                if isinstance(js, list):
                    tel_numbers.append(f"{js[0]['country']['code']}{js[0]['number']}")


async def gather_data():
    # создаём список урлов, каждый урл - страница с 25 автомобилями
    links = []
    for number in range(1, int(input('Введите количество страниц: ')) + 1):
        links.append(
            f"https://cars.av.by/filter?place_city[0]=133&w[1]=141&place_city[2]=143&place_city[3]=145&place_city[4]=148&place_region[0]=1002&page={number}&sort=4")

    # формируем список задач
    tasks = []
    for page_with_links in links:
        task = asyncio.create_task(parcer_numbers(link=page_with_links))
        tasks.append(task)

    await asyncio.gather(*tasks)
    print(tel_numbers)


asyncio.run(gather_data())
