from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from blog.models import Post, Comment
from django.utils import timezone
from blog.forms import PostForm, CommentForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (TemplateView, ListView,
                                  DetailView, CreateView,
                                  UpdateView, DeleteView)  #dzięki () możemy dodać multiply views
from django.urls import reverse_lazy    #chcę aby przeniesienie usera odbyło się, kiedy wykona akcję (np.delete)



# Create your views here.

class AboutView(TemplateView):
    template_name = 'blog/about.html'

class PostListView(ListView):
    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
        #grab a Post model, all objects there and filter by these conditions
        # __lte oznacza 'less then or equal to'
        #order_by oznacza 'filtruj przez', a -published_date 'datę od najnowszych'/ inaczej może pokazywać od najstarszych

class PostDetailView(DetailView):
    model = Post

class CreatePostView(LoginRequiredMixin, CreateView):
    # jeżeli używamy login_required to long_url & redirect_field_name są bardzo ważne

    login_url = '/login/'    # in case of person isn't logged in, where should they go? to '/login/'
    redirect_field_name = 'blog/post_detail.html'   # redirect them to site post_detail
    form_class = PostForm
    model = Post
    # teraz stworzymy do tego url, aby użytkownik stworzył post, a jeśli niezalogowany - został przeniesiony do 'login'

    # jeśli popełnimy błąd, będziemy chcieli zaktualizować nasz post

class UpdatePostView(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post

# dla tej klasy musimy pamiętać, że nie chcemy published_date, bo to tylko drafty
# nie ma tu form_class, bo to tylko lista draftów, nie edytowanie ich
class DraftListView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_draft_list.html'
    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by('created_date') #filtruj po create_date

class DeletePost(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('post_list') #po usunięciu, wróć do głównej/listy postów




    # TERAZ BUDUJEMY OSOBNE VIEWS DLA KOMENTARZY - wymagają <PK> match

@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)


@login_required
def add_comment_to_post(request, pk):   #gość wybrał post, który chce skomentować, więc mamy pk(primary key)
    post = get_object_or_404(Post, pk=pk)   #weź ten konkretny post (lub 'nieznaleziono') i dalej prześlij model 'Post'
    if request.method == "POST":            #gość wypełnia i postuje komentarz
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post     #odnosimy się do atrybuty post w modelu klsy Post i łączymy: ten konretny kmentarz do TEGO KONKRETNEGO postu -> .save()
            comment.save()
            return redirect('post_detail', pk=post.pk)     #dodaj komentarz i przenieś do strony z detaliami konkretnego posta
    else:
        form = CommentForm
    return render(request, 'blog/comment_form.html', {'form': form})    # tu podpinamy stronę, która pojawi się kiedy gość zechce skomentować post

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()   #funkcja approve() znajduje się w modelu Comment, oznacza po prostu save()
    return redirect('post_detail', pk=comment.post.pk) #odsyła do post_detail, do konkretnego komentarza, do postu z konkretny <pk>

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail', pk=post_pk)