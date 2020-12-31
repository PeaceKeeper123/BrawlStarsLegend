"""Legend Gaming Cog

Originally Coded by: GR8
Ported to V3 by: ThePeaceKeeper, Generaleoley

"""

import discord
#from discord.ext import commands # wtf? edit below
from redbot.core import commands, checks
import brawlstats # pip install brawlstats


credits = "Bot by Legend Gaming. Original Code by GR8" # :( 


class BrawlStars(commands.Cog):
    """Live statistics for Brawl Stars"""

    def __init__(self, bot):
        self.bot = bot
        self.bstools = self.bot.get_cog('bstools')
        self.token_task = self.bot.loop.create_task(self.api_init())
        

    async def api_init(self):
        """"Initializes the api, don't call this."""
        token = await self.bot.get_shared_api_tokens("brawlstars") # todo check here if it's not saved, just make sure to save it using !set api brawlstars,token
        if token is None:
            print("Brawl Stars token is not set, use [p]set api brawlstars,YOURAPITOKEN")
            raise ValueError
        self.brawl = brawlstats.Client(self.auth.getBSToken(), is_async=False) # Yes defining class attrs (self) outside __init__ is not a good practice but this is to get around the async issues


    @commands.command(aliases=['brawlprofile'])
    async def brawlProfile(self, ctx, member: discord.User = None):
        """View your Brawl Stars Profile Data and Statstics."""

        member = member or ctx.message.author

        #await self.bot.type() QOL change, i'm pretty sure new version is async with self.bot.type() but I CBA
        try:
            profiletag = await self.bstools.getTag(member) # edit for new bstools
            profiledata = self.brawl.get_player(profiletag)
        except brawlstats.RequestError as e:
            return await ctx.send('```\n{}: {}\n```'.format(e.code, e.error))
        except KeyError:
            return await ctx.send("You need to first save your profile using ``{}bsave #GAMETAG``".format(ctx.prefix))

        embed = discord.Embed(color=0xFAA61A)
        embed.set_author(name="{} (#{})".format(await self.tags.formatName(profiledata.name), profiledata.tag),
                         icon_url=profiledata.club.badge_url if profiledata.club is not None else "",
                         url="https://brawlstats.com/profile/" + profiledata.tag)
        embed.set_thumbnail(url=profiledata.avatar_url)
        embed.add_field(name="Trophies", value="{} {:,}".format(self.getLeagueEmoji(profiledata.trophies), profiledata.trophies), inline=True)
        embed.add_field(name="Highest Trophies", value="{} {:,}".format(self.getLeagueEmoji(profiledata.highest_trophies), profiledata.highest_trophies), inline=True)
        embed.add_field(name="Level", value="{} {:,}".format(self.emoji("xp"), profiledata.exp_level), inline=True)
        if profiledata.club is not None:
            embed.add_field(name="Club {}".format(profiledata.club.role),
                            value=profiledata.club.name, inline=True)
        embed.add_field(name="Brawlers Unlocked", value="{} {}/22".format(self.emoji("default"), profiledata.brawlers_unlocked), inline=True)
        embed.add_field(name="Victories", value="{} {}".format(self.emoji("bountystar"), profiledata.victories), inline=True)
        embed.add_field(name="Solo SD Victories", value="{} {}".format(self.emoji("showdown"), profiledata.solo_showdown_victories), inline=True)
        embed.add_field(name="Duo SD Victories", value="{} {}".format(self.emoji("duoshowdown"), profiledata.duo_showdown_victories), inline=True)
        embed.add_field(name="Best Time as Big Brawler", value="{} {}".format(self.emoji("bossfight"), profiledata.best_time_as_big_brawler), inline=True)
        embed.add_field(name="Best Robo Rumble Time", value="{} {}".format(self.emoji("roborumble"), profiledata.best_robo_rumble_time), inline=True)
        embed.set_footer(text=credits) 

        await ctx.send(embed=embed)

    @commands.command()
    async def club(self, ctx, clantag):
        """View Brawl Stars Club statistics and information """

        clantag = self.bstools.formatTag(clantag)

        if not self.tags.verifyTag(clantag):
            return await ctx.send("The clantag you provided has invalid characters. Please try again.")

        try:
            clandata = self.brawl.get_club(clantag)
        except brawlstats.RequestError:
            return await ctx.send("Error: cannot reach Brawl Stars Servers. Please try again later.")

        embed = discord.Embed(description=clandata.description, color=0xFAA61A)
        embed.set_author(name=clandata.name + " (#" + clandata.tag + ")",
                         icon_url=clandata.badge_url) # url removed because website isn't hosted
        embed.set_thumbnail(url=clandata.badge_url)
        embed.add_field(name="Members", value="{} {}/100".format(self.emoji("gameroom"), clandata.members_count), inline=True)
        embed.add_field(name="President", value=await self.getClanLeader(clandata.get('members')), inline=True)
        embed.add_field(name="Online", value="{} {:,}".format(self.emoji("online"), clandata.online_members), inline=True)
        embed.add_field(name="Score", value="{} {:,}".format(self.emoji("bstrophy2"), clandata.trophies), inline=True)
        embed.add_field(name="Required Trophies",
                        value="{} {:,}".format(self.emoji("bstrophy"), clandata.required_trophies), inline=True)
        embed.add_field(name="Status", value=":envelope_with_arrow: {}".format(clandata.status), inline=True)
        embed.set_footer(text=credits)

        await ctx.send(embed=embed)

    @commands.command(paliases=['bssave'])
    async def bsave(self, ctx, profiletag: str, member: discord.User = None):
        """ save your Brawl Stars Profile Tag
        Example:
            [p]bssave #CRRYTPTT @ThePeaceKeeper
            [p]bssave #CRRYRPCC
        """

        server = ctx.message.server
        author = ctx.message.author

        profiletag = self.tags.formatTag(profiletag)

        if not self.tags.verifyTag(profiletag):
            return await ctx.send("The ID you provided has invalid characters. Please try again.")


         # Trying to save tag for someone else (Generaleoley way, personally feel it's cleaner)
        if member is not None and member != ctx.author:
            if await self.bot.is_mod(ctx.author) is False:
                await ctx.send(
                    "Sorry you cannot save tags for others. You need a mod permission level"
                )
                return

        if member is None:
            user = ctx.author

        try:
            profiledata = self.brawl.get_player(profiletag)

            # Account sharing is a thing and this makes it un-necessarily complicated
            # checkUser = await self.tags.getUserBS(server.members, profiletag)
            # if checkUser is not None:
            #     return await self.bot.say("Error, This Player ID is already linked with **" + checkUser.display_name + "**")

            await self.bstools.saveTag(member, profiletag)

            embed = discord.Embed(color=discord.Color.green())
            avatar = member.avatar_url if member.avatar else member.default_avatar_url
            embed.set_author(name='{} (#{}) has been successfully saved.'.format(await self.tags.formatName(profiledata.name), profiletag),
                             icon_url=avatar)
            await ctx.send(embed=embed)
        except brawlstats.NotFoundError:
            return await ctx.send("We cannot find your ID in our database, please try again.")
        except brawlstats.RequestError:
            return await ctx.send("Error: cannot reach Brawl Stars Servers. Please try again later.")

