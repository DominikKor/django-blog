from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.core.mail import send_mail
from django.db.models import Count

from blog.forms import EmailForm, CommentForm
from blog.models import Post

from taggit.models import Tag


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts, 'tag': tag})


def post_detail(request, year, month, day, slug):
    NUM_RECOMMENDED_POSTS = 4

    post = get_object_or_404(
        Post, slug=slug, status='published', publish__year=year, publish__month=month, publish__day=day
    )

    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    post_tag_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tag_ids) \
        .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')) \
        .order_by('-same_tags', '-publish')[:NUM_RECOMMENDED_POSTS]

    return render(request, 'blog/post/detail.html', {
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'similar_posts': similar_posts,
    })


def share_post(request, post_id):
    sent_email = False
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            send_mail(
                subject=form.cleaned_data.get('subject'),
                from_email=form.cleaned_data.get('email_from'),
                recipient_list=[form.cleaned_data.get('email_to')],
                message=form.cleaned_data.get('comment'),
            )
            sent_email = True
    else:
        form = EmailForm()
    return render(request, 'blog/post/share.html', {
        'post': post,
        'form': form,
        'sent_email': sent_email,
    })
