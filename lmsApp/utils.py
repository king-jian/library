import random

from .models import Book, Readers, Record


def create_book():
    for i in range(30):
        b = Book.objects.create(title="哈利波特%d" % (random.randrange(1, 1000)),
                                author="哈利波特%d" % (random.randrange(1, 1000)),
                                ISBN="%d" % (random.randrange(1, 1000)),
                                publisher="上海%d" % (random.randrange(1, 1000)),
                                pages="%d" % (random.randrange(1, 1000)),
                                position="A-%d" % (random.randrange(1, 1000)),
                                price="%d" % (random.randrange(10, 99)))
        b.save()


def create_user():
    for i in range(30):
        a = Readers.objects.create(name="king%d" % (random.randrange(1, 1000)),
                                   student_card="%d" % (random.randrange(1000, 1000000000)),
                                   password="%d" % (random.randrange(100, 999)))
        a.save()


def create_record():
    for i in range(30):
        try:
            c = Record.objects.create(book=Book.objects.get(id=random.randrange(1, 150)),
                                      reader=Readers.objects.get(id=random.randrange(1, 150)),
                                      fine="%d" % (random.randrange(1, 100)))
            c.save()
        except:
            pass

