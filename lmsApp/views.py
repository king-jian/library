import uuid
from django.conf import settings
from django.core.cache import caches
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count, Sum, Q
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View

from .utils import *
from .models import *

user_cache = caches["user"]


# 欢迎界面
def welcome_page(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    print(x_forwarded_for)
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # 所以这里是真实的ip
        print("ip:", ip)
    else:
        ip = request.META.get('REMOTE_ADDR')  # 这里获得代理ip
        print("proxy_ip:", ip)
    return render(request, 'welcome.html')


# 登陆界面
def login_page(request):
    # create_book()
    # create_user()
    # create_record()
    return render(request, 'login.html', {'line': '请输入账户和密码'})


def login_action(request):
    # 先获取登陆的账号密码
    student_card = request.POST.get("namefield")
    password = request.POST.get("pwdfield")
    # 解析数据
    if student_card.isdigit() and len(student_card) <= 12:
        # 从数据库中获取该账号/密码
        user = Readers.objects.filter(student_card=student_card, password=password).first()
        if user:
            request.session["reader_id"] = user.id
            request.session.set_expiry(3600)
            request.session["reader_name"] = user.name
            # 验证成功，设置缓存token，返回主页面，并返回token
            token = uuid.uuid4().hex
            user_cache.set(token, user.pk, settings.USER_TOKEN_LIFE)
            if user.active:
                url = reverse("MyLMS:index")
                return redirect(url, {"token": token})
            else:
                # 登陆失败，仍返回登录页
                return render(request, "login.html", {'line': '请先激活账户'})
        else:
            # 登陆失败，仍返回登录页
            return render(request, "login.html", {'line': '账户或密码错误，请重试'})
    else:
        return render(request, "login.html", {'line': '您输入的账户名不符合要求，请重试'})


def signup_page(request):
    # 返回注册页面
    return render(request, "signup.html", {"line": "请填写注册信息"})


def signup_action(request):
    name = request.POST.get("namefield")
    student_card = request.POST.get("scfield")
    password = request.POST.get("pwdfield")
    # 解析数据
    if len(name) <= 12 and student_card.isdigit():
        # 从数据库中获取该账号,看是否已被注册
        user = Readers.objects.filter(student_card=student_card).first()
        if not user:
            print(dir(user))
            user = Readers.objects.create(name=name, student_card=student_card, password=password)
            user.save()
            return render(request, 'login.html', {'line': '请输入账户和密码'})
        else:
            # 注册失败，仍返回注册页
            return render(request, "signup.html", {'line': '该账号已被注册，请重新填写'})
    else:
        return render(request, "login.html", {'line': '您输入的姓名或账号名不符合要求，请重试'})


def logout_action(request):
    try:
        print(request.session["reader_id"])
        del request.session['reader_id']
    except:
        return render(request, 'login.html', {'line': '您已退出'})
    return render(request, 'login.html', {'line': '您已退出!'})


def index(request):
    # 判断是否有用户登陆
    if "reader_id" not in request.session:
        # 如果没有用户登陆，重定向至登陆
        return render(request, "login.html", {"line": "请先登陆"})
    # 返回最活跃的三个用户
    readers = Record.objects.values_list("reader").annotate(borrow_num=Count("id")).order_by("-borrow_num")
    reader1 = Readers.objects.get(pk=readers[0][0])
    Top1 = {"id": reader1.id, "name": reader1.name, "Act_times": readers[0][1]}
    reader2 = Readers.objects.get(pk=readers[1][0])
    Top2 = {"id": reader2.id, "name": reader1.name, "Act_times": readers[1][1]}
    reader3 = Readers.objects.get(pk=readers[2][0])
    Top3 = {"id": reader3.id, "name": reader1.name, "Act_times": readers[2][1]}
    # 返回最新的七本书
    Newbooks = Book.objects.all().order_by("-id")[0:7]
    # 可用/总数目
    sum = Book.objects.all().count()
    available = Book.objects.filter(available=True).count()
    per = (float(available)) / float(sum) * 100
    booksum = {"sum": sum, "available": available, "per": int(per)}
    records = Record.objects.filter(reader=request.session["reader_id"]).values_list("status").annotate(Count("id"))
    BORROWED = 0
    WAITFORCHECK = 0
    TURNDOWN = 0
    DEMAGE = 0
    RETURNED = 0
    for item in records:
        if item[0] == 'BORROWED':
            BORROWED = item[1]
        if item[0] == 'WAITFORCHECK':
            WAITFORCHECK = item[1]
        if item[0] == 'TURNDOWN':
            TURNDOWN = item[1]
        if item[0] == 'DEMAGE':
            DEMAGE = item[1]
        if item[0] == 'RETURNED':
            RETURNED = item[1]
    # 罚款总数
    record = Record.objects.filter(reader=request.session["reader_id"])
    t = record.aggregate(Sum('fine'))['fine__sum']
    if t:
        TotalFine = t
    else:
        TotalFine = 0
    return render(request, 'index.html',
                  {'Top1': Top1, 'Top2': Top2, 'Top3': Top3, 'Newbooks': Newbooks, 'booksum': booksum,
                   'TotalFine': TotalFine, 'BORROWED': BORROWED, 'WAITFORCHECK': WAITFORCHECK, 'TURNDOWN': TURNDOWN,
                   'DEMAGE': DEMAGE, 'RETURNED': RETURNED})


def bookslist(request):
    try:
        reader = Readers.objects.get(pk=request.session["reader_id"])
    except:
        return render(request, "login.html", {"line": "请重新登陆"})
    books = Book.objects.all()
    booksall = books.count()
    per_page_limit = 13
    paginator = Paginator(books, per_page_limit)
    page = request.GET.get("page")
    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)
    return render(request, 'bookslist.html', {'books': books, 'booksall': booksall, 'reader': reader})


def book_page(request, book_id):
    book = Book.objects.get(pk=book_id)
    return render(request, 'book_page.html', {'book': book})


def search_action(request):
    param = request.GET.get("title", None)
    if param:
        books = Book.objects.filter(title__icontains=param)
    else:
        param = request.COOKIES.get("search_key")
        books = Book.objects.filter(title__icontains=param)
    booksall = books.count()
    per_page_limit = 13
    paginator = Paginator(books, per_page_limit)
    page = request.GET.get("page")
    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)
    try:
        reader = Readers.objects.get(pk=request.session["reader_id"])
    except KeyError:
        return render(request, 'login.html', {'line': '请重新登陆'})
    response = render(request, 'bookslist.html', {'books': books, 'booksall': booksall, 'reader': reader})
    response.set_cookie('search_key', param,)
    return response


def setting(request):
    reader_id = request.session["reader_id"]
    if reader_id:
        reader = Readers.objects.get(pk=reader_id)
        return render(request, 'settings.html', {'reader': reader})
    else:
        return render(request, 'login.html', {'line': '请重新登陆'})


def borrow_action(request):
    try:
        reader_id = request.session.get("reader_id")
        reader = Readers.objects.get(id=reader_id)
    except:
        return render(request, "login.html", {"line": "请重新登录"})
    book_borrow_count=Record.objects.filter(reader=reader,status='BORROWED').count()
    if book_borrow_count>=2:
        book_id = request.POST.get("book_id")
        book = Book.objects.filter(id=book_id).first()
        book_borrow_count=Record.objects.filter(reader=reader,status='WAITFORCHECK').count()
        if book_borrow_count>2:
            return render(request, "book_page.html", {"line": "两本书已在申请状态了，先看完再借吧", 'book': book})
        Record.objects.create(book_id=book.id, reader_id=reader.id,status='WAITFORCHECK')
        book.save()
        return render(request, "book_page.html", {"line": "亲，你已经借了3本书了，这本书已经在帮您申请了",'book': book})

    book_id = request.POST.get("book_id")
    book = Book.objects.filter(id=book_id).first()
    if not book.available:
        return render(request, "book_page.html", {"line": "《%s》已被借走，尚未归还"%(book.title), 'book': book})
    book.available=False
    Record.objects.create(book_id=book.id, reader_id=reader.id,status='BORROWED')
    book.save()
    return render(request, "book_page_success.html", {"line": "已借书成功", 'book': book})


def record_page(request):
    try:
        reader_id = request.session["reader_id"]
    except:
        return render(request, 'login.html', {'line': '请先登录'})
    records_book = Record.objects.filter(reader_id=reader_id)
    readersall = records_book.count()
    paginator = Paginator(records_book, 13)
    page = request.GET.get("page")
    try:
        records_book = paginator.page(page)
    except PageNotAnInteger:
        records_book = paginator.page(1)
    except EmptyPage:
        records_book = paginator.page(paginator.num_pages)
    return render(request, "record_page.html",
                  {"records": records_book, "recordsall": readersall, 'line': "(●'◡'●) 借书清单:"})


def delete_waiting(request, record_id):
    Record.objects.filter(id=record_id).delete()
    records_book = Record.objects.filter(reader_id=request.session["reader_id"])
    recordsall = records_book.all()
    paginator = Paginator(records_book, 13)
    page = request.GET.get("page")
    try:
        records_book = paginator.page(page)
    except PageNotAnInteger:
        records_book = paginator.page(1)
    except EmptyPage:
        records_book = paginator.page(paginator.num_pages)
    return render(request, "record_page.html",
                  {"records": records_book, 'line': "(●'◡'●) Delete the borrow request sucessfully:"})


