from django.shortcuts import render
from .models import Post
from django.http import JsonResponse
# Create your views here.
def index(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request,'myapp/index.html',{'posts':posts})

def detail(request):
    id = request.POST.get('id')
    try:    
        post = Post.objects.get(id=id)
        content = post.content
        return JsonResponse({'content':content})
    except Post.DoesNotExist:
        return JsonResponse({'error': '게시글이 존재하지 않습니다.'}, status=404)