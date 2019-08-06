from django.db import models

class Blog(models.Model):
    title = models.CharField(max_length=150)
    text = models.TextField()
    date = models.DateField()

    @property
    def img_main(self): 
        if self.blogphoto_set.all():
            return self.blogphoto_set.order_by('-ratio')[0].photo.url

    class Meta:
        ordering = ["-date"]

    
class BlogPhoto(models.Model): 
    photo = models.ImageField()
    blog = models.ForeignKey('Blog', null=True, on_delete=models.SET_NULL)
    ratio = models.DecimalField(max_digits=5, decimal_places=2)
