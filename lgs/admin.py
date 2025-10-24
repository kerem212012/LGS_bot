from django.contrib import admin

from lgs.models import CustomUser, Quiz, Subject


@admin.register(CustomUser)
class AdminCustomUser(admin.ModelAdmin):
    pass

@admin.register(Subject)
class AdminSubject(admin.ModelAdmin):
    pass


@admin.register(Quiz)
class AdminQuiz(admin.ModelAdmin):
    pass

