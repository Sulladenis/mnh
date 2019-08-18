from urllib import request
from django.core.files.base import ContentFile
from .blogdata import *

url = "http://monaha.ru/blog/item/ravnaya-apostolam"

def uploader(image_url, post, file_name):
    response  = request.urlopen(image_url)
    name = 'doom.jpg'
    myfile = ImageFile(ContentFile(response.read()))
    try:
        ratio =  myfile.width / myfile.height
    except TypeError:
        ratio = 1
    img = BlogPhoto.objects.create(blog = post, ratio=ratio)
    if myfile.size >= 5000:
        img.photo.save(name=file_name, content=myfile)
        with open("output.txt", "a") as f:
            print(f"data[{datetime.now()}] id[{os.getpid()}]"
            f"fun[add_blog_photo] - add file[{img.photo.name}]", file=f)


post = add_blog_post(url)
list_img = get_img_page_detail(url)
for url in list_img:
    if not url.startswith('http'):
        url = 'http://monaha.ru'+ url
    file_name = str(uuid.uuid4()) + url.split('.')[-1]
    uploader(url, post, file_name)

print(f'copying the article {post} is complete')

#uploader(url)
#from blog.loader import *
