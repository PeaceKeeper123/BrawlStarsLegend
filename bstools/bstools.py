import discord
from redbot.core import Config, checks, commands

# I'm not doing a seperate tags class it's not needed because there isn't SQL 
class BSTools(commands.Cog):
  def __init__(self,  bot):
    self.bot = bot;
    self.config = Config.get_conf(self, identifier=9034283423)
    default_user = { # todo feel free to do multiple tags, I really don't have the time rn @TPK
      'tag': None
    }
    self.config.register_user(**default_user) # User becauser it doesn't matter what server they are in
    
   def getTag(self, user: int):
    """Returns tag (str) without # or None if it wasn't saved"""
    self.config.user(int).tag()
    
   def saveTag(self, user: int, tag: str):
    """Saves user tag. Doesn't return anything. Throws ValueError if the tag is invalid"""
    
    
