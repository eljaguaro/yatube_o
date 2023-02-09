from django.shortcuts import render, get_object_or_404
from .models import Post, Group, Comment, Follow
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import PostForm, CommentForm
from django.shortcuts import redirect
from .models import User
from django.conf import settings


# Главная страница
# @login_required

# @cache_page(20)
def index(request):
    post_list = Post.objects.select_related('author', 'group').all()
    paginator = Paginator(post_list, settings.TEN_SLICE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    template = 'posts/index.html'
    return render(request, template, context)


# Страница со сгруппированными постами
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author', 'group').all()
    paginator = Paginator(post_list, settings.TEN_SLICE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    template = 'posts/group_list.html'
    return render(request, template, context)


def profile(request, username):
    author = User.objects.filter(username=username)[0]
    sameuser = 0
    posts = author.posts.select_related('author', 'group').all()
    num_of_posts = posts.count()
    paginator = Paginator(posts, settings.TEN_SLICE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = Follow.objects.filter(user=request.user.id, author=author)
    sameuser = author == request.user
    context = {
        'author': author,
        'postsnum': num_of_posts,
        'page_obj': page_obj,
        'following': following,
        'sameuser': sameuser
    }
    return render(request, 'posts/profile.html', context)


@login_required
def post_create(request):
    groups = Group.objects.all()
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            form.save()
            return redirect(f'/profile/{request.user.username}/')
        return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm()
    return render(request, 'posts/create_post.html',
                  {'form': form, 'groups': groups})


def post_detail(request, post_id):
    post = Post.objects.select_related('author', 'group').filter(pk=post_id)[0]
    comments = Comment.objects.filter(post=post_id)
    author = User.objects.filter(username=post.author)[0]
    num_of_posts = author.posts.all().count()
    title = post.text[:30]
    if request.user == author:
        is_author = True
    else:
        is_author = False
    if request.method == 'POST':
        form = PostForm(request.POST,
                        files=request.FILES or None, instance=post)
        if form.is_valid():
            form.save()
            return redirect(f'/posts/{post_id}/')
        return render(request, 'posts/post_detail.html', {
            'form': form,
            'post': post,
            'postsnum': num_of_posts,
            'title': title,
            'author': author,
            'is_author': is_author,
            'comments': comments
        })
    form = CommentForm()
    return render(request, 'posts/post_detail.html', {
        'form': form,
        'post': post,
        'postsnum': num_of_posts,
        'title': title,
        'author': author,
        'is_author': is_author,
        'comments': comments
    })


@login_required
def post_edit(request, post_id):
    is_edit = True
    groups = Group.objects.all()
    post = Post.objects.select_related('author', 'group').filter(pk=post_id)[0]
    if post.author != request.user:
        return redirect(f'/posts/{post_id}/')
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None,
                        instance=post)
        if form.is_valid():
            form.save()
            return redirect(f'/posts/{post_id}/')
        return render(request, 'posts/create_post.html',
                      {'form': form, 'groups': groups,
                       'id': post_id, 'post': post, 'is_edit': is_edit})
    form = PostForm()
    return render(request, 'posts/create_post.html',
                  {'form': form, 'groups': groups,
                   'post': post, 'is_edit': is_edit})


@login_required
def add_comment(request, post_id):
    post = Post.objects.filter(pk=post_id).first()
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    ''' информация о текущем пользователе доступна в request.user '''
    followslst = Follow.objects.select_related(
        'user', 'author').filter(user=request.user)
    authors = followslst.values_list('author', flat=True)
    posts_list = Post.objects.filter(author__in=authors)
    paginator = Paginator(posts_list, settings.TEN_SLICE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    template = 'posts/follow.html'
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = User.objects.filter(username=username).first()
    follower_name = request.user.username
    follows = Follow.objects.filter(
        user=request.user, author=author).count()
    if follower_name != username and not follows:
        Follow.objects.create(user=request.user, author=author)
    return profile(request, username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.filter(username=username).first()
    Follow.objects.filter(user=request.user, author=author).delete()
    return profile(request, username)
