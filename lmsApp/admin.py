from datetime import datetime

from django.contrib import admin

# Register your models here.
from .models import Record, Book, Readers


# class MyAdminSite(admin.AdminSite):
#     site_header = "图书馆后台管理系统"
#     site_title = '这是标题'
#     site_url = '106.12.27.42:15000'
#
# site = MyAdminSite()


class RecordInline(admin.TabularInline):
    model = Record
    fk_name = "reader"


class BooksAdmin(admin.ModelAdmin):
    # ModelAdmin.save_as¶
    save_as = True
    actions_on_top = True
    actions_on_bottom = False
    search_fields = ('title', 'ISBN', 'id', 'publisher')
    list_filter = ('pub_time', 'position', 'available')
    list_display = ('id', 'title', 'author', 'ISBN', 'publisher', 'pages', 'pub_time', 'price', 'position', 'available')
    # list_editable = ('ISBN',)
    list_display_links = ('title', 'pub_time')

    def make_available(modeladmin, request, queryset):
        queryset.update(available=True)

    make_available.short_description = "Mark selected Books as Available"

    def make_unavailable(modeladmin, request, queryset):
        queryset.update(available=False)

    make_unavailable.short_description = "Mark selected Books as Unavailable"
    actions = [make_available, make_unavailable]


admin.site.register(Book, BooksAdmin)


class ReadersAdmin(admin.ModelAdmin):
    actions_on_top = True
    actions_on_bottom = False
    list_display = ('id', 'name', 'student_card', 'password', 'active')
    search_fields = ('id', 'name',)
    list_filter = ('active', 'name', 'id', 'student_card')
    list_display_links = ('id', 'student_card',)
    inlines = [
        RecordInline,
    ]

    def make_active(self, request, queryset):
        queryset.update(active=True)
        self.message_user(request, "Mark selected Readers Active successfully. ")

    make_active.short_description = "Mark selected Readers as Active "

    def make_inactive(self, request, queryset):
        queryset.update(active=False)
        self.message_user(request, "Mark selected Readers Inactive successfully. ")

    make_inactive.short_description = "Mark selected Readers as Inactive "
    actions = [make_active, make_inactive]


admin.site.register(Readers, ReadersAdmin)


class RecordsAdmin(admin.ModelAdmin):
    actions_on_top = True
    actions_on_bottom = False
    list_display = ('id', 'create_time', 'status', 'fine')
    list_display_links = ('id',)
    search_fields = ('id', 'reader__name', 'reader__id', 'book__title', 'book__ISBN', 'book__id')
    list_filter = ('status', 'book__available')
    # list_editable  = ('create_time',)
    fields = ('id', 'reader', 'book', 'create_time', 'status', 'fine')

    def make_borrow(self, request, queryset):
        num = 0
        for record in queryset:
            if record.status != 'BORROWED':
                b = record.book
                if b.available:
                    b.available = False
                    b.save()
                    record.status = 'BORROWED'
                    record.save()
                    num = num + 1
                else:
                    record.status = 'WAITFORCHECK'
                    record.save()
        self.message_user(request, "%s record(s) been Mark BORROWED and others remain ." % (num))

    make_borrow.short_description = "Mark BORROWED if book is Availible "

    def make_return(self, request, queryset):
        num = 0
        for record in queryset:
            if record.status == 'BORROWED':
                b = record.book
                b.available = True
                b.save()
                nowtime = datetime.now()
                lasttime = datetime.strptime(str(record.modified_time)[0:19], "%Y-%m-%d %H:%M:%S")
                fine = (nowtime - lasttime).days - 14  # 超过14天罚款，1块钱/一天
                if fine > 0:
                    if fine > record.book.price:
                        record.fine = record.book.price
                    else:
                        record.fine = fine

                record.status = 'RETURNED'
                record.save()
                num = num + 1
        self.message_user(request, "%s record(s) been Mark Return and Calculate the Fine." % (num))

    make_return.short_description = "Mark RETURNED if book is Borrowed"

    def make_turndown(modeladmin, request, queryset):
        queryset.filter(Status='WAITFORCHECK').update(Status='TURNDOWN')

    make_turndown.short_description = "TURNDOWN All the REQUEST"

    def make_demage(self, request, queryset):
        num = 0
        for record in queryset:
            if record.status == 'BORROWED':
                record.status = 'DEMAGE'
                record.fine = record.book.price
                record.save()
                num = num + 1

        self.message_user(request, "%s record(s) been Mark Demage and Calculate the Fine." % (num))

    make_demage.short_description = "Mark Demage and Calculate the Fine if book is Borrowed "

    actions = [make_borrow, make_return, make_turndown, make_demage]

    def suit_row_attributes(self, obj):
        class_map = {
            'TURNDOWN': 'black',
            'BORROWED': 'warning',
            'WAITFORCHECK': 'info',
            'RETURNED': 'success',
            'DEMAGE': 'error'
        }
        css_class = class_map.get(obj.Status)
        if css_class:
            return {'class': css_class}


admin.site.register(Record, RecordsAdmin)
