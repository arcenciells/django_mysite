from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown
from ..models import Post

register = template.Library()

@register.simple_tag
def total_posts():
    return Post.published.count()

@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}

# Django의 템플릿 라이브러리 데코레이터, 함수가 단순한 템플릿 태그로 사용되도록 등록하는 것
@register.simple_tag
# 기본적으로 최대 5개의 게시물 반환, count 파라미터를 통해 반환할 게시물 수 조절 가능
def get_most_commented_posts(count=5):
    # Count('comments') : 각 게시물의 댓글 수 count
    return Post.published.annotate(
               total_comments=Count('comments')
           ).order_by('-total_comments')[:count]

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))
