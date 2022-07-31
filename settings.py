import lightbulb, hikari
import json

plugin = lightbulb.Plugin("settings")

async def get_users_data():
    with open("users.json", "r") as f:
        users = json.load(f)
    
async def set_profile(userID):
    #make em a profile in the JSON if they don't got one already
    with open("users.json", "r") as f:
        users = json.load(f)
    if str(userID) in users:
        return False
    else:
        users[str(userID)] = {}
        users[str(userID)]["description"] = "This profile has not been edited yet. This can be changed using `/settings profile_description`"
        users[str(userID)]["messages"] = {}
        users[str(userID)]["appointments"] = {}
        users[str(userID)]["daily_updates"] = False

    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)
    f.close()
    return True

@plugin.command
@lightbulb.command("settings", "Commands to personalize this bot to your fitting")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def settings(ctx):
    pass

@settings.child
@lightbulb.option("description", "Your new profile description")
@lightbulb.command("profile_description", "Change your profile description to your liking")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def profile_description(ctx):
    with open("users.json", "r") as f:
        users = json.load(f)
    old_desc = users[str(ctx.author.id)]["description"]
    users[str(ctx.author.id)]["description"] = ctx.options.description
    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)
    #MAKE A EMBED HERE WITH A BEFORE AND AFTER
    await ctx.respond("**Your description has been changed**")
    
    

@settings.child
@lightbulb.command("daily_updates", "Toggle to receive a update on your inbox daily by dms")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def daily_updates(ctx):
    await set_profile(ctx.author.id)
    with open("users.json", "r") as f:
        users = json.load(f)
    #This code is unnecessarily long plz find a better way to write this
    users[str(ctx.author.id)]["daily_updates"] = not users[str(ctx.author.id)]["daily_updates"] #there is probably a much shorter way to write this
    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)
    
    embed = hikari.Embed(title="Daily updates has been toggled \✔️", description=f"`Daily_updates : {users[str(ctx.author.id)]['daily_updates']}`")
    await ctx.respond(embed)

def load(bot):
    bot.add_plugin(plugin)