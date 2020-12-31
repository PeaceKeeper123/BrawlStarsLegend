from .brawlstars import BrawlStars

def setup(bot):
    cog = BrawlStars(bot)
    bot.add_cog(cog)