import discord
from qwikidata.sparql import (get_subclasses_of_item,
                              return_sparql_query_results)
import qwikidata
import hashlib
from dotenv import load_dotenv
import os

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


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    t = message.content.lower()
    if t[0:3] == ck and t[0:5] != '!unbc':
        embedV = discord.Embed()
        try:
            for i in range(len(res.get('results').get('bindings'))):
                if t[4:len(t)] == res.get('results').get('bindings')[i].get('countryLabel').get('value').lower():
                    try:
                        name = res.get('results').get('bindings')[i].get('flag_image').get('value')[51:-1].replace("%20", "_") + 'g'
                        for j in range(0,10):
                            name = name.replace("%2" + str(j),"")
                        m = hashlib.md5()
                        m.update(name.encode('utf-8'))
                        h = str(m.hexdigest())
                        url = "https://upload.wikimedia.org/wikipedia/commons/" + h[0] + "/" + h[0] + h[1] + "/" + name
                        print(url)
                        embedV = discord.Embed(title=res.get('results').get('bindings')[i].get('countryLabel').get('value'),color=0xebab34, url=url)
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
            message.channel.send("That didn't work! Try again fuck face!")
        await message.channel.send(embed = embedV)
    l = []
    if t[0:5] == ck+'bc':
        for i in range(len(borderingCountries.get('results').get('bindings'))):
            try:
                for j in range(len(borderingCountries.get('results').get('bindings')[i].get('instance_ofLabel'))):
                    if t[6:len(t)] == borderingCountries.get('results').get('bindings')[i].get('instance_ofLabel').get('value').lower():
                        embedBC = discord.Embed(title="Bordering Countries of " + borderingCountries.get('results').get('bindings')[i].get('instance_ofLabel').get('value'), color=0xebab34)
                        l.append(borderingCountries.get('results').get('bindings')[i].get('shares_border_withLabel').get('value'))
            except AttributeError:
                pass
        l = list(dict.fromkeys(l))
        for i in range(len(l)):
            embedBC.add_field(name = "Bordering Country " + str(i+1) + ": ",value=l[i],inline = False)
        await message.channel.send(embed = embedBC)
    if t[0:4] == '!bad':
        await message.channel.send("Fuck " + str(t[5:len(t)]))
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
# Bordering countries
# Major Religion