# Django + Nginx + Waitress 프로젝트

Windows 환경에서 Django 웹 애플리케이션을 nginx와 waitress로 배포하는 프로젝트입니다.

## 📁 프로젝트 구조

```
C:\20250625\
├── config/                 # Django 프로젝트 설정
│   ├── __init__.py
│   ├── settings.py         # Django 설정 파일
│   ├── urls.py
│   └── wsgi.py
├── myapp/                  # Django 앱
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── static/                 # 개발용 정적 파일
│   └── style.css
├── staticfiles/            # 배포용 정적 파일 (collectstatic 결과)
│   ├── admin/
│   └── style.css
├── templates/              # HTML 템플릿
│   └── myapp/
├── nginx/                  # nginx 웹 서버
│   └── nginx-1.24.0/
│       ├── conf/
│       │   └── nginx.conf  # nginx 설정 파일
│       └── nginx.exe
├── manage.py
└── db.sqlite3
```

## 🚀 설치 및 설정 과정

### 1. Django 프로젝트 생성

```bash
# Django 설치
pip install django

# 프로젝트 생성
django-admin startproject config .

# 앱 생성
python manage.py startapp myapp
```

### 2. Django 설정 (settings.py)

```python
# config/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myapp',  # 추가
]

# 템플릿 설정
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # 루트에 templates 폴더
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# 정적 파일 설정
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']  # 개발용 정적 파일
STATIC_ROOT = BASE_DIR / 'staticfiles'    # 배포용 정적 파일

# 프로덕션 환경 설정
DEBUG = False
ALLOWED_HOSTS = ['*']
```

### 3. 모델 및 관리자 설정

```python
# myapp/models.py
from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
```

```python
# myapp/admin.py
from django.contrib import admin
from .models import Post

admin.site.register(Post)
```

### 4. URL 설정

```python
# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),
]
```

```python
# myapp/urls.py
from django.urls import path
from .views import post_list

urlpatterns = [
    path('', post_list, name='post_list'),
]
```

### 5. 뷰 및 템플릿

```python
# myapp/views.py
from django.shortcuts import render
from .models import Post

def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'myapp/post_list.html', {'posts': posts})
```

```html
<!-- templates/myapp/post_list.html -->
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>게시글 리스트</title>
    {% load static %}
    <link rel="stylesheet" href="{% static 'style.css' %}">
</head>
<body>
    <h1>게시글 리스트</h1>
    <ul>
        {% for post in posts %}
            <li>{{ post.title }} - {{ post.created_at|date:'Y-m-d H:i' }}</li>
        {% empty %}
            <li>게시글이 없습니다.</li>
        {% endfor %}
    </ul>
</body>
</html>
```

### 6. 데이터베이스 마이그레이션

```bash
# 마이그레이션 생성
python manage.py makemigrations

# 마이그레이션 적용
python manage.py migrate

# 관리자 계정 생성
python manage.py createsuperuser
```

### 7. Waitress 설치 및 설정

```bash
# Waitress 설치 (Windows용 WSGI 서버)
pip install waitress
```

### 8. Nginx 설치 및 설정

#### 8.1 Nginx 다운로드
```bash
# nginx 다운로드
Invoke-WebRequest -Uri "https://nginx.org/download/nginx-1.24.0.zip" -OutFile "nginx.zip"

# 압축 해제
Expand-Archive -Path nginx.zip -DestinationPath .
```

#### 8.2 Nginx 설정 (nginx/nginx-1.24.0/conf/nginx.conf)

```nginx
server {
    listen       80;
    server_name  localhost;

    # Django 정적 파일 서빙
    location /static/ {
        alias C:/20250625/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Django 앱으로 프록시
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🏃‍♂️ 실행 방법

### 1. 정적 파일 수집
```bash
python manage.py collectstatic --noinput
```

### 2. Waitress 실행 (Django WSGI 서버)
```bash
python -m waitress --listen=0.0.0.0:8000 config.wsgi:application
```

### 3. Nginx 실행 (웹 서버)
```bash
# nginx.exe 더블클릭 또는
cd nginx/nginx-1.24.0
nginx.exe
```

## 🌐 접속 확인

### 정상 동작 확인:
- **http://localhost** - nginx를 통한 접속 (CSS/JS 정상 로드) ✅
- **http://localhost:8000** - waitress 직접 접속 (CSS/JS 깨짐, 정상) ✅
- **http://localhost/admin** - Django 관리자 페이지 ✅

### 예상 결과:
- nginx (80번 포트): 정적 파일 서빙 + Django 앱 프록시
- waitress (8000번 포트): Django WSGI 서버만 담당

## 🔧 문제 해결

### 1. 정적 파일이 로드되지 않는 경우
- `python manage.py collectstatic --noinput` 재실행
- nginx 설정의 경로 확인
- nginx 재시작

### 2. 포트 충돌
- `netstat -an | findstr :8000` - 8000번 포트 사용 확인
- `netstat -an | findstr :80` - 80번 포트 사용 확인

### 3. 권한 문제
- nginx를 관리자 권한으로 실행

## 📝 주의사항

1. **Windows 환경**: waitress 사용 (gunicorn은 Linux 전용)
2. **정적 파일**: nginx가 담당, waitress는 WSGI 서버만 담당
3. **프로덕션**: DEBUG=False 설정 필요
4. **경로**: nginx 설정의 경로를 실제 프로젝트 경로로 수정

## 🎯 완성된 구조

```
사용자 요청 → nginx (80번) → waitress (8000번) → Django 앱
                ↓
            정적 파일 서빙 (CSS, JS, 이미지)
```