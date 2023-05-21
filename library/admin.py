from django.contrib import admin
from library.models import AuthUser, Books, Libraries, Admins, Loans, Reserves, Comments, Storages

admin.site.register([AuthUser, Books, Libraries, Admins, Loans, Reserves, Comments, Storages])
