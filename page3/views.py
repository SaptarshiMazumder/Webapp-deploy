
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from django.views.generic import ListView, DetailView, UpdateView
from matplotlib.style import context
from . models import Community, GameProfile, Post, Replies, ImageFiles, Profile, Tags, Main_Profile
from . forms import EditPostForm, EditVideoPostForm, ImageForm, PostForm, PostImageForm, PostVideoForm, EditImagePostForm, GameProfileForm, MatchmakingForm, CreateCommunityForm, EditCommunityForm
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.db.models import Q
from django.conf import settings
from django.conf.urls.static import static
# Create your views here.
# Paginator stuff
from django.core.paginator import Paginator
from django.contrib.auth.models import User

from .serializers import PostSerializer
from django.core import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view
import json


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def home(request):
    object_list = Post.objects.all().order_by('-post_datetime')
    image_list = ImageFiles.objects.all()
    context = {
        'object_list': object_list,
        'image_list': image_list,
    }
    return render(request, 'home.html', context)


def home_timeline(request, post_id=None):

    object_list = Post.objects.all().order_by('-post_datetime')
    communities = Community.objects.all()[:5]
    try:
        main_game_profile = Main_Profile.objects.get(user=request.user)

        gamer_profiles = GameProfile.objects.filter(user=request.user)
        print("User's GAME PROFILES: ", gamer_profiles)
    except:
        main_game_profile = None
        print("MAIN GAME PROFILE: ", main_game_profile)
        gamer_profiles = None

    # joined_communities = request.user.profile.communities.all()
    try:
        joined_communities = request.user.profile.communities.all()
    except:
        joined_communities = ""
    # Set up pagination
    # request.session['loaded_posts'] = object_list
    p = Paginator(object_list, 4)

    # p = Paginator(Post.objects.all().order_by('-post_datetime'), 4)
    page = request.GET.get('page')
    objects = p.get_page(page)
    a = 200
    # printing
    print(objects)
    try:

        last_viewed = request.session['post_in_view']
    except:
        last_viewed = ""
    # image_list = ImageFiles.objects.all()
    image_list = ""
    profiles = Profile.objects.all()
    has_images_to_show = False
    try:
        post = Post.objects.get(id=post_id)
        profile = Post.objects.get(user=post['author'])
        context = {
            'object_list': object_list,
            'image_list': image_list,
            'post': post,
            'post_id': post_id,
            'objects': objects,
            'last_viewed': last_viewed,
            'has_images_to_show': has_images_to_show,
            'profile': profile,
            'communities': communities,
            'joined_communities': joined_communities,
            'media_url': "127.0.0.1: 8000/media",
            'main_game_profile': main_game_profile,
            'game_logos': GameProfile.games_logo_list,
            'page': 'home-timeline',
        }
    except:
        context = {
            'object_list': object_list,
            'image_list': image_list,
            'objects': objects,
            'last_viewed': last_viewed,
            'has_images_to_show': has_images_to_show,
            'profiles': profiles,
            'communities': communities,
            'joined_communities': joined_communities,
            'media_url': "127.0.0.1: 8000/media",
            'main_game_profile': main_game_profile,
            'gamer_profiles': gamer_profiles,
            'game_logos': GameProfile.games_logo_list,
            'page': 'home-timeline',
        }
    # print("SETTINGS: ", static(settings.MEDIA_URL))

    return render(request, 'base/home_timeline.html', context)


@csrf_exempt
def upload_reply(request, pk):
    form1 = PostImageForm()
    form2 = PostVideoForm()
    imageform = ImageForm()

    post_data = return_post_data(request, pk)

    replying_to = []
    # replying_to = Post.objects.get(id=pk)
    replying_to = get_parent_post(pk, replying_to)
    replying_to = replying_to[::-1]

    replies_obj = []
    replies_to_post = []

    replies = Replies.objects.filter(reply_to=pk)

    if replies:
        print("REPLIES", replies)
        for reply in replies:
            reply_post = Post.objects.get(id=reply.post_id)
            replies_obj.append(reply_post)
        replies_to_post = replies_obj[::-1]

    profiles = Profile.objects.all()

    # Sidebar data
    communities = Community.objects.all()[:5]
    try:
        main_game_profile = Main_Profile.objects.get(user=request.user)

        gamer_profiles = GameProfile.objects.filter(user=request.user)
        print("User's GAME PROFILES: ", gamer_profiles)
    except:
        main_game_profile = None
        print("MAIN GAME PROFILE: ", main_game_profile)
        gamer_profiles = None

    # joined_communities = request.user.profile.communities.all()
    try:
        joined_communities = request.user.profile.communities.all()
    except:
        joined_communities = ""
    context = {
        'form1': form1,
        'form2': form2,
        'replying_to': replying_to,
        'imageform': imageform,
        'replies_to_post': replies_to_post,
        'show_replies_button': True,
        'profiles': profiles,
        'communities': communities,
        'joined_communities': joined_communities,
        'main_game_profile': main_game_profile,
        'gamer_profiles': gamer_profiles,
        'game_logos': GameProfile.games_logo_list,
        'page': 'replies-page',
    }
    print('')
    context.update(post_data)
    print(context)

    if request.method == 'POST':

        form1 = PostImageForm(request.POST, request.FILES)
        form2 = PostVideoForm(request.POST, request.FILES)
        id = int(request.POST.get('postid'))
        image_files = request.FILES.getlist("image")
        video_files = request.FILES.getlist("video")
        print("FILES2 UPLOADED: ", video_files)
        if video_files:
            print("FILES 2 IS NOT NONE")
            form1 = PostVideoForm(request.POST, request.FILES)
        if form1.is_valid():
            print("FORM1 VALID")

            instance = form1.save(commit=False)
            tags = request.POST['tags']
            print("REPLT TAGS: ", tags)

            print("POSTID: ", id)
            print(type(pk))
            print(type(id))
            instance.author = request.user
            instance.user_profile = request.user.profile
            instance.reply_to = id
            instance.is_reply = True
            instance.is_parent_a_reply = is_parent_a_reply(id)
            print("is_parent_a_reply: ", instance.is_parent_a_reply)
            if instance.is_parent_a_reply:
                instance.reply_root = id
            if instance.is_parent_a_reply:
                parent_reply_root = get_parent_reply_root(id)
                if parent_reply_root != -1:
                    instance.reply_root = parent_reply_root

                print("reply_root: ", instance.reply_root)

            print("INSTANCE: ", instance)
            if image_files:
                instance.has_images = True
            else:
                instance.has_images = False

            if video_files:
                instance.has_video = True
            else:
                instance.has_video = False

            instance.save()

            for file in image_files:
                res = ImageFiles.objects.create(post=instance, image=file)
                instance.images_ids_list.append(res.id)
                instance.images_urls_list.append(res.image)
                instance.save()

            for file in video_files:
                print("VIDEO FILE: ", file)

            reply_to_post = Post.objects.get(id=pk)

            reply = Replies(reply_to=id, post_id=instance.id,
                            reply_to_post=reply_to_post, reply_root=instance.reply_root)
            reply.save()
            add_reply_count(id, instance.reply_root)

            # Adding tags to db
            if len(tags) > 0:
                tags_list = tags.replace(' ', '').split(",")

                for t in tags_list:
                    if not(Tags.objects.filter(tag_name=t).exists()):

                        new_tag = Tags(tag_name=t)
                        new_tag.save()
                        Tags.objects.get(id=new_tag.id).post.add(
                            Post.objects.get(id=instance.id))

                    else:
                        print("MATCHED: ", Tags.objects.filter(tag_name=t))
                        Tags.objects.get(tag_name=t).post.add(
                            Post.objects.get(id=instance.id))

                post_obj = Post.objects.get(id=instance.id)
                post_obj.set_Tag(tags_list)
                post_obj.save()

            return(update_replies_list(request, pk, True))
            # return JsonResponse({'error': False, 'message': 'Uploaded Successfully'})

        if form2.is_valid():
            print("FORM2 VALID")
            instance = form2.save(commit=False)
            instance.author = request.user
            instance.user_profile = request.user.profile
            instance.reply_to = pk
            instance.is_reply = True
            if request.FILES:
                instance.has_video = True
            instance.save()

            reply = Replies(reply_to=id, post_id=instance.id,
                            reply_to_post=reply_to_post, reply_root=instance.reply_root)
            reply.save()

            return(update_replies_list(request, pk, True))
        else:
            return JsonResponse({'error': True, 'errors': form1.errors})
    else:
        form1 = PostImageForm()
        form2 = PostVideoForm()
        imageform = ImageForm()

    return render(request, 'post/replies/replies_page.html', context)


def is_parent_a_reply(id):
    parent = Post.objects.get(id=id)
    if parent:
        return parent.is_reply
    else:
        return False


def get_parent_reply_root(id):
    parent = Post.objects.get(id=id)
    if parent:
        return parent.reply_root
    else:
        return -1


def update_replies_list(request, post_id, fetching_replies_to_post):
    replies_obj = []
    replies_to_post = []

    replies = Replies.objects.filter(reply_to=post_id)
    replies2 = Replies.objects.filter(
        Q(reply_to=post_id) | Q(reply_root=post_id))
    for reply2 in replies2:
        print("Reply2: ", reply2)
    if replies2:
        print("REPLIES", replies)
        for reply in replies2:
            reply_post = Post.objects.get(id=reply.post_id)
            replies_obj.append(reply_post)
        # if(reply_root == -1):
        #     replies_to_post = replies_obj[::-1]
        # else:
        #     replies_to_post = replies_obj
        show_replies_button = True
        if fetching_replies_to_post:
            replies_to_post = replies_obj[::-1]
            show_replies_button = True
        else:
            replies_to_post = replies_obj
            show_replies_button = False
        image_list = ImageFiles.objects.all()

        replyingToAuthor = ""
        replyingToIsReply = False
        replyingTo = Post.objects.get(id=post_id)

        if replyingTo:
            replyingToAuthor = replyingTo.author.username
            replyingToIsReply = replyingTo.is_reply
            print("REPLYINGG TO: ", replyingToAuthor)
            print("REPLYING TO A REPLY?: ", replyingToIsReply)

        profiles = Profile.objects.all()
        context = {
            'replies': replies,
            'replies_obj': replies_obj,
            'replies_to_post': replies_to_post,
            'image_list': image_list,
            'replyingToAuthor': replyingToAuthor,
            'replyingToIsReply': replyingToIsReply,
            'show_replies_button': show_replies_button,
            'profiles': profiles,

        }
        for p in profiles:
            print("PROFILE:: ", p)
        html = render_to_string(
            'post/replies/replies_list.html', context, request=request)
        # print("HTML: ", html)

        return JsonResponse({'replies_list': html, })
    else:
        return JsonResponse({'replies_list': "", })


@csrf_exempt
def fetch_replies_to_reply(request):
    id = int(request.POST.get('postid'))
    return(update_replies_list(request, id, False))
    # return JsonResponse({'replies_list': "lkkkk", })


def add_reply_count(id, reply_root):
    if id == reply_root:
        post = get_object_or_404(Post, id=id)
        if post:
            post.reply_count += 1
            post.save()
            print("If part getting called")
            print("REPLY ROOT HERE: ", reply_root)
            try:
                original_parent_post = Post.objects.get(
                    id=post.reply_to)
                if original_parent_post:
                    original_parent_post.reply_count += 1
                    original_parent_post.save()
            except:
                return
    else:
        try:
            post = get_object_or_404(Post, id=id)
            if post:
                post.reply_count += 1
                post.save()
                print("Budeweiser")
                print(type(reply_root))
        except:
            return
        try:
            if(reply_root != -1):
                this_reply_root = Post.objects.get(id=reply_root)
                print("Else part getting called")
                print("REPLY ROOT HERE: ", reply_root)
                if this_reply_root:
                    print(">>>")
                    this_reply_root.reply_count += 1
                    this_reply_root.save()
                    try:
                        original_parent_post = Post.objects.get(
                            id=this_reply_root.reply_to)
                        if original_parent_post:
                            original_parent_post.reply_count += 1
                            original_parent_post.save()
                    except:
                        return
        except:
            return


def return_post_data(request, post_id):
    post = Post.objects.get(id=post_id)
    image_list = ImageFiles.objects.all()

    replies_obj = []
    replies_to_post = []

    replies = Replies.objects.filter(reply_to=post_id)

    if replies:
        print("REPLIES", replies)
        for reply in replies:
            if reply.post_id:
                reply_post = Post.objects.get(id=reply.post_id)
                if reply_post:
                    replies_obj.append(reply_post)
        replies_to_post = replies_obj[::-1]
    liked = False
    if post.likes.filter(id=request.user.id).exists():
        liked = True
    total_likes = post.total_likes()
    print("Working till here")
    parents_arr = []
    if post.is_reply:
        parents_arr = get_parent_post(post.reply_to, parents_arr)
        parents_arr = parents_arr[::-1]

    context = {
        'post': post,
        'total_likes': total_likes,
        'liked': liked,
        'replies': replies,
        'replies_obj': replies_obj,
        'replies_to_post': replies_to_post,
        'parents_arr': parents_arr,
        'image_list': image_list,
        'last_viewed': "",

    }

    return context


def add_post(request):
    form = PostForm()
    context = {
        'form': form
    }
    if request.method == 'POST':
        print(request.POST)
        form = PostForm(request.POST, request.FILES)
        tags = request.POST['tags']
        if form.is_valid():
            # form.save()
            instance = form.save(commit=False)
            instance.author = request.user
            instance.user_profile = request.user.profile
            print("PRINTING PROFILE: ", request.user.profile)
            instance.save()
            if len(tags) > 0:
                tags_list = tags.replace(' ', '').split(",")

                for t in tags_list:
                    if not(Tags.objects.filter(tag_name=t).exists()):

                        new_tag = Tags(tag_name=t)
                        new_tag.save()
                        Tags.objects.get(id=new_tag.id).post.add(
                            Post.objects.get(id=instance.id))

                    else:
                        print("MATCHED: ", Tags.objects.filter(tag_name=t))
                        Tags.objects.get(tag_name=t).post.add(
                            Post.objects.get(id=instance.id))

                post_obj = Post.objects.get(id=instance.id)
                post_obj.set_Tag(tags_list)
                post_obj.save()
            return redirect('home-page')
        else:
            return render(request, 'post/addPost/add_post.html', context)
    else:
        form = PostForm()

    return render(request, 'post/addPost/add_post.html', context)


def add_image_post(request):
    form = PostImageForm()
    context = {
        'form': form
    }
   
    if request.method == 'POST':
        print(request.POST)
        form = PostImageForm(request.POST)
        files = request.FILES.getlist("image")
        tags = request.POST['tags']
        if form.is_valid():
            # form.save()
            instance = form.save(commit=False)
            instance.author = request.user
            instance.user_profile = request.user.profile
            if files:
                instance.has_images = True
            else:
                instance.has_images = False
            instance.save()
            if len(tags) > 0:
                tags_list = tags.replace(' ', '').split(",")

                for t in tags_list:
                    if not(Tags.objects.filter(tag_name=t).exists()):

                        new_tag = Tags(tag_name=t)
                        new_tag.save()
                        Tags.objects.get(id=new_tag.id).post.add(
                            Post.objects.get(id=instance.id))

                    else:
                        print("MATCHED: ", Tags.objects.filter(tag_name=t))
                        Tags.objects.get(tag_name=t).post.add(
                            Post.objects.get(id=instance.id))

                post_obj = Post.objects.get(id=instance.id)
                post_obj.set_Tag(tags_list)
                post_obj.save()
            for file in files:
                res = ImageFiles.objects.create(post=instance, image=file)
                print("RES: ", res.image)
                instance.images_ids_list.append(res.id)
                instance.images_urls_list.append(res.image)
                instance.save()
            
            return redirect('home-page')
        else:
            print("Came Here")
            print(form.errors)
    else:
        form = PostImageForm()
        imageform = ImageForm()

    return render(request, 'post/addPost/add_image_post.html', {"form": form, "imageform": imageform})


def add_video_post(request):
    form = PostVideoForm()
    context = {
        'form': form
    }
    if request.method == 'POST':
        print(request.POST)
        form = PostVideoForm(request.POST, request.FILES)
        tags = request.POST['tags']
        if form.is_valid():
            # form.save()
            instance = form.save(commit=False)
            instance.author = request.user
            instance.user_profile = request.user.profile
            if request.FILES:
                instance.has_video = True
            instance.save()
            if len(tags) > 0:
                tags_list = tags.replace(' ', '').split(",")

                for t in tags_list:
                    if not(Tags.objects.filter(tag_name=t).exists()):

                        new_tag = Tags(tag_name=t)
                        new_tag.save()
                        Tags.objects.get(id=new_tag.id).post.add(
                            Post.objects.get(id=instance.id))

                    else:
                        print("MATCHED: ", Tags.objects.filter(tag_name=t))
                        Tags.objects.get(tag_name=t).post.add(
                            Post.objects.get(id=instance.id))

                post_obj = Post.objects.get(id=instance.id)
                post_obj.set_Tag(tags_list)
                post_obj.save()
            return redirect('home-page')
        else:
            return render(request, 'post/addPost/add_video_post.html', context)
    else:
        form = PostVideoForm()

    return render(request, 'post/addPost/add_video_post.html', context)


def get_parent_post(parent_id, arr):
    parents = Post.objects.get(id=parent_id)
    if parents:
        arr.append(parents)
    if parents.is_reply:
        is_reply_to = Post.objects.get(id=parents.reply_to)
        get_parent_post(is_reply_to.id, arr)
    return arr


def edit_post(request, post_id):
    post = Post.objects.get(id=post_id)
    form = EditPostForm(request.POST or None, instance=post)
    context = {
        'post': post,
        'form': form
    }

    if form.is_valid():
        form.save()
        return redirect('home-page')
    return render(request, 'post/addPost/update_post.html', context)


def edit_image_post(request, post_id):
    post = Post.objects.get(id=post_id)
    form = EditImagePostForm(request.POST or None, instance=post)
    imageform = ImageForm()
    files = request.FILES.getlist("image")

    context = {
        'post': post,
        'form': form,
        'imageform': imageform
    }

    if form.is_valid():
        form.save()
        instance = form.save(commit=False)
        if files:
            instance.has_images = True
        else:
            instance.has_images = False
        instance.save()
        ImageFiles.objects.filter(post=instance).delete()
        for file in files:
            ImageFiles.objects.create(post=instance, image=file)

        return redirect('home-page')

    return render(request, 'post/addPost/update_image_post.html', context)


def edit_video_post(request, post_id):
    post = Post.objects.get(id=post_id)
    form = EditVideoPostForm(request.POST or None,
                             request.FILES or None, instance=post)
    context = {
        'post': post,
        'form': form
    }

    if form.is_valid():
        # form.save()
        instance = form.save(commit=False)
        if not request.FILES:
            instance.has_video = False

        instance.save()
        return redirect('home-page')
    return render(request, 'post/addPost/update_video_post.html', context)


def delete_post(request, post_id):
    post = Post.objects.get(id=post_id)
    is_reply = False
    if post.is_reply:
        is_reply = True
        print("IS REPLY:", is_reply)
    post.delete()

    if is_reply:
        reply_object = Replies.objects.get(post_id=post_id)
        print("TO BE DELETED:", reply_object)
        reply_object.delete()

    return redirect('home-page')


@login_required
@csrf_exempt
def like(request):
    if request.POST.get('action') == 'post':
        result = ''
        id = int(request.POST.get('postid'))
        post = get_object_or_404(Post, id=id)
        print(id)
        print(post.like_count)
        test = post.likes.filter(id=request.user.id)
        print(test)
        # print(request.POST.get('elem'))
        # request.session['post_in_view'] = id
        if post.likes.filter(id=request.user.id).exists():
            print("Exists")
            post.likes.remove(request.user)
            post.like_count -= 1
            result = post.like_count
            post.save()
        else:
            print("Doesn't exist")
            post.likes.add(request.user)
            post.like_count += 1
            result = post.like_count
            post.save()
        return JsonResponse({'result': result, })


@login_required
@csrf_exempt
def set_likes(request):
    if request.POST.get('action') == 'post':
        result = ''
        id = int(request.POST.get('postid'))
        post = get_object_or_404(Post, id=id)
        # print(id)
        # print(post.body, post.like_count)
        result = post.like_count
        # print(request.POST.get('elem'))

        return JsonResponse({'result': result, })


@login_required
@csrf_exempt
def liked_by(request, post_id):
    print("HEREEEE!!")
    post = Post.objects.get(id=post_id)
    liked_by = post.likes.all()
    print("LIKEDBY: ", liked_by)
    context = {
        'liked_by': liked_by,
    }
    return render(request, 'post/liked_by.html', context)


@login_required
@csrf_exempt
def vouch(request):
    if request.POST.get('action') == 'post':
        result = ''
        id = int(request.POST.get('postid'))
        post = get_object_or_404(Post, id=id)
        print(id)
        # print(post.like_count)
        test = post.vouches.filter(id=request.user.id)
        print(test)
        # print(request.POST.get('elem'))
        # request.session['post_in_view'] = id
        if post.vouches.filter(id=request.user.id).exists():
            print("Exists")
            post.vouches.remove(request.user)
            post.vouch_count -= 1
            result = post.vouch_count
            post.save()
        else:
            print("Doesn't exist")
            post.vouches.add(request.user)
            post.vouch_count += 1
            result = post.vouch_count
            post.save()

        return JsonResponse({'result': result, })


@login_required
@csrf_exempt
def update_session(request):
    if request.POST.get('action') == 'post':
        id = int(request.POST.get('postid'))
        request.session['post_in_view'] = id
        return JsonResponse({'id': request.session['post_in_view']})


@login_required
@csrf_exempt
def get_session_data(request):

    if request.POST.get('action') == 'post':
        id = request.session['post_in_view']
        post = get_object_or_404(Post, id=id)
        result = post.like_count
        print("Last post clicked on: ", request.session['post_in_view'])
        return JsonResponse({'result': result})


def category(request, cat):
    print("CAT: ", cat)
    catrgory_posts = Post.objects.filter(tags=cat)
    context = {
        'cat': cat.title().replace('-', ' '),
        'catrgory_posts': catrgory_posts
    }
    return render(request, 'post/posts_by_category.html', context)


def join_leave_community(request, community_id):
    pass

# REST API Views


def home_view(request):
    return render(request, "api/home_view.html", status=200)


def post_list_view(request):
    object_list = Post.objects.all().order_by('-post_datetime')
    image_list = ImageFiles.objects.all()
    post_list = [{"id": x.id, "author": x.author.username, "body": x.body}
                 for x in object_list]
    data = {
        "response": post_list
    }
    return JsonResponse(data)
    return render(request, 'home.html', context)


@api_view(['GET'])
def getPosts(request):
    object_list = Post.objects.all().order_by('-post_datetime')
    serializer = PostSerializer(object_list, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getPost(request, pk):
    object = Post.objects.get(id=pk)
    serializer = PostSerializer(object, many=False)
    return Response(serializer.data)


@api_view(['PUT'])
def updatePost(request, pk):
    print("Hello")
    data = request.data
    object = Post.objects.get(id=pk)
    serializer = PostSerializer(instance=object, data=data)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(['DELETE'])
def deletePost(request, pk):
    post = Post.objects.get(id=pk)
    post.delete()
    return Response('Post was deleted!')


def user_profile_stats(request, user):
    if(user != 'favicon.png'):
        user = User.objects.get(username=user)
        posts = Post.objects.filter(author=user)
        profile = Profile.objects.filter(user=user)[0]
        image_list = ImageFiles.objects.all()
        gamer_profiles = GameProfile.objects.filter(user=user)
        try:
            main_gamer_profile = Main_Profile.objects.get(
                user=User.objects.get(username=user))
        except:
            main_gamer_profile = None

        additional_info = []
        for g in gamer_profiles:
            info_obj = g.additional_info

            dict_obj = {}
            for i in range(len(info_obj)):
                dict_obj[i] = info_obj[i]
            additional_info.append({'game': g.game,
                                    'info': dict_obj})

        context = {'posts': posts, 'profile_owner': user,
                   'profile': profile, 'image_list': image_list,
                   'gamer_profiles': gamer_profiles,
                   'main_game_profile': main_gamer_profile,
                   'additional_info': additional_info,
                   'game_logos': GameProfile.games_logo_list,
                   'page': 'user_profile_page',
                   'user_to_view': user.username}

        return render(request, 'user/user_profile_stats.html', context)
    return render(request, 'user/user_profile_stats.html', context={})


def user_posts_page(request, user):
    try:
        if(user != 'favicon.png'):
            user = User.objects.get(username=user)
            posts = Post.objects.filter(author=user)
            profile = Profile.objects.filter(user=user)[0]
            image_list = ImageFiles.objects.all()
            gamer_profiles = GameProfile.objects.filter(user=user)
            try:
                main_gamer_profile = Main_Profile.objects.get(
                    user=User.objects.get(username=user))
            except:
                main_gamer_profile = None

            additional_info = []
            for g in gamer_profiles:
                info_obj = g.additional_info

                dict_obj = {}
                for i in range(len(info_obj)):
                    dict_obj[i] = info_obj[i]
                additional_info.append({'game': g.game,
                                        'info': dict_obj})

            context = {'posts': posts, 'profile_owner': user,
                       'profile': profile, 'image_list': image_list,
                       'gamer_profiles': gamer_profiles,
                       'main_game_profile': main_gamer_profile,
                       'additional_info': additional_info,
                       'game_logos': GameProfile.games_logo_list, }

            return render(request, 'user/user_posts_page.html', context)
        else:
            return redirect('home-page')

    except:
        print("Mike", user, "Smalling")
        return render(request, 'user/user_posts_page.html', context={})


@api_view(['GET', 'POST'])
def start_following(request, who_to_follow):
    # print(who_to_follow, request.POST['user'])
    print(request.POST['user'], 'INIESTAA')
    profile = Profile.objects.filter(
        user=User.objects.get(username=request.POST['user']).id)
    profile[0].following.add(User.objects.get(username=who_to_follow))

    profile_followed = Profile.objects.filter(
        user=User.objects.get(username=who_to_follow))
    profile_followed[0].followers.add(
        User.objects.get(username=request.POST['user']))
    print(profile_followed, request.POST['user'])
    return Response(who_to_follow)


def create_game_profile(request, user):
    form = GameProfileForm()
    post_form = PostForm()

    if(user != 'favicon.png'):
        user = User.objects.get(username=user)

        if(request.method == 'POST'):

            additional_info = []
            roles = []
            is_looking_for_friends = False

            experience = []
            teams = []
            positions = []
            for i in request.POST.items():
                if "field" in i[0]:
                    additional_info.append(i[1])
                if "role" in i[0]:
                    roles.append(i[1])
             # for experience fields---------------
                if "Team/ Org Name" in i[0]:
                    teams.append(i[1])
                if "Role/ Experience" in i[0]:
                    positions.append(i[1])
            # END for experience fields---------------

            for i in range(len(teams)):
                experience.append([teams[i], positions[i]])
            if(request.POST.get('is_looking_for_friends') == 'on'):
                is_looking_for_friends = True

            comm_rating = request.POST.get("comm_rating")

            if(GameProfile.objects.filter(user=user.id, game=request.POST.get("game"))):

                game_profile = GameProfile.objects.filter(user=user.id,
                                                          game=request.POST.get("game"))
                game_profile.update(
                    server=request.POST.get("server"), rank=request.POST.get("rank"),
                    additional_info=additional_info, roles_rating=roles,
                    remarks=request.POST.get("remarks"), looking_for_friends=is_looking_for_friends,
                    time_available=request.POST.get('time_available'),
                    communication_level=int(comm_rating),
                    achievements=request.POST.get('achievements'),
                    experience=experience)

                if Main_Profile.objects.filter(user=user.id).exists():

                    main_profile = Main_Profile.objects.get(user=user.id)
                    if(request.POST.get('is_main') == 'on'):
                        main_profile.main_gamer_profile = game_profile[0]
                        main_profile.save()

                if len(request.POST.get('body')) > 1:

                    user_profile = Profile.objects.get(
                        user=User.objects.get(username=user))
                    new_post = Post(title="Gamer Profile Update", author=user,
                                    user_profile=user_profile,
                                    body=request.POST.get('body'), category=request.POST.get('game'))
                    new_post.save()
                    return redirect('home-page')

            else:

                new_gamer_profile = GameProfile(user=user, game=request.POST.get('game'),
                                                server=request.POST.get('server'), rank=request.POST.get('rank'),
                                                additional_info=additional_info, roles_rating=roles,
                                                remarks=request.POST.get(
                                                    "remarks"),
                                                looking_for_friends=is_looking_for_friends,
                                                time_available=request.POST.get(
                                                    'time_available'),
                                                communication_level=int(
                                                    comm_rating),
                                                achievements=request.POST.get(
                                                    'achievements'),
                                                experience=experience)
                new_gamer_profile.save()

                if Main_Profile.objects.filter(user=user).exists():
                    if (request.POST.get('is_main') == 'on'):
                        main_profile = Main_Profile.objects.get(user=user.id)
                        main_profile.main_gamer_profile = new_gamer_profile
                        main_profile.save()

                else:
                    new_main_profile = Main_Profile(user=user,
                                                    main_gamer_profile=new_gamer_profile)
                    new_main_profile.save()

                context = {'form': form, 'profile': new_gamer_profile,
                           'post_form': post_form}

                if len(request.POST.get('body')) > 1:

                    user_profile = Profile.objects.get(
                        user=User.objects.get(username=user))
                    new_post = Post(title="Gamer Profile Created", author=user,
                                    user_profile=user_profile,
                                    body=request.POST.get('body'), category=request.POST.get('game'))
                    new_post.save()
                    return redirect('home-page')

                # return render(request, 'create_gamer_profile.html', context)
    try:
        main_game_profile = Main_Profile.objects.get(user=request.user)

        gamer_profiles = GameProfile.objects.filter(user=request.user)

    except:
        main_game_profile = None

        gamer_profiles = None

    context = {
        'form': form,
        'post_form': post_form,
        'main_game_profile': main_game_profile,
        'gamer_profiles': gamer_profiles,
        'game_logos': GameProfile.games_logo_list,
        'page': 'create-gamer-profile'

    }

    return render(request, 'gamerProfile/create_gamer_profile.html', context)


def edit_gamer_profile(request, user):
    form = GameProfileForm()
    post_form = PostForm()

    if(user != 'favicon.png'):
        user = User.objects.get(username=user)

        if(request.method == 'POST'):

            additional_info = []
            roles = []
            is_looking_for_friends = False
            experience = []

            teams = []
            positions = []

            # for additional fields---------------
            for i in request.POST.items():
                if "field" in i[0]:
                    additional_info.append(i[1])
                if "role" in i[0]:
                    roles.append(i[1])
            # END for additional fields---------------

            # for experience fields---------------
                if "Team/ Org Name" in i[0]:
                    teams.append(i[1])
                if "Role/ Experience" in i[0]:
                    positions.append(i[1])
            # END for experience fields---------------

            for i in range(len(teams)):
                experience.append([teams[i], positions[i]])

            print(experience, "Icarus")
            print(request.POST, "Suns")
            if(request.POST.get('is_looking_for_friends') == 'on'):
                is_looking_for_friends = True

            comm_rating = request.POST.get("comm_rating")

            if(GameProfile.objects.filter(user=user.id, game=request.POST.get("game_to_edit"))):

                game_profile = GameProfile.objects.filter(user=user.id,
                                                          game=request.POST.get("game_to_edit"))

                game_profile.update(
                    server=request.POST.get("server"), rank=request.POST.get("rank"),
                    additional_info=additional_info, roles_rating=roles,
                    remarks=request.POST.get("remarks"), looking_for_friends=is_looking_for_friends,
                    time_available=request.POST.get('time_available'),
                    communication_level=int(comm_rating),
                    user_status=request.POST.get("user_status"),
                    in_game_user_id=request.POST.get('in_game_user_id'),
                    achievements=request.POST.get('achievements'),
                    experience=experience)

                if Main_Profile.objects.filter(user=user.id).exists():

                    main_profile = Main_Profile.objects.get(user=user.id)
                    if(request.POST.get('is_main') == 'on'):
                        main_profile.main_gamer_profile = game_profile[0]
                        main_profile.save()

                if len(request.POST.get('body')) > 1:

                    user_profile = Profile.objects.get(
                        user=User.objects.get(username=user))
                    new_post = Post(title="Gamer Profile Update", author=user,
                                    user_profile=user_profile,
                                    body=request.POST.get('body'), category=request.POST.get('game'))
                    new_post.save()
                    return redirect('home-page')

    try:
        main_game_profile = Main_Profile.objects.get(user=request.user)

        gamer_profiles = GameProfile.objects.filter(user=request.user)

    except:
        main_game_profile = None

        gamer_profiles = None

    context = {
        'form': form,
        'post_form': post_form,
        'main_game_profile': main_game_profile,
        'gamer_profiles': gamer_profiles,
        'game_logos': GameProfile.games_logo_list,
        'page': 'edit-gamer-profile',
        'Game_Profile_Class': GameProfile,
    }

    return render(request, 'gamerProfile/edit_gamer_profile.html', context)


def MatchmakingHome(request, user):
    form = GameProfileForm()
    print(user)
    context = {'form': form}

    return render(request, 'matchmaking/matchmaking.html', context)


def Matchmaking_Data(request, user):
    form = GameProfileForm()

    if request.method == 'POST':
        print(request.POST)
        pref_game = request.POST['game']
        pref_server = request.POST['server']
        rank = request.POST['rank']
        user_profiles = []
        proflies = []
        game_profiles = GameProfile.objects.filter(game=pref_game)
        for g in game_profiles:
            this_user = User.objects.get(username=g.user).id
            this_profile = (Profile.objects.filter(user=int(this_user)))
            if(this_profile):
                print(this_profile[0].bio)
                obj = {'username': g.user.username, 'game': g.game, 'rank': g.rank, 'server': g.server,
                       'bio': this_profile[0].bio, 'profile_pic': str(this_profile[0].profile_pic), 'user_status': g.user_status}
                proflies.append(obj)

        print("PROFILES :", proflies)
        context = {'profiles': proflies}

        html = render_to_string(
            'matchmaking/matchmaking_found_list.html', context, request=request)

        return JsonResponse({"profiles": html})


def Gamer_Profile_Data(request, user):

    gamer_profiles = GameProfile.objects.filter(
        user=User.objects.get(username=user), game=request.POST['game'])

    main_gamer_profile = Main_Profile.objects.get(
        user=User.objects.get(username=user))
    additional_info = []
    for g in gamer_profiles:
        info_obj = g.additional_info

        dict_obj = {}
        for i in range(len(info_obj)):
            dict_obj[i] = info_obj[i]
        additional_info.append({'game': g.game,
                                'info': dict_obj})

    context = {
        'selected_gamer_profiles': gamer_profiles,
        'main_gamer_profile': main_gamer_profile,
        'additional_info': additional_info,
        'game_logos': GameProfile.games_logo_list,
    }

    html = render_to_string(
        'gamerProfile/gamer_profile_stats.html', context, request=request)
    print(context)
    return JsonResponse({"gamer_profile_stats": html,
                         'game_logo': GameProfile.games_logo_list[gamer_profiles[0].game],
                         })


def User_Profile_Page_Data(request, user, game):
    gamer_profiles = GameProfile.objects.filter(
        user=User.objects.get(username=user), game=request.POST['game'])

    main_gamer_profile = Main_Profile.objects.get(
        user=User.objects.get(username=user))
    additional_info = []
    for g in gamer_profiles:
        info_obj = g.additional_info

        dict_obj = {}
        for i in range(len(info_obj)):
            dict_obj[i] = info_obj[i]
        additional_info.append({'game': g.game,
                                'info': dict_obj})
    saved_roles_rating = []

    if game == "Valorant":
        default_game_role = GameProfile.Valorant_Roles
    elif game == "League of Legends":
        default_game_role = GameProfile.LOL_Roles
    elif game == "Call of Duty":
        default_game_role = GameProfile.COD_Roles
    elif game == "Counter Strike: GO":
        default_game_role = GameProfile.CS_GO_Roles

    for i in range(0, len(gamer_profiles[0].roles_rating)):
        saved_roles_rating.append(
            (default_game_role[i], gamer_profiles[0].roles_rating[i]))

    context = {
        'selected_gamer_profiles': gamer_profiles,
        'main_gamer_profile': main_gamer_profile,
        'additional_info': additional_info,
        'game_logos': GameProfile.games_logo_list,
        'saved_roles_rating': saved_roles_rating}

    if(game == 'Valorant'):

        html = render_to_string(
            'gamerProfile/game_specific_stats/valorant_stats.html', context, request=request)
        print(context)
        return JsonResponse({"gamer_profile_stats": html,
                             'game_logo': GameProfile.games_logo_list[gamer_profiles[0].game],
                             })
    elif(game == 'Call of Duty'):
        html = render_to_string(
            'gamerProfile/game_specific_stats/cod_stats.html', context, request=request)
        print(context)
        return JsonResponse({"gamer_profile_stats": html,
                             'game_logo': GameProfile.games_logo_list[gamer_profiles[0].game],
                             })
    elif(game == 'League of Legends'):
        html = render_to_string(
            'gamerProfile/game_specific_stats/lol_stats.html', context, request=request)
        print(context)
        return JsonResponse({"gamer_profile_stats": html,
                             'game_logo': GameProfile.games_logo_list[gamer_profiles[0].game],
                             })
    elif(game == 'Counter Strike: GO'):
        html = render_to_string(
            'gamerProfile/game_specific_stats/cs_go_stats.html', context, request=request)
        print(context)
        return JsonResponse({"gamer_profile_stats": html,
                             'game_logo': GameProfile.games_logo_list[gamer_profiles[0].game],
                             })


@csrf_exempt
@api_view(['GET'])
def get_game_rank_server(request, game):

    ranks = []
    servers = []
    additional_info_fields = []
    default_roles = []
    if game == "Valorant":
        ranks = GameProfile.ValorantRanks.choices
        servers = GameProfile.ValorantServers.choices
        additional_info_fields = GameProfile.Valorant_additional_fields
        default_roles = GameProfile.Valorant_Roles

    if game == "Call of Duty":
        ranks = GameProfile.CODRanks.choices
        servers = GameProfile.CODServers.choices
        additional_info_fields = GameProfile.COD_additional_fields
        default_roles = GameProfile.COD_Roles

    if game == "League of Legends":
        ranks = GameProfile.LOLRanks.choices
        servers = GameProfile.LOLServers.choices
        additional_info_fields = GameProfile.LOL_additional_fields
        default_roles = GameProfile.LOL_Roles

    if game == "Counter Strike: GO":
        ranks = GameProfile.CSRanks.choices
        servers = GameProfile.CSServers.choices
        additional_info_fields = GameProfile.CS_GO_additional_fields
        default_roles = GameProfile.CS_GO_Roles

    default_user_status = GameProfile.User_Status.choices
    is_profile_exists = GameProfile.objects.filter(user=request.user,
                                                   game=game).exists()
    print(game, ranks, servers, additional_info_fields)
    return JsonResponse({"ranks": ranks, "servers": servers,
                        "additional_fields": additional_info_fields,
                         "default_roles": default_roles,
                         "is_profile_exists": is_profile_exists,
                         "default_user_status": default_user_status,
                         'experience_fields': GameProfile.experience_fields, })


def get_saved_game_rank_server(request, game):
    ranks = []
    servers = []
    default_additonal_fields = []
    default_roles = []
    default_user_status = []
    remarks = ""

    if game == "Valorant":
        ranks = GameProfile.ValorantRanks.choices
        servers = GameProfile.ValorantServers.choices
        default_additonal_fields = GameProfile.Valorant_additional_fields
        default_roles = GameProfile.Valorant_Roles

    if game == "Call of Duty":
        ranks = GameProfile.CODRanks.choices
        servers = GameProfile.CODServers.choices
        default_additonal_fields = GameProfile.COD_additional_fields
        default_roles = GameProfile.COD_Roles

    if game == "League of Legends":
        ranks = GameProfile.LOLRanks.choices
        servers = GameProfile.LOLServers.choices
        default_additonal_fields = GameProfile.LOL_additional_fields
        default_roles = GameProfile.LOL_Roles

    if game == "Counter Strike: GO":
        ranks = GameProfile.CSRanks.choices
        servers = GameProfile.CSServers.choices
        default_additonal_fields = GameProfile.CS_GO_additional_fields
        default_roles = GameProfile.CS_GO_Roles

    default_user_status = GameProfile.User_Status.choices
    saved_gamer_profile = GameProfile.objects.get(user=request.user,
                                                  game=game)
    print(request.user)
    return JsonResponse({"ranks": ranks, "servers": servers,
                        "saved_rank": saved_gamer_profile.rank,
                         "saved_server": saved_gamer_profile.server,
                         "additional_fields": saved_gamer_profile.additional_info,
                         "default_additonal_fields": default_additonal_fields,
                         "default_roles": default_roles,
                         "roles_rating": saved_gamer_profile.roles_rating,
                         "remarks": saved_gamer_profile.remarks,
                         "looking_for_friends": saved_gamer_profile.looking_for_friends,
                         "time_available": saved_gamer_profile.time_available,
                         "communication_level": saved_gamer_profile.communication_level,
                         "default_user_status": default_user_status,
                         "saved_user_status": saved_gamer_profile.user_status,
                         'in_game_user_id': saved_gamer_profile.in_game_user_id,
                         'achievements': saved_gamer_profile.achievements,
                         'experience_fields': GameProfile.experience_fields,
                         'experience': saved_gamer_profile.experience
                         })


def search_results(request):

    if request.method == 'POST':
        og_search_query = request.POST['search_query']
        search_query = request.POST['search_query'].lower().replace(' ', '')
        posts_list = []
        people_list = []
        all_posts = Post.objects.all().order_by('-post_datetime')
        all_profiles = Profile.objects.all()
        profiles = Profile.objects.all()
        image_list = ImageFiles.objects.all()

        for p in all_posts:
            if p.body.lower().find(search_query) != -1:
                posts_list.append(p)

            elif len(p.tags) > 0 and p.get_Tag() != "":

                for t in p.get_Tag():
                    if t.lower().find(search_query) != -1:
                        posts_list.append(p)
            elif str(p.category).lower().replace(' ', '').find(search_query) != -1:
                posts_list.append(p)
            if p.author.username.find(search_query) != -1:
                posts_list.append(p)

        for pr in all_profiles:
            if pr.user.username.find(search_query) != -1:
                people_list.append(pr)

        print(posts_list)

        return render(request, 'search/search_results.html', context={'posts_list': posts_list,
                                                                      'search_query': og_search_query, 'profiles': profiles,
                                                                      'people_list': people_list, 'image_list': image_list})
    return render(request, 'search/search_results.html')


# Community

# Create Community

def create_community(request):
    form = CreateCommunityForm()
    message = ""
    context = {
        'user': request.user,
        'form': form,
        'message': message
    }
    if request.method == 'POST':
        form = CreateCommunityForm(request.POST, request.FILES)
        if form.is_valid():
            # form.save()
            # print("Name: ",)
            instance = form.save(commit=False)
            print("COMMUNITY NAME: ", instance.name)
            existing_community = Community.objects.filter(name=instance.name)

            print("EXISTING COMMUNITY: ", existing_community)
            print(existing_community.count())
            if existing_community.count() == 0:

                instance.created_by = request.user

                instance.save()

                instance.community_admins.add(request.user)
                instance.save()

            else:
                message = "This community already exists! Try something else"
                context['message'] = message
                return render(request, 'community/create_community.html', context)

            return redirect('home-page')

    return render(request, 'community/create_community.html', context)


def edit_community(request, id):
    community = Community.objects.filter(id=id)[0]
    form = EditCommunityForm(request.POST or None,
                             request.FILES or None, instance=community)

    message = "Hiii"
    context = {
        'user': request.user,
        'form': form,
        'message': message,
        'existing_community_data': community,
    }
    if request.method == 'POST':
        form = EditCommunityForm(request.POST or None,
                                 request.FILES or None, instance=community)

        instance = form.save(commit=False)

        instance.save()
        return redirect('home-page')
    return render(request, 'community/edit_community.html', context)


def editCommunityRules(request, id):
    community = Community.objects.filter(id=id)[0]


def get_community_details(request, id):
    community = Community.objects.filter(id=id)
    json_data = {'community_name': community[0].name}
    return JsonResponse(json_data)


def community_page(request, community_id):
    community = Community.objects.get(id=community_id)
    print(community)
    context = {
        'community': community
    }

    # object_list = Post.objects.all().order_by('-post_datetime')
    object_list = Post.objects.filter(
        community=community).order_by('-post_datetime')
    game_profiles = GameProfile.objects.all()
    communities = Community.objects.all()

    # Set up pagination
    # request.session['loaded_posts'] = object_list
    p = Paginator(object_list, 4)
    # p = Paginator(Post.objects.all().order_by('-post_datetime'), 4)
    page = request.GET.get('page')
    objects = p.get_page(page)
    a = 200
    print(objects)
    # image_list = ImageFiles.objects.all()
    image_list = ""
    profiles = Profile.objects.all()
    has_images_to_show = False
    context = {
        'community': community,
        'object_list': object_list,
        'image_list': image_list,
        'objects': objects,
        'has_images_to_show': has_images_to_show,
        'profiles': profiles,
        'game_profiles': game_profiles,
        'communities': communities,
    }

    return render(request, 'community/community_page.html', context)


@login_required
@csrf_exempt
def join_community(request):
    if request.POST.get('action') == 'post':
        result = ''
        id = int(request.POST.get('community_id'))
        community = get_object_or_404(Community, id=id)
        print(id)
        # print(community.like_count)
        test = community.members.filter(id=request.user.id)
        print(test)
        buttonText = ""
        # buttonColor =""
        # print(request.POST.get('elem'))
        # request.session['post_in_view'] = id
        if community.members.filter(id=request.user.id).exists():
            print("Exists")
            community.members.remove(request.user)
            community.save()
            if(request.user.profile.communities.filter(id=id).exists()):
                request.user.profile.communities.remove(community)
                request.user.profile.save()
            print("This user's communities: ",
                  request.user.profile.communities.all())
            buttonText = "Join"

        else:
            print("Doesn't exist")
            community.members.add(request.user)
            community.save()
            if(not(request.user.profile.communities.filter(id=id).exists())):
                request.user.profile.communities.add(community)
                request.user.profile.save()
            print("This user's communities: ",
                  request.user.profile.communities.all())
            buttonText = "Joined"
        return JsonResponse({'result': "success", 'buttonText': buttonText})


def add_post_community(request, community_id):
    form = PostForm()
    community = None
    try:
        community = Community.objects.get(id=community_id)
        print("COMMUNITY TO ADD POST TO: ", community)
    except:
        return redirect("home-page")

    context = {
        'form': form
    }
    if request.method == 'POST':
        print(request.POST)
        form = PostForm(request.POST, request.FILES)
        tags = request.POST['tags']
        if form.is_valid():
            # form.save()
            instance = form.save(commit=False)
            instance.author = request.user
            instance.user_profile = request.user.profile
            if community:
                instance.community = community
            print("PRINTING PROFILE: ", request.user.profile)
            instance.save()
            if len(tags) > 0:
                tags_list = tags.replace(' ', '').split(",")

                for t in tags_list:
                    if not(Tags.objects.filter(tag_name=t).exists()):

                        new_tag = Tags(tag_name=t)
                        new_tag.save()
                        Tags.objects.get(id=new_tag.id).post.add(
                            Post.objects.get(id=instance.id))

                    else:
                        print("MATCHED: ", Tags.objects.filter(tag_name=t))
                        Tags.objects.get(tag_name=t).post.add(
                            Post.objects.get(id=instance.id))

                post_obj = Post.objects.get(id=instance.id)
                post_obj.set_Tag(tags_list)
                post_obj.save()
            return redirect('home-page')
        else:
            return render(request, 'post/addPost/add_post.html', context)
    else:
        form = PostForm()

    return render(request, 'post/addPost/add_post.html', context)


def add_image_post_community(request, community_id):
    form = PostImageForm()
    community = None
    try:
        community = Community.objects.get(id=community_id)
        print("COMMUNITY TO ADD POST TO: ", community)
    except:
        return redirect("home-page")
    context = {
        'form': form
    }
    if request.method == 'POST':
        print(request.POST)
        form = PostImageForm(request.POST)
        files = request.FILES.getlist("image")
        tags = request.POST['tags']
        if form.is_valid():
            # form.save()
            instance = form.save(commit=False)
            instance.author = request.user
            instance.user_profile = request.user.profile
            if files:
                instance.has_images = True
            else:
                instance.has_images = False
            if community:
                instance.community = community
            instance.save()
            if len(tags) > 0:
                tags_list = tags.replace(' ', '').split(",")

                for t in tags_list:
                    if not(Tags.objects.filter(tag_name=t).exists()):

                        new_tag = Tags(tag_name=t)
                        new_tag.save()
                        Tags.objects.get(id=new_tag.id).post.add(
                            Post.objects.get(id=instance.id))

                    else:
                        print("MATCHED: ", Tags.objects.filter(tag_name=t))
                        Tags.objects.get(tag_name=t).post.add(
                            Post.objects.get(id=instance.id))

                post_obj = Post.objects.get(id=instance.id)
                post_obj.set_Tag(tags_list)
                post_obj.save()
            for file in files:
                # ImageFiles.objects.create(post=instance, image=file)
                res = ImageFiles.objects.create(post=instance, image=file)
                print("RES: ", res.image)
                instance.images_ids_list.append(res.id)
                instance.images_urls_list.append(res.image)
                instance.save()

            return redirect('home-page')
        else:
            print(form.errors)
    else:
        form = PostImageForm()
        imageform = ImageForm()

    return render(request, 'post/addPost/add_image_post.html', {"form": form, "imageform": imageform})


def add_video_post_community(request, community_id):
    form = PostVideoForm()
    community = None
    try:
        community = Community.objects.get(id=community_id)
        print("COMMUNITY TO ADD POST TO: ", community)
    except:
        return redirect("home-page")
    context = {
        'form': form
    }
    if request.method == 'POST':
        print(request.POST)
        form = PostVideoForm(request.POST, request.FILES)
        tags = request.POST['tags']
        if form.is_valid():
            # form.save()
            instance = form.save(commit=False)
            instance.author = request.user
            instance.user_profile = request.user.profile
            if request.FILES:
                instance.has_video = True
            if community:
                instance.community = community
            instance.save()
            if len(tags) > 0:
                tags_list = tags.replace(' ', '').split(",")

                for t in tags_list:
                    if not(Tags.objects.filter(tag_name=t).exists()):

                        new_tag = Tags(tag_name=t)
                        new_tag.save()
                        Tags.objects.get(id=new_tag.id).post.add(
                            Post.objects.get(id=instance.id))

                    else:
                        print("MATCHED: ", Tags.objects.filter(tag_name=t))
                        Tags.objects.get(tag_name=t).post.add(
                            Post.objects.get(id=instance.id))

                post_obj = Post.objects.get(id=instance.id)
                post_obj.set_Tag(tags_list)
                post_obj.save()
            return redirect('home-page')
        else:
            return render(request, 'post/addPost/add_video_post.html', context)
    else:
        form = PostVideoForm()

    return render(request, 'post/addPost/add_video_post.html', context)
