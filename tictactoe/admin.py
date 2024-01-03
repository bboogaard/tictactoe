from django.contrib import admin

from tictactoe import models


class GameAdmin(admin.ModelAdmin):
    readonly_fields = ('board',)


admin.site.register(models.GameSession)

admin.site.register(models.Player)

admin.site.register(models.Game, GameAdmin)
