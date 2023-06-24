from bs4 import BeautifulSoup
import re
import json
import requests

# https://www.compareraja.in/search?c=all&q=iphone-11


def scrapeCompareRaja(query):
    url = 'https://www.compareraja.in/search?c=all&q=' + \
        query.replace(' ', '-')
    print(url)
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    products = soup.find(
        'div', {'class': 'prodcut-listing'}).find_all('article', {'class': 'product'})
    results = []
    for product in products:
        data = {}
        title = product.select_one('.prodcut-detail .link').text.strip()
        # Extract the ID from the URL
        url = product.select_one('.prodcut-detail .link')['href']
        id_ = url.split('/')[-1].split('.')[0]
        # Extract the image URL
        image = product.select_one('.prodcut-detail img')['src']
        # Extract the number of stores by finding the span with text 'stores'
        stores = product.find_all('span', text=re.compile('stores'))[
            0].text.strip('()').replace('stores', '').strip()
        # Extract the price
        price = product.select_one(
            '.prodcut-detail b').text.strip().split(' ')[-1].strip()
        # Extract the points as a dictionary
        points = []
        ul = product.select_one('.search-prdct-sumry ul')
        lis = ul.find_all('li')
        for li in lis:
            points.append(li.text.strip())
        data['title'] = title
        data['url'] = url
        data['id'] = id_
        data['image'] = image
        data['stores'] = stores
        data['price'] = price
        data['points'] = points
        results.append(data)
    print(len(results))
    return results


def scrapeDetailPage(url):
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    product_data = {}
    title = soup.find('h1', {'class': 'heading1'}).text.strip()
    image = soup.find(
        'a', {'class': 'simpleLens-lens-image'}).find('img')['src']
    points = []
    ul = soup.find('ul', {'class': 'nexmob-lst-nw'})
    lis = ul.find_all('li')
    for li in lis:
        points.append(li.text.strip())
    data = []
    listings = soup.find('div', {'class': 'pcompTbl'}).find_all('ul')
    for listing in listings:
        item = listing.find('li')
        # find class of span
        try:
            website = '/logo/'+item.find('div', {'class': 'cell1'}).find(
                'span')['class'][0]
        except:
            website = item.find('div', {'class': 'cell1'}).find('img')['src']
        price = item.find('div', {'class': 'cell3'}).text.strip()
        try:
            productUrl = getProductLink(
                item.find('div', {'class': 'cell4'}).find('a')['href'])
        except:
            productUrl = ''
            continue
        data.append({
            'website': website,
            'price': price,
            'productUrl': productUrl
        })

    product_data['title'] = title
    product_data['image'] = image
    product_data['points'] = points
    product_data['prices'] = data
    return product_data


def getProductLink(redirectUrl):
    print(redirectUrl)
    soup = BeautifulSoup(requests.get(redirectUrl).text, 'html.parser')
    return soup.find('p', {'class': 'small-text'}).find('a')['href']


# print(scrapeDetailPage("https://www.compareraja.in/apple-iphone-11-price.html"))
