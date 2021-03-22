from django.db import models
from django.utils import timezone
from django.urls import reverse
# Create your models here.


class Post(models.Model):
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE) #jeden autor będzie odpowiedzialny za różne aspekty, dlatego Foreign Key/ jeden user, dlatego auth.User
    title = models.CharField(max_length=200)
    text = models.TextField() #nie ograniczamy usera do wielkości
    created_date = models.DateTimeField(default=timezone.now) #dlatego importujemy timezone
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()
        #oznacza to, że data publikacji będzie automatycznie przypisana do now()

    #Post może mieć komentarze, dlatego dodajemy funkcję komentowania
    def approve_comments(self):
        return self.comments.filter(approved_comment=True) #docelowo będziemy mieli listę komenatzry, dlatego juz się do niej odnosimy

    #to jest funkcja stworzona po ustawieniu modelów - mówi: po zapostowaniu idź do miejsca określonego w reverse()
    def get_absolute_url(self):   #nazwa własna, zdefiniowana w Django
        return reverse("post_detail", kwargs={'pk': self.pk})

    def __str__(self):
        return self.title

# tworzymy nową klasę Comments, na którą patrzymy od strony bazy, czyli kiedy User dostaje komentarz
class Comment(models.Model):
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='comments') #ForeignKey
    author = models.CharField(max_length=200) #author nie będzie zalogowany, więc CharFiel wystarczy
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.approved_comment = True
        self.save()

    #to jest funkcja stworzona po ustawieniu modelów - mówi: po zostawieniu komentarza idź do miejca określonego w reverse()
    def get_absolute_url(self):   #nazwa własna, zdefiniowana w Django
        return reverse("post_list")

    def __str__(self):
        return self.text

