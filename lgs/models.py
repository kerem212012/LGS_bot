from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    tg_id = models.CharField(max_length=150, blank=True)
    wrongs = models.IntegerField(default=0,verbose_name='Wrongs',)
    admin = models.BooleanField(default=False,verbose_name="Admin")
    corrects = models.IntegerField(default=0,verbose_name='Corrects')
    def __str__(self):
        return f"{self.first_name} {self.tg_id}"

class Subject(models.Model):
    title = models.CharField(verbose_name="Title", max_length=150, blank=True)
    description = models.TextField(
        verbose_name='Description',
        blank=True,
        max_length=300,
    )
    def __str__(self):
        return self.title

class Quiz(models.Model):
    created_at = models.DateTimeField(verbose_name="Created at", default=timezone.now)
    question=models.ImageField(verbose_name='Question',blank=True)
    right_answer = models.CharField(
        verbose_name='Right Answer',
        blank=True,
        max_length=300,
    )
    wrong_answer_1 = models.CharField(
        verbose_name='Wrong Answer 1',
        blank=True,
        max_length=300,
    )
    wrong_answer_2 = models.CharField(
        verbose_name='Wrong Answer 2',
        blank=True,
        max_length=300,
    )
    wrong_answer_3 = models.CharField(
        verbose_name='Wrong Answer 3',
        blank=True,
        max_length=300,
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="quiz_types",
        blank=True,
        null=True,
        verbose_name="Type"
    )
    def __str__(self):
        return self.right_answer
