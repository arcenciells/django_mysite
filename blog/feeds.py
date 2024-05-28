import markdown
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy
from .models import *
from django.utils.feedgenerator import DefaultFeed

class PostTypeFeed(DefaultFeed):
    # 기본적으로 RSS 피드는 XML 형식 사용하기 때문에 DefaultFeed를 상속받아 피드의 content_type XML 형식으로 설정
    content_type = 'application/xml; charset=utf-8'

class LatestPostsFeed(Feed) :
    title = 'My blog'
    link = reverse_lazy('blog:post_list')
    description = 'New posts of my blog.'
    feed_type = PostTypeFeed # PostTypeFeed : 피드의 content_type이 XML로 설정되는 것


    def items(self):
        return Post.published.all()[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return truncatewords_html(markdown.markdown(item.body), 30)

    def item_pubdate(self, item):
        return item.publish