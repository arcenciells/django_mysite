from django import forms
from .models import Comment


class EmailPostForm(forms.Form):
     # forms.Form : 모델과 독립적으로 동작하며 폼 데이터를 처리하기 위해
     # 직접 정의하는 폼, 데이터가 반드시 데이터베이스 모델과 연결될 필요가 없는 경우
     # 이메일을 보내기 위한 폼(데이터)은 특정 모델에 저장될 필요 X
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False,
                               widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    # forms.ModelForm : 특정 데이터베이스 모델과 연결되어 있으며,
    # 모델 인스턴스를 생성, 업데이트 또는 삭제하는 폼을 정의하는 데 사용
    # 폼의 필드가 모델의 필드와 직접 매핑되고 폼을 통해 입력된 데이터가 자동으로 모델 인스턴스에 저장
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']

class SearchForm(forms.Form):
    query = forms.CharField(label='Search Word')
