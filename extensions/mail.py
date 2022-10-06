from urllib import request
import hikari, lightbulb, miru
from lightbulb.utils import pag, nav
import json
from difflib import get_close_matches
from datetime import date, datetime
from dateutil import parser #To parse
import pytz #get the list of timezones
from utils import get_users_data, set_profile
import uuid

plugin = lightbulb.Plugin("mail")

def build_embed(page_index, page_content):
    return hikari.Embed(title=f"Your inbox:", description=page_content)

@plugin.command
@lightbulb.option("username", "The end user's name", type=hikari.User)
@lightbulb.option("message", "What you want to tell them")
@lightbulb.command("mail", "Send a message to a user")
@lightbulb.implements(lightbulb.SlashCommand)
async def mail(ctx):
    await set_profile(ctx.author.id)
    users = await get_users_data()
    #Check if the username id they mentioned exists in the users JSON
    if str(ctx.options.username.id) in users:
        ID = str(uuid.uuid4())[:8]
        #Check if the user has already been messaged by them
        users[str(ctx.options.username.id)]["messages"].update({ID:[str(ctx.user.id), ctx.options.message]})
        with open("users.json", "w") as f:
            json.dump(users, f, indent=2)
        embed = hikari.Embed(title=f"Message Successfuly Sent ✔️",description=f"Code: {ID}\n To edit or delete this message,\n Use `/message [code] [Action]`") 
        await ctx.respond(embed)
    else:
        await ctx.respond("**It appears the user you want to message doesn't have a profile setup. A profile can be setup by using bot commands.**")



class BookingRequests(miru.View):
    def __init__(self, page, requestIDs, requestDetails, requestCount, timeout=None):
        super().__init__()
        self.page = page
        self.requestIDs = requestIDs
        self.requestDetails = requestDetails
        self.requestCount = requestCount
    
    async def updatePage(self, ctx):
        if self.requestCount == 0:
            embed = hikari.Embed(title="No more requests.")
            await ctx.edit_response(embed, components=[])
            self.stop()
            return

        embed = hikari.Embed(title="Booking Requests", description=f"`Request from:` <@{self.requestDetails[self.page][0]}>")
        embed.add_field("Date", self.requestDetails[self.page][1])
        embed.add_field("Reason", self.requestDetails[self.page][2])
        await ctx.edit_response(embed, components=self.build())
        
    async def pageLeft(self, ctx):
        if self.page == 0:
            self.page = self.requestCount - 1
        else: 
            self.page -= 1
        await self.updatePage(ctx)

    async def pageRight(self, ctx):
        
        if self.page == self.requestCount - 1:
            self.page = 0
        else:
            self.page += 1
        await self.updatePage(ctx)

    @miru.button(emoji="⏪", style=hikari.ButtonStyle.SECONDARY)
    async def btn_l(self, button: miru.Button, ctx: miru.Context) -> None:
        await self.pageLeft(ctx)
        
    
    @miru.button(label="Accept", emoji="✅", style=hikari.ButtonStyle.PRIMARY)
    async def btn_Accept(self, button: miru.Button, ctx: miru.Context) -> None:
        users = await get_users_data()
        #add the booking request to the confirmed bookings
        users[str(ctx.user.id)]["bookings"].update({self.requestIDs[self.page]:self.requestDetails[self.page]})
        #delete the booking request from the unconfirmed bookings
        users[str(ctx.user.id)]["booking_requests"].pop(self.requestIDs[self.page])
        with open("users.json", "w") as f:
            json.dump(users, f, indent=2)
        self.page -=1
        #update values just in case...   
        self.requestDetails = list(users[str(ctx.user.id)]["booking_requests"].values())
        self.requestIDs = list(users[str(ctx.user.id)]["booking_requests"].keys())
        self.requestCount = len(users[str(ctx.user.id)]["booking_requests"])
        await self.pageRight(ctx)

    @miru.button(label="Deny", emoji="❌", style=hikari.ButtonStyle.PRIMARY)
    async def btn_Deny(self, button: miru.Button, ctx: miru.Context) -> None:
        users = await get_users_data()
        
        users[str(ctx.user.id)]["booking_requests"].pop(self.requestIDs[self.page])
        with open("users.json", "w") as f:
            json.dump(users, f, indent=2)
        self.page -=1
        #update values just in case...   
        self.requestDetails = list(users[str(ctx.user.id)]["booking_requests"].values())
        self.requestIDs = list(users[str(ctx.user.id)]["booking_requests"].keys())
        self.requestCount = len(users[str(ctx.user.id)]["booking_requests"])
        await self.pageRight(ctx)

    @miru.button(emoji="⏩", style=hikari.ButtonStyle.SECONDARY)
    async def btn_r(self, button: miru.Button, ctx: miru.Context) -> None:
        await self.pageRight(ctx)

    @miru.button(label="Close", emoji="✅", style=hikari.ButtonStyle.DANGER)
    async def btn_Close(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.message.delete()
        self.stop()

#@inbox.child
#@lightbulb.command("booking_requests", "View booking requests")
#@lightbulb.implements(lightbulb.SlashSubCommand)


class inboxes(miru.View):
    def __init__(self, context ,timeout=None):
        super().__init__()
        self.context = context
    
    async def messages(self, ctx):
        await set_profile(ctx.user.id)
        users = await get_users_data()

        inbox = pag.EmbedPaginator()
        inbox.set_embed_factory(build_embed)
        if len(users[str(ctx.user.id)]["messages"].keys()): #this does not work
            for keys, values in reversed(users[str(ctx.user.id)]["messages"].items()):   
                inbox.add_line(f"<@{values[0]}> : {values[1]}")
                inbox.add_line("")
            navigator = nav.ButtonNavigator(inbox.build_pages())
            await navigator.run(self.context)
        else: await ctx.edit_response("**Your inbox is currently empty**")

    async def booking_requests(self, ctx):
        users = await get_users_data()
        requestCount = len(users[str(ctx.user.id)]["booking_requests"])
        requestDetails = list(users[str(ctx.user.id)]["booking_requests"].values())
        requestIDs = list(users[str(ctx.user.id)]["booking_requests"].keys()) 
        if requestCount > 0:    
            view = BookingRequests(0, requestIDs, requestDetails, requestCount, timeout=60)
            embed = hikari.Embed(title="Booking Requests", description=f"`Request from:` <@{requestDetails[0][0]}>")
            embed.add_field("Date", requestDetails[0][1])
            embed.add_field("Reason", requestDetails[0][2])
            #idk why it only works with original context
            message = await self.context.respond(embed, components=view.build())
            message = await message
            view.start(message)
            await view.wait()
        else: await ctx.respond("**You do not have any booking requests currently")
        
    @miru.select(
        placeholder = "Overview",
        options =[
            miru.SelectOption(label="Messages"),
            miru.SelectOption(label="Booking Requests"),
            miru.SelectOption(label="Booked Requests")
        ]
    )
    async def Inboxes(self, select: miru.Select, ctx: miru.Context) -> None:
        if select.values[0] == "Messages":
            await ctx.message.delete()
            await self.messages(ctx)
        elif select.values[0] == "Booking Requests":
            await ctx.message.delete()
            await self.booking_requests(ctx)
        elif select.values[0] == "Booked Requests":
            await ctx.respond("working on it")  
    
@plugin.command
@lightbulb.command("inbox", "Your inbox")
@lightbulb.implements(lightbulb.SlashCommand)
async def inbox(ctx):
    view = inboxes(ctx, timeout=60)
    embed = hikari.Embed(title="yes")
    message = await ctx.respond(embed, components=view.build())
    message = await message
    view.start(message)
    await view.wait()
    #add some general info here about their inbox


def load(bot):
    bot.add_plugin(plugin)