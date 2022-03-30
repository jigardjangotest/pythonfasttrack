from django.contrib import admin
from .models import User,Course,Questions,Result,Faculty_Subject
# Register your models here.
admin.site.register(User)
admin.site.register(Course)
admin.site.register(Questions)
admin.site.register(Result)
admin.site.register(Faculty_Subject)