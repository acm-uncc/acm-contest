from django.contrib import admin

# Register your models here.
from jam import models

admin.site.register(models.Score)
admin.site.register(models.Part)
admin.site.register(models.Problem)
admin.site.register(models.Submission)
