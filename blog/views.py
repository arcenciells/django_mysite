from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage,\
                                  PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count, Q

from django.contrib import messages

from django.shortcuts import render
from .models import Post
from django.db.models import Q

def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None

    # 태그에 따라 필터링
    # 전체 흐름 : 태그 전달 되었는지 확인 > 태그 객체 가져오기 > 게시물 필터링
    if tag_slug: # tag_slug 변수가 None이 아니거나 빈 문자열이 아닌 경우에만 실행
        # 태그 모델에서 slug 필드가 tag_slug와 일치하는 태그 객체 가져오는 것
        # 조건에 맞는 객체 없을 경우, 404에러 발생
        tag = get_object_or_404(Tag, slug=tag_slug)
        # post_list : 필터링을 적용할 게시물의 쿼리셋
        # tags 필드에 주어진 tag가 포함된 게시물들로 쿼리셋 필터링
        post_list = post_list.filter(tags__in=[tag])

    # 검색어가 있을 경우 필터링
    # HTTP GET 요청에서 'q'라는 이름의 쿼리 매개변수 가져오기 (사용자가 검색 폼에서 제출한 검색어 포함할 수 있도록)
    search_query = request.GET.get('q')
    if search_query:
        post_list = post_list.filter(
            Q(title__icontains=search_query) | Q(body__icontains=search_query)
        )

    # 페이지네이션
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    total_results = post_list.count()
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    # 검색어, 태그, post_list에 게시물이 없는 경우 사용자에게 메시지 표시
    if not tag_slug and not search_query and not post_list.exists():
        messages.info(request, 'No posts found.')

    return render(request,
                 'blog/post/list.html',
                 {'posts': posts,
                  'tag': tag,
                  'query': search_query,
                  'total_results':total_results})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    # Form for users to comment
    form = CommentForm()
    # 현재 보고 있는 게시물 post의 모든 태그들의 ID 리스트 가져오는 것
    # values_list : 쿼리셋의 결과를 튜플이 아닌 단일 값의 리스트로 반환하도록 하는 것
    post_tags_ids = post.tags.values_list('id',flat=True)
    # post_tags_ids 리스트에 포함된 게시물 선택
    # exclude : 현재 보고 있는 게시물은 결과에서 제외하는 것
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    # similar_posts : 각 게시물이 몇 개의 동일한 태그를 가지고 있는지 계산하여 same_tags라는 새로운 필드 추가한 것
    # same_tags 가 많은 순서로 내림차순 정렬, 동일한 태그 수가 같은 경우에는 게시물의 게시 날짜 publish 기준으로 내림차순 정렬
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]
    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'form': form,
                   'similar_posts':similar_posts})

class PostListView(ListView):
    """
    Alternative post list view
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, \
                                   status=Post.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " \
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'your_account@gmail.com',
                      [cd['to']])
            sent = True

    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, \
                                   status=Post.Status.PUBLISHED)
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create a Comment object without saving it to the database
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()
    return render(request, 'blog/post/comment.html',
                           {'post': post,
                            'form': form,
                            'comment': comment})
