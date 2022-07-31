import hikari, lightbulb

plugin = lightbulb.Plugin("scheduling")


@plugin.command
@lightbulb.option("reason", "Describe the reason in the least amount of words")
@lightbulb.option("timezone", "The timezone on said time", autocomplete=True)
@lightbulb.option("time", "time on said date using the 24-HOUR CLOCK")
@lightbulb.option("day", "The day on said month", type=int, max_value=31)
@lightbulb.option("month", "The month", choices=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
@lightbulb.option("username", "The user you want to book", type=hikari.User)
@lightbulb.command("book", "Book an appointment with a user")
@lightbulb.implements(lightbulb.SlashCommand)
async def book(ctx):
    co = ctx.options
    SelectedDate = parser.parse(f"{co.month} {co.day} {date.today().year}")
    if datetime.today() > SelectedDate:
        await ctx.respond("The date you've entered is in the past.") 
    else:
        with open("users.json", "r") as f:
            users = json.load(f)
        strDate = f"{co.month} {co.day}, {co.time} {co.timezone}"
        users[str(co.username.id)]["booking_requests"].update({ctx.author.id:[strDate, co.reason]})
        with open("users.json", "w") as f:
            json.dump(users, f, indent=2)
        await ctx.respond(f"Booking request scheduled on {strDate} ")

@plugin.command
@lightbulb.command("bookings", "View approved bookings")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def bookings(ctx):
    pass

@plugin.command
@lightbulb.command("calander", "View booked appointments this week")
@lightbulb.implements(lightbulb.SlashCommand)
async def calander(ctx):
    pass
    
def load(bot):
    bot.add_plugin(plugin)