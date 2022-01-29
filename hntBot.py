import json
import requests
import uuid
import discord
from discord.ext import commands
from discord_webhook import DiscordWebhook

helium_api_endpoint = "https://api.helium.io/v1/"
helium_explorer_tx = "https://explorer.helium.com/txns/"
config_file = r"E:\Rocco\Documents\HNT Bot\config.json"
discordWebhook = "https://discord.com/api/webhooks/936333349197316188/bb-1zuXa3p5cyImLKE8S1d8U0Cx36sdvv89smb2KcY_qcK67_Qf2h1MG3Ad61WAwclYK"
# Generate a UUID from a host ID, sequence number, and the current time
headers = {'User-Agent': str(uuid.uuid1())}

bot = commands.Bot(command_prefix="$")

@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')

@bot.command()
async def add(ctx, args):
    #add the helium hotspot miner address to config file
    if str(requests.get(helium_api_endpoint + "badapicall", headers=headers)):
        await ctx.send("This Hotspot address does not exist. Hotspot was NOT added.")
    #await ctx.send(args)

bot.run("OTM2MzI4MTY0NzY5MTQwODM2.YfLljg.LJb_6kE0_hfz8QDw_mWt3t7XOYo")

#*******************************************************************************************
#   Functions
#*******************************************************************************************
def nice_hotspot_name(name):
    return name.replace("-", " ").upper()

def nice_hotspot_initials(name):
    if not bool(config["initials"]):
        name = nice_hotspot_name(name)
        config["initials"] = "".join(item[0].upper() for item in name.split())
    return config["initials"]

def sendDiscordMessage():
    messageContent = "This is just a test!"
    webhook = DiscordWebhook(url="https://discord.com/api/webhooks/936333349197316188/bb-1zuXa3p5cyImLKE8S1d8U0Cx36sdvv89smb2KcY_qcK67_Qf2h1MG3Ad61WAwclYK", content=messageContent)
    # send
    webhook_response = webhook.execute()
#____________________________________________________________________________________________________________________________________________________

#--------------------------------------------------------------------------------------------
# Zees is ze main function
#--------------------------------------------------------------------------------------------
global activities, config, hs, wellness_check, send, send_report, send_wellness_check
with open(config_file) as json_data_file:
        for jsonObj in json_data_file:
            #getting the next hotspot name to process
            config = json.loads(jsonObj)

            # try to get json or return error
            status = ""
            # LIVE API data
            activity_endpoint = (
                helium_api_endpoint + "hotspots/" + config["hotspot"] + "/activity/"
            )
            activity_request = requests.get(activity_endpoint, headers=headers)

            #getting the name, owner, status, reward scale from api
            hs_endpoint = helium_api_endpoint + "hotspots/" + config["hotspot"]
            hs_request = requests.get(hs_endpoint, headers=headers)
            data = hs_request.json()

            hotspot_data = data["data"]

            hs_add = {
                "owner": hotspot_data["owner"],
                "name": nice_hotspot_name(hotspot_data['name']),
                #"initials": nice_hotspot_initials(hotspot_data["name"]),
                "status": str(hotspot_data["status"]["online"]).upper(),
                "height": hotspot_data["status"]["height"],
                "block": hotspot_data["block"],
                "reward_scale": "{:.2f}".format(round(hotspot_data["reward_scale"], 2)),
            }
            
            #sendDiscordMessage()
            print(hs_add)

