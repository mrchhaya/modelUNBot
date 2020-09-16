import discord
from qwikidata.sparql import (get_subclasses_of_item,
                              return_sparql_query_results)
import qwikidata
import hashlib
from dotenv import load_dotenv
import os,random
import pycountry,requests
from bs4 import BeautifulSoup
import re,math,pickle
load_dotenv('secrets.env')
discordToken = os.getenv('DISCORD_TOKEN')

client = discord.Client()
ck = '!un'
sparql_query = """
SELECT DISTINCT ?countryLabel ?capital ?capitalLabel ?population ?nominal_GDP ?Human_Development_Index ?currency_symbol_descriptionLabel ?head_of_governmentLabel ?area ?flag_image ?office_held_by_head_of_governmentLabel ?office_held_by_head_of_stateLabel ?head_of_stateLabel WHERE {
  ?country wdt:P31 wd:Q3624078.
  FILTER(NOT EXISTS { ?country wdt:P31 wd:Q3024240. })
  FILTER(NOT EXISTS { ?country wdt:P31 wd:Q28171280. })
  OPTIONAL { ?country wdt:P36 ?capital. }
  OPTIONAL { ?country wdt:P1082 ?population. }
  OPTIONAL { ?country wdt:P1082 ?population. }
  OPTIONAL { ?country wdt:P2131 ?nominal_GDP. }
  OPTIONAL { ?country wdt:P1081 ?Human_Development_Index. }
  OPTIONAL { ?country wdt:P38 ?currency_symbol_description. }
  OPTIONAL { ?country wdt:P6 ?head_of_government. }
  OPTIONAL {  }
  OPTIONAL { ?country wdt:P2046 ?area. }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
  OPTIONAL { ?country wdt:P41 ?flag_image. }
  OPTIONAL {  }
  OPTIONAL { ?country wdt:P1313 ?office_held_by_head_of_government. }
  OPTIONAL { ?country wdt:P1906 ?office_held_by_head_of_state. }
  OPTIONAL { ?country wdt:P35 ?head_of_state. }
}
ORDER BY (?countryLabel)
"""
res = return_sparql_query_results(sparql_query)
sq2 = """
SELECT ?instance_of ?instance_ofLabel ?shares_border_with ?shares_border_withLabel WHERE {
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }

  OPTIONAL {  }
  OPTIONAL {  }
  ?instance_of wdt:P31 wd:Q3624078.
  OPTIONAL { ?instance_of wdt:P47 ?shares_border_with. }
}
"""
borderingCountries = return_sparql_query_results(sq2)
sq3 = """
SELECT ?sovereign_state ?sovereign_stateLabel ?short_name WHERE {
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
  ?sovereign_state wdt:P31 wd:Q3624078.
  OPTIONAL { ?sovereign_state wdt:P1813 ?short_name. }
}
"""
shortNames = return_sparql_query_results(sq3)

def shortHand(s):
    list_alpha_2 = [i.alpha_2 for i in list(pycountry.countries)]
    list_alpha_3 = [i.alpha_3 for i in list(pycountry.countries)]
    for i in range(len(shortNames.get('results').get('bindings'))):
        try:
            if s == shortNames.get('results').get('bindings')[i].get('short_name').get('value').lower():
                return shortNames.get('results').get('bindings')[i].get('sovereign_stateLabel').get('value').lower()
        except:
            if(len(s)==2 and s.upper() in list_alpha_2):
                return pycountry.countries.get(alpha_2=s).name.lower()
            elif(len(s)==3 and s.upper() in list_alpha_3):
                return pycountry.countries.get(alpha_3=s).name.lower()
            else:
                return "invalid"
def pagintion(elementList,page):
    page -= 1
    chars, elementsPerPage = 0,0
    for i in range(len(elementList)):
        if chars < 1024:
            chars += len(elementList[i])
            print(chars)
            elementsPerPage = i
        elif chars > 1024:
            elementsPerPage = elementsPerPage-1
            break
        elif chars == 1024:
            elementsPerPage = i
            break
    fieldList = []
    print(elementsPerPage * page, elementsPerPage * (page+1))
    try:
        for i in range(elementsPerPage * page, elementsPerPage * (page+1)):
            fieldList.append(elementList[i])
    except IndexError:
        pass
    return fieldList

nl = []
def start():
    urls = []
    page = requests.get('https://www.un.org/securitycouncil/content/resolutions-0')
    soup = BeautifulSoup(page.content,'html.parser')
    x = soup.find_all('a')
    for y in x:
        if re.search("^[123][0-9]",y.get_text()) and len(y.get_text()) == 4:
            urls.append('https://www.un.org/securitycouncil/content/resolutions-adopted-security-council-'+y.get_text())
    for url in urls:
        soup = BeautifulSoup(requests.get(url).content,'html.parser')
        x = soup.find_all('tr')
        for td in x:
            nl.append(td.get_text() + url[-4:])
    print('done')
def search(keyword, year):
    with open('resolutions.data', 'rb') as filehandle:
        nl = pickle.load(filehandle)
    rl = []
    for y in nl:
        if keyword.lower() in y.lower() and year.lower() in y.lower():
             rl.append(y[:-4])
    return rl


@client.event
async def on_ready():
    # start()
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Model UN Nerds"))
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    t = message.content.lower()
    if t[0:3] == ck and t[0:5] != '!unbc' and t.split(" ")[1].lower() != "help" and t[0:4] != '!unr':
        embedV = discord.Embed()
        embedV.add_field(name = "Error",value="Couldn't find that country!")
        try:
            for i in range(len(res.get('results').get('bindings'))):
                if t[4:len(t)] == res.get('results').get('bindings')[i].get('countryLabel').get('value').lower() or shortHand(t[4:len(t)]) == res.get('results').get('bindings')[i].get('countryLabel').get('value').lower():
                    try:
                        name = res.get('results').get('bindings')[i].get('flag_image').get('value')[51:-1].replace("%20", "_") + 'g'
                        for j in range(0,10):
                            name = name.replace("%2" + str(j),"")
                        m = hashlib.md5()
                        m.update(name.encode('utf-8'))
                        h = str(m.hexdigest())
                        url = "https://upload.wikimedia.org/wikipedia/commons/" + h[0] + "/" + h[0] + h[1] + "/" + name
                        embedV = discord.Embed(title=res.get('results').get('bindings')[i].get('countryLabel').get('value'),color=int(hex(random.randint(0,16777215)),16), url=url)
                        embedV.set_image(url=str(url))
                        await message.channel.send(url)
                    except AttributeError:
                        embedV = discord.Embed(title=res.get('results').get('bindings')[i].get('countryLabel').get('value'),color=0xebab34)
                    try:
                        embedV.add_field(name = "Capital", value=res.get('results').get('bindings')[i].get('capitalLabel').get('value'), inline = False)
                    except AttributeError:
                        embedV.add_field(name = "Capital", value="No Value", inline = False)
                    try:
                        embedV.add_field(name = "Nominal GDP", value='US$ ' +'{:20,.2f}'.format(float(res.get('results').get('bindings')[i].get('nominal_GDP').get('value'))), inline = False)
                    except AttributeError:
                        embedV.add_field(name = "Nominal GDP", value="No Value", inline = False)
                    try:
                        embedV.add_field(name = "Population", value='{:20,.2f}'.format(float(res.get('results').get('bindings')[i].get('population').get('value'))), inline = False)
                    except AttributeError:
                        embedV.add_field(name = "Population", value= "No Value", inline = False)
                    try:
                        embedV.add_field(name = "Human Development Index", value = res.get('results').get('bindings')[i].get('Human_Development_Index').get('value'), inline= False)
                    except AttributeError:
                        embedV.add_field(name = "Human Development Index", value= "No Value", inline = False)
                    try:
                        embedV.add_field(name = res.get('results').get('bindings')[i].get('office_held_by_head_of_governmentLabel').get('value'), value = res.get('results').get('bindings')[i].get('head_of_governmentLabel').get('value'), inline= True)
                    except AttributeError:
                        embedV.add_field(name = "Head of Government", value= "No Value", inline = True)
                    try:
                        embedV.add_field(name = res.get('results').get('bindings')[i].get('office_held_by_head_of_stateLabel').get('value'), value = res.get('results').get('bindings')[i].get('head_of_stateLabel').get('value'), inline= True)
                    except AttributeError:
                        embedV.add_field(name = "Head of State", value= "No Value", inline = True)
                    try:
                        embedV.add_field(name = "Area", value = '{:20,.2f}'.format(float(res.get('results').get('bindings')[i].get('area').get('value')))+' km²', inline= False)
                    except AttributeError:
                        embedV.add_field(name = "Area", value= "No Value", inline = False)
                    try:
                        embedV.add_field(name = "Currency", value = res.get('results').get('bindings')[i].get('currency_symbol_descriptionLabel').get('value'), inline= False)
                    except AttributeError:
                        embedV.add_field(name = "Currency", value= "No Value", inline = False)
        except IndexError:
            await message.channel.send("Error.")
        await message.channel.send(embed = embedV)
    elif t[0:5] == ck+'bc':
        embedBC = discord.Embed()
        embedBC.add_field(name = "Error",value="Couldn't find that country!")
        l = []
        for i in range(len(borderingCountries.get('results').get('bindings'))):
            try:
                if t[6:len(t)] == borderingCountries.get('results').get('bindings')[i].get('instance_ofLabel').get('value').lower():
                    for j in range(len(borderingCountries.get('results').get('bindings')[i].get('instance_ofLabel'))):
                            embedBC = discord.Embed(title="Bordering Countries of " + borderingCountries.get('results').get('bindings')[i].get('instance_ofLabel').get('value'), color=int(hex(random.randint(0,16777215)),16))
                            l.append(borderingCountries.get('results').get('bindings')[i].get('shares_border_withLabel').get('value'))
            except AttributeError:
                pass
        l = list(dict.fromkeys(l))
        for i in range(len(l)):
            embedBC.add_field(name = "Bordering Country " + str(i+1) + ": ",value=l[i],inline = False)
        await message.channel.send(embed = embedBC)
    elif t[0:4] == '!bad':
        await message.channel.send(str(t[5:len(t)]) + " sucks!")
    elif t[0:3] == ck and t.split(" ")[1].lower() == "help":
        embedHelp = discord.Embed(title="Commands: ", color = int(hex(random.randint(0,16777215)),16))
        embedHelp.add_field(name = "Information about Country: ", value = "Returns information about a certain country. Usage: !un {country_name}")
        embedHelp.add_field(name = "Bordering Countries to Country", value = "Returns all of the bordering countries to a certain country. Usage: !unbc {country_name}")
        embedHelp.add_field(name = "UN Resolution Search", value = "Searches the UN database for all resolutions with a certain keyword in a certain year. Usage: !unr {country_name} {year}")
        embedHelp.add_field(name = "Author: ", value="Mohit Chhaya - https://github.com/mrchhaya, Sundays are for Chick-Fil-A#2964", inline=False)
        await message.channel.send(embed = embedHelp)
    elif t[0:4] == ck+'r':
        page =1
        left_reactCount, right_reactCount = 1, 1
        embedRes1 = discord.Embed(title="Resolutions containing the keyword: " + t.split()[1] + " in the year, " + t.split()[2],color=int(hex(random.randint(0,16777215)),16))
        try:
            embedRes1.add_field(name = "Resolution: ", value=''.join(pagintion(search(t.split()[1],t.split()[2]),right_reactCount)), inline=False)
            embedRes1.add_field(name = "Resolution: ", value=''.join(pagintion(search(t.split()[1],t.split()[2]),right_reactCount+1)), inline=False)
            embedRes1.add_field(name = "Resolution: ", value=''.join(pagintion(search(t.split()[1],t.split()[2]),right_reactCount+2)), inline=False)
            embedRes1.add_field(name = "Resolution: ", value=''.join(pagintion(search(t.split()[1],t.split()[2]),right_reactCount+3)), inline=False)
            embedRes1.add_field(name = "Resolution: ", value=''.join(pagintion(search(t.split()[1],t.split()[2]),right_reactCount+4)), inline=False)
            counter = 0
            for i in embedRes1.fields:
                if i.value == '':
                    embedRes1.remove_field(counter)
                    counter -= 1
                counter += 1
            if embedRes1.fields == '[]':
                embedRes1.add_field(name="Resolution: ", value='None Found.',
                                    inline=False)
            await message.channel.send(embed=embedRes1)
        except IndexError:
            await message.channel.send('Index Error, Did you have both a country and year?')

client.run(discordToken)



# Model UN Bot
# Bring up a basic details of a country such as:
# Population ✅
# GDP ✅
# HDI ✅
# Currency ✅
# Leader ✅
# Ruling party
# Area ✅
# Bordering countries ✅
# Major Religion


#✅
# https://www.un.org/en/sections/documents/general-assembly-resolutions/index.html
# Be able to find resolutions where [enter country] was involved from https://www.un.org/securitycouncil/content/resolutions-0 and bring them up.
# Use keywords to bring up resolutions from https://www.un.org/securitycouncil/content/resolutions-0