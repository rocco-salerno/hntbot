from email import message
import json
import requests
import uuid
import discord, random, asyncio
from discord.ext import commands, tasks
from discord_webhook import DiscordWebhook
from pycoingecko import CoinGeckoAPI


helium_api_endpoint = "https://api.helium.io/v1/"
helium_explorer_tx = "https://explorer.helium.com/txns/"
config_file = r".\config.json"
webhook_file = ".\webhook.json"
webhook = ""
token = ""
client =discord.Client()
# Generate a UUID from a host ID, sequence number, and the current time
headers = {'User-Agent': str(uuid.uuid1())}
bot = commands.Bot(command_prefix="$")

global activities, config, hs, wellness_check, send, send_report, send_wellness_check, discordGroupMessage

#*******************************************************************************************
#   Functions
#*******************************************************************************************
def nice_hnt_amount_or_seconds(amt):
    niceNum = 0.00000001
    niceNumSmall = 100000000

    if isinstance(amt, float):
        # float. for time i
        amt_output = "{:.2f}".format(amt)
    else:
        # int. up to 3 decimal payments
        amt_output = "{:.3f}".format(amt * niceNum)

    # int. 8 decimal places for micropayments
    # if amt > 0 and amt < 100000 :
    if amt in range(0, 100000):
        amt_output = "{:.8f}".format(amt / niceNumSmall).rstrip("0")
        amt_output = f"`{amt_output}`"

    return str(amt_output)

def getWebhook():
    openJson = open(webhook_file)
    data = json.load(openJson)
    webhook = data["webhook"]
    print ("The webhook is: " + webhook)
    return webhook

def getToken():
    openJson = open(webhook_file)
    data = json.load(openJson)
    token = data["token"]
    print("The token is: " + token)
    return token

def getStatusIcon(currStatus):
    if str(currStatus) == "ONLINE":
        statusIcon = "🟢"
    else:
        statusIcon = "🔴"
    return statusIcon

def nice_hotspot_name(name):
    return name.replace("-", " ").upper()

#def nice_hotspot_initials(name):
#    if not bool(config["initials"]):
#        name = nice_hotspot_name(name)
#        config["initials"] = "".join(item[0].upper() for item in name.split())
#    return config["initials"]

def sendDiscordMessage(messageConent):
    webhook = DiscordWebhook(url=getWebhook(), content=messageConent)
    # send
    webhook_response = webhook.execute()

def addHeliumAddress(address,userID):
    print("Entered addHeliumAddress")
    #Confirm address is alpha numeric
    if address is None:
        return "Error: New address is null"

    #Get discord server webhook
    webhook = getWebhook()

    #Concatenate address to json format
    jsonStr = {"hotspot": address,
                "discord_webhook": webhook,
                "name": userID}

    #appends the new address to config file
    write_json(jsonStr)

# function to add to JSON
def write_json(new_data, filename=config_file):
    with open(filename,'r+') as file:
          # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data["hotspotArray"].append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)

def getAPIDataToMessage(hs_endpoint):
    hs_request = requests.get(hs_endpoint, headers=headers)
    data = hs_request.json()
    hotspot_data = data["data"]
            
    #hotspot data
    hs_add = {
        "owner": hotspot_data["owner"],
        "name": nice_hotspot_name(hotspot_data['name']),
        #"initials": nice_hotspot_initials(hotspot_data["name"]),
        "status": str(hotspot_data["status"]["online"]).upper(),
        "height": hotspot_data["status"]["height"],
        "block": hotspot_data["block"],
        "reward_scale": "{:.2f}".format(round(hotspot_data["reward_scale"], 2)),
    }
    
    #getting the account balance
    wallet_request = requests.get(helium_api_endpoint + "accounts/" + hs_add["owner"], headers=headers)
    wallet = wallet_request.json()
    balance = nice_hnt_amount_or_seconds(wallet["data"]["balance"])
            
    #print(getStatusIcon(hs_add["status"]))
    discordGroupMessage = (
                            "📡**" + hs_add["name"] + "**📡\n"
                            + getStatusIcon(hs_add["status"]) + " " + hs_add["status"] + getStatusIcon(hs_add["status"]) + "\n"
                            + "⚖️  Reward Scale: " + hs_add["reward_scale"] + " ⚖️\n"
                            + "💰️ Wallet Balance: " + balance + " 💰️\n\n"
                        )
    return discordGroupMessage

def checkAddressExists(heliumAddress, uName, addrExist):
    iter = 0
    with open(config_file) as json_data_file:
        config = json.load(json_data_file)
        for index in config["hotspotArray"]:
            if str(config["hotspotArray"][iter]["hotspot"]) == heliumAddress:
                print("The helium address already exists")
                uName = str(config["hotspotArray"][iter]["name"])
                addrExist = True
                break
    print(str(addrExist) + " " + uName)
    return addrExist, uName
#____________________________________________________________________________________________________________________________________________________


#--------------------------------------------------------------------------------------------
# Zees is ze main functeen
#--------------------------------------------------------------------------------------------
def getAllHotspots():
    discordMassMessage = ""
    i=0
    with open(config_file) as json_data_file:
        config = json.load(json_data_file)
        for index in config["hotspotArray"]:
            print("index: " + str(i))
            # try to get json or return error
            status = ""
            #LIVE API data

            #getting the name, owner, status, reward scale from api
            hs_endpoint = helium_api_endpoint + "hotspots/" + config["hotspotArray"][i]["hotspot"]
            #getAPIDataToMessage(hs_endpoint)

            #print(discordGroupMessage)
            discordMassMessage = discordMassMessage + str(getAPIDataToMessage(hs_endpoint))
            i+=1
            #print(hs_add)
    return discordMassMessage

#***********************************************************************************************************
#          BOT COMMANDS
#***********************************************************************************************************
@bot.command()
async def add(ctx, args):
    addressExists = False
    userName = ""
    print("YOUR ID: " + str(ctx.author))
    #adds the helium hotspot miner address to config file
    result = checkAddressExists(args, userName, addressExists)
    if result[0]:
        await ctx.send("That hotspot address was already added by: " + result[1])
    elif not str(requests.get(helium_api_endpoint + "hotspots/" + args, headers=headers)) == "<Response [200]>":
        print("The parameter is: " + args)
        print(str(requests.get(helium_api_endpoint + "hotspots/" + args, headers=headers)))
        await ctx.send("This hotspot address does not exist. Hotspot was NOT added.")
    else:
        addHeliumAddress(args, str(ctx.author))
        await ctx.send("Your hotspot has been added. You can use the $status command to see your hotspot's status.")

# status of all the users hotspots
@bot.command()
async def status(ctx):
    foundHotspot = False
    userID = str(ctx.author)
    messageToSend = ""
    i = 0
    with open(config_file) as json_data_file:
        config = json.load(json_data_file)
        for index in config["hotspotArray"]:
            if str(config["hotspotArray"][i]["name"]) == userID:
                foundHotspot = True
                print("Found a hotspot for user")
                #getting the name, owner, status, reward scale from api
                hs_endpoint = helium_api_endpoint + "hotspots/" + config["hotspotArray"][i]["hotspot"]
                await ctx.send(str(getAPIDataToMessage(hs_endpoint)))
            i = i+1
        if not foundHotspot:
            print("No hotspots found with that user ID")
            await ctx.send("Sorry, I could not find your hotspot(s).")


#bot sends alerts +- 5% coin price
@tasks.loop(hours=24.0)
async def getAlert():
    cg = CoinGeckoAPI()
    messageToSend = ""
    hntUpdate = cg.get_price(ids='helium', vs_currencies='usd', include_24hr_change=True)
    percChange = "{:.2f}".format(hntUpdate["helium"]["usd_24h_change"])
    if float(str(percChange)) >= 5:
        messageToSend = ("⬆️ HNT has gone up " + str(percChange) + "% ⬆️\n"
                        + "The current price of HNT is: $" + str(hntUpdate["helium"]["usd"]))
    elif float(str(percChange)) <= -5:
        messageToSend = ("⬇️ HNT has gone down " + str(percChange) + "% ⬇️ \n" 
                        + "The current price of HNT is: $" + str(hntUpdate["helium"]["usd"]))
    guild = bot.get_guild(341747768810799105)
    channel = guild.get_channel(936713741041549333)
    await channel.send(messageToSend)

# get current price of HNT in US dollars
@bot.command()
async def price(ctx):
    cg = CoinGeckoAPI()
    hntUpdate = cg.get_price(ids='helium', vs_currencies='usd', include_24hr_change=True)
    await ctx.send("The current price of Helium in USD is $" + str(hntUpdate["helium"]["usd"]))

@bot.event
async def on_ready():
    getAlert.start()

#sendDiscordMessage(getAllHotspots())
bot.run(str(getToken()))