import json
import requests
import uuid
import discord
from discord.ext import commands
from discord_webhook import DiscordWebhook

helium_api_endpoint = "https://api.helium.io/v1/"
helium_explorer_tx = "https://explorer.helium.com/txns/"
config_file = r".\config.json"
discordWebhook = "discord webhook here"
# Generate a UUID from a host ID, sequence number, and the current time
headers = {'User-Agent': str(uuid.uuid1())}

bot = commands.Bot(command_prefix="$")
global activities, config, hs, wellness_check, send, send_report, send_wellness_check

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

def addHeliumAddress(address):
    print("Entered")
    #Confirm address is alpha numeric
    #Concatenate address to json format
    jsonStr = '{"hotspot": ' + address + ', "discord_webhook": "https://discord.com/api/webhooks/936333349197316188/bb-1zuXa3p5cyImLKE8S1d8U0Cx36sdvv89smb2KcY_qcK67_Qf2h1MG3Ad61WAwclYK", "name": ""}'
    # Append-adds to the end of the config file
    file1 = open("config.json", "a")  # append mode
    file1.write(jsonStr)
    print("Wrote to config")
    file1.close()
#____________________________________________________________________________________________________________________________________________________


#--------------------------------------------------------------------------------------------
# Zees is ze main function
#--------------------------------------------------------------------------------------------
"""with open(config_file) as json_data_file:
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
"""
            #sendDiscordMessage()
            #print(hs_add)


#***********************************************************************************************************
#          BOT COMMANDS
#***********************************************************************************************************
@bot.command()
async def add(ctx, args):
    #TODO add code to check if the address already exists when trying to add a new one
    #adds the helium hotspot miner address to config file
    if not str(requests.get(helium_api_endpoint + "hotspots/" + args, headers=headers)) == "<Response [200]>":
        print("The parameter is: " + args)
        print(str(requests.get(helium_api_endpoint + "hotspots/" + args, headers=headers)))
        await ctx.send("This hotspot address does not exist. Hotspot was NOT added.")
    else:
        addHeliumAddress(args)
        await ctx.send("Your hotspot has been added. You can use the $status command to see your hotspot's status.")     

bot.run("OTM2MzI4MTY0NzY5MTQwODM2.YfLljg.9GibXN-mUpYZjaONcVeVgIUOnxM")