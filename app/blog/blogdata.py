import locale, requests, os, uuid
from datetime import datetime
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.files.images import File, ImageFile
from blog.models import BlogPhoto, Blog
from multiprocessing import Pool 

path_temp = os.path.join(settings.BASE_DIR, 'temp')
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

def get_data_page_detail(url: str) -> dict:
    """Returns data found on the blog page"""
    block = BeautifulSoup(requests.get(url).text, "html.parser")
    title = block.find('h1', class_="title").text.strip()
    text = block.find('div', class_="pos-content").text.strip().replace(u'\xa0', u' ')
    date = block.find('p', class_="meta").text.replace('.', ' ').split(' ')[2:5]
    date = '{} {} {}'.format(date[0], date[1], date[2])
    date = datetime.strptime(date, '%d %B %Y').date()
    return {'title': title, 'text': text, 'date': date}


def get_img_page_detail(url: str) -> list:
    """Returns links to images found on blog page"""
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    block = soup.find("div", {"id": "system"})
    main_img = block.find('div', class_="pos-media")
    slideshow = block.find('div', class_="wk-slideshow")

    if slideshow != None:
        img = slideshow.find('img')['src']
        all_img = slideshow.find_all('img')
        list_img = [x.get('data-src') for x in all_img]
        list_img[0] = img #list_img before adding the imag was None
 
    else:
        img = block.find('div', class_="pos-content").find_all('img')
        list_img = [x['src'] for x in img]

    if main_img is not None:
        main_img = main_img.find('img')['src']
        list_img.append(main_img)
    return list_img


def get_pagelists() -> list:
    """The function generates article list pages"""
    url_list = ['http://monaha.ru/blog/' + str(i) for i in range(48, 0, -1)]
    return url_list


def get_urls_pagelist(url_pagelist: str) -> list:
    """The function gets a list of articles and returns links to individual articles"""
    soup = BeautifulSoup(requests.get(url_pagelist).text, "html.parser")
    src = soup.find_all('h1', class_='title')
    urls = ['http://monaha.ru' + url.find('a').get('href') for url in src]
    with open("output.txt", "a") as f:
        for url in urls:
            print(f'data[{datetime.now()}] id[{os.getpid()}] fun[get_urls_pagelist] articles address: {url}', file=f)
    return urls


def get_all_urls_articles() -> list:
    """Returns a list of links to all articles"""
    all_urls = get_pagelists()
    with Pool(10) as pool:
       ll = pool.map(get_urls_pagelist, all_urls)
    l = []
    for i in ll:
        l += i
    print(f'There are {len(l)} articles for transfer')
    return l


def upload_file(img_url, file_name):
    """The function receives a link to the image and file name, saves the file to disk"""
    r = requests.get(img_url)
    with open(os.path.join(path_temp, file_name), 'wb') as f:
        f.write(r.content)
    with open("output.txt", "a") as f:
        print(f'data[{datetime.now()}] id[{os.getpid()}] fun[upload_file] - upload file[{file_name}]', file=f)

def add_blog_photo(post, file_name):
    """The function receives a link to the object of the Blog model and the name of the image,
       saves the images in Django and links it to the Blog."""
    with open(os.path.join(path_temp, file_name), 'rb') as f:
        myfile = ImageFile(f)
        ratio =  myfile.width / myfile.height
        img = BlogPhoto.objects.create(blog = post, ratio=ratio)
        if myfile.size >= 5000:
            img.photo.save(name=file_name, content=myfile)
            with open("output.txt", "a") as f:
                print("data[{}] id[{}] fun[add_blog_photo] - add file[{}]".format(datetime.now(), os.getpid(), img.photo.name), file=f)


def add_blog_post(url):
    """The function receives a link to the article, using it receives data, save this data to Django."""
    data = get_data_page_detail(url)
    post = Blog.objects.create(title=data['title'], text=data['text'], date=data['date'],)
    with open("output.txt", "a") as f:
        print("data[{}] id[{}] fun[add_blog_post] - add post[{}]".format(datetime.now(), os.getpid(), post.title), file=f)
    return post


def mv_one_post(url):
    """Defines the sequence of actions"""
    post = add_blog_post(url)
    list_img = get_img_page_detail(url)
    for url in list_img:
        if not url.startswith('http'):
            url = 'http://monaha.ru'+ url
        file_name = str(uuid.uuid4()) + url.split('/')[-1]
        upload_file(url, file_name)
        add_blog_photo(post, file_name)
        os.remove(os.path.join(path_temp, file_name))
        with open("output.txt", "a") as f:
            print("data[{}] id[{}] fun[mv_one_post] -- delete file[{}]".format(datetime.now(), os.getpid(), file_name), file=f)
    print(f'copying the article {post} is complete')
        

def main(url_list):
    """Asynchronously processes each article from the list"""
    with Pool(10) as pool:
        pool.map(mv_one_post, url_list)


#import blog.blogdata

#blog.blogdata.main(blog.blogdata.get_all_urls_articles())
