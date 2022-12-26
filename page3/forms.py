

from django.forms import ModelForm
from matplotlib import widgets
from .models import Post, Category, ImageFiles, GameProfile, Community, User
from django import forms


choices = [('VALORANT', 'VALORANT'), ('CSGO', 'CSGO'), ('COD', 'COD')]
# choices = Category.objects.all().values_list('name', 'name')
tags = Category.objects.all().values_list('tags', 'tags')

choice_list = []

for item in choices:
    choice_list.append(item)


class PostForm(ModelForm):
    class Meta:
        model = Post
        # fields = '__all__'
        fields = ('body', 'category', 'tags', 'is_lft_lfp_post')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            # 'author': forms.TextInput(attrs={'class': 'form-control', 'value': '', 'id': 'author-name', 'type': 'hidden'}),
            # 'author': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(choices=choice_list, attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write something here...'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'eg- #LFT, #Valo, #Valorant'})
        }


class PostImageForm(ModelForm):
    class Meta:
        model = Post
        # fields = '__all__'
        fields = ('body', 'category', 'tags', 'is_lft_lfp_post')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'category': forms.Select(choices=choice_list, attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'id': 'form-body', 'placeholder': 'Write something here...'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'eg- #LFT, #Valo, #Valorant'})
        }


class PostVideoForm(ModelForm):
    class Meta:
        model = Post
        # fields = '__all__'
        fields = ('body', 'category', 'video', 'tags', 'is_lft_lfp_post')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            # 'author': forms.TextInput(attrs={'class': 'form-control', 'value': '', 'id': 'author-name', 'type': 'hidden'}),
            # 'author': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(choices=choice_list, attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write something here...'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'eg- #LFT, #Valo, #Valorant'})
        }


class EditPostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'body', 'category')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Post Title'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write something here...'}),
            'category': forms.Select(choices=choice_list, attrs={'class': 'form-control'}),
        }


class EditVideoPostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'body', 'category', 'video')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Post Title'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write something here...'}),
            'category': forms.Select(choices=choice_list, attrs={'class': 'form-control'}),
        }


class EditImagePostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'body', 'category')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Post Title'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write something here...'}),
            'category': forms.Select(choices=choice_list, attrs={'class': 'form-control'}),
        }


class ImageForm(ModelForm):
    image = forms.ImageField(
        label="Image", widget=forms.ClearableFileInput(attrs={"multiple": True}), required=False)

    class Meta:
        model = ImageFiles
        fields = ("image",)


class GameProfileForm(ModelForm):
    class Meta:
        model = GameProfile
        # fields = '__all__'
        fields = ('game', 'server', 'rank')
        # widgets = {
        #     'game': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Valorant'}),
        #     # 'author': forms.TextInput(attrs={'class': 'form-control', 'value': '', 'id': 'author-name', 'type': 'hidden'}),
        #     # 'author': forms.Select(attrs={'class': 'form-control'}),
        #     'category': forms.Select(choices=choice_list, attrs={'class': 'form-control'}),
        #     'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write something here...'})
        # }


class MatchmakingForm(ModelForm):
    class Meta:
        model = GameProfile
        fields = ('game', 'server', 'rank')


# Community

#all_users = User.objects.all().values_list('username', 'username')
all_users = []

# for item in all_users:
#     users_list.append(item)


class CreateCommunityForm(ModelForm):
    class Meta:
        model = Community
        fields = ('name', 'bio', 'profile_pic')
        # widgets = {
        #     'community_admins': forms.Select(choices=all_users, attrs={'class': 'form-control'}),
        # }


class EditCommunityForm(ModelForm):

    class Meta:
        model = Community
        fields = ('name', 'profile_pic', 'bio',
                  'community_header_pic',
                  )
        widgets = {
            'community_admins': forms.Select(choices=all_users, attrs={'class': 'form-control'}),
        }


class JoinCommunity(ModelForm):
    class Meta:
        model = Community
        fields = ('name', 'bio', 'profile_pic')
