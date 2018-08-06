from riotwatcher import RiotWatcher
import discord
from discord.ext import commands
import time
import random
import math


def setup(bot):
    bot.add_cog(riot(bot))

class riot:
    '''This uses the Riot API, the key has to be refreshed every 24 hours for now.'''
    def __init__(self, bot):
        self.bot = bot
        self.servers = [460816759554048000, 460816847437037580, 460816987912798252, 460817157756813312,
                        460817260341100556, 475616108766953482, 475630608073228290]
        self.champdict = {
    "type": "champion",
    "version": "8.15.1",
    "data": {
        "MonkeyKing": {
            "title": "the Monkey King",
            "id": 62,
            "key": "MonkeyKing",
            "name": "Wukong"
        },
        "Jax": {
            "title": "Grandmaster at Arms",
            "id": 24,
            "key": "Jax",
            "name": "Jax"
        },
        "Fiddlesticks": {
            "title": "the Harbinger of Doom",
            "id": 9,
            "key": "Fiddlesticks",
            "name": "Fiddlesticks"
        },
        "Shaco": {
            "title": "the Demon Jester",
            "id": 35,
            "key": "Shaco",
            "name": "Shaco"
        },
        "Warwick": {
            "title": "the Uncaged Wrath of Zaun",
            "id": 19,
            "key": "Warwick",
            "name": "Warwick"
        },
        "Xayah": {
            "title": "the Rebel",
            "id": 498,
            "key": "Xayah",
            "name": "Xayah"
        },
        "Nidalee": {
            "title": "the Bestial Huntress",
            "id": 76,
            "key": "Nidalee",
            "name": "Nidalee"
        },
        "Zyra": {
            "title": "Rise of the Thorns",
            "id": 143,
            "key": "Zyra",
            "name": "Zyra"
        },
        "Kled": {
            "title": "the Cantankerous Cavalier",
            "id": 240,
            "key": "Kled",
            "name": "Kled"
        },
        "Brand": {
            "title": "the Burning Vengeance",
            "id": 63,
            "key": "Brand",
            "name": "Brand"
        },
        "Rammus": {
            "title": "the Armordillo",
            "id": 33,
            "key": "Rammus",
            "name": "Rammus"
        },
        "Illaoi": {
            "title": "the Kraken Priestess",
            "id": 420,
            "key": "Illaoi",
            "name": "Illaoi"
        },
        "Corki": {
            "title": "the Daring Bombardier",
            "id": 42,
            "key": "Corki",
            "name": "Corki"
        },
        "Braum": {
            "title": "the Heart of the Freljord",
            "id": 201,
            "key": "Braum",
            "name": "Braum"
        },
        "Darius": {
            "title": "the Hand of Noxus",
            "id": 122,
            "key": "Darius",
            "name": "Darius"
        },
        "Tryndamere": {
            "title": "the Barbarian King",
            "id": 23,
            "key": "Tryndamere",
            "name": "Tryndamere"
        },
        "MissFortune": {
            "title": "the Bounty Hunter",
            "id": 21,
            "key": "MissFortune",
            "name": "Miss Fortune"
        },
        "Yorick": {
            "title": "Shepherd of Souls",
            "id": 83,
            "key": "Yorick",
            "name": "Yorick"
        },
        "Xerath": {
            "title": "the Magus Ascendant",
            "id": 101,
            "key": "Xerath",
            "name": "Xerath"
        },
        "Sivir": {
            "title": "the Battle Mistress",
            "id": 15,
            "key": "Sivir",
            "name": "Sivir"
        },
        "Riven": {
            "title": "the Exile",
            "id": 92,
            "key": "Riven",
            "name": "Riven"
        },
        "Orianna": {
            "title": "the Lady of Clockwork",
            "id": 61,
            "key": "Orianna",
            "name": "Orianna"
        },
        "Gangplank": {
            "title": "the Saltwater Scourge",
            "id": 41,
            "key": "Gangplank",
            "name": "Gangplank"
        },
        "Malphite": {
            "title": "Shard of the Monolith",
            "id": 54,
            "key": "Malphite",
            "name": "Malphite"
        },
        "Poppy": {
            "title": "Keeper of the Hammer",
            "id": 78,
            "key": "Poppy",
            "name": "Poppy"
        },
        "Lissandra": {
            "title": "the Ice Witch",
            "id": 127,
            "key": "Lissandra",
            "name": "Lissandra"
        },
        "Jayce": {
            "title": "the Defender of Tomorrow",
            "id": 126,
            "key": "Jayce",
            "name": "Jayce"
        },
        "Nunu": {
            "title": "the Yeti Rider",
            "id": 20,
            "key": "Nunu",
            "name": "Nunu"
        },
        "Trundle": {
            "title": "the Troll King",
            "id": 48,
            "key": "Trundle",
            "name": "Trundle"
        },
        "Karthus": {
            "title": "the Deathsinger",
            "id": 30,
            "key": "Karthus",
            "name": "Karthus"
        },
        "Graves": {
            "title": "the Outlaw",
            "id": 104,
            "key": "Graves",
            "name": "Graves"
        },
        "Zoe": {
            "title": "the Aspect of Twilight",
            "id": 142,
            "key": "Zoe",
            "name": "Zoe"
        },
        "Gnar": {
            "title": "the Missing Link",
            "id": 150,
            "key": "Gnar",
            "name": "Gnar"
        },
        "Lux": {
            "title": "the Lady of Luminosity",
            "id": 99,
            "key": "Lux",
            "name": "Lux"
        },
        "Shyvana": {
            "title": "the Half-Dragon",
            "id": 102,
            "key": "Shyvana",
            "name": "Shyvana"
        },
        "Renekton": {
            "title": "the Butcher of the Sands",
            "id": 58,
            "key": "Renekton",
            "name": "Renekton"
        },
        "Fiora": {
            "title": "the Grand Duelist",
            "id": 114,
            "key": "Fiora",
            "name": "Fiora"
        },
        "Jinx": {
            "title": "the Loose Cannon",
            "id": 222,
            "key": "Jinx",
            "name": "Jinx"
        },
        "Kalista": {
            "title": "the Spear of Vengeance",
            "id": 429,
            "key": "Kalista",
            "name": "Kalista"
        },
        "Fizz": {
            "title": "the Tidal Trickster",
            "id": 105,
            "key": "Fizz",
            "name": "Fizz"
        },
        "Kassadin": {
            "title": "the Void Walker",
            "id": 38,
            "key": "Kassadin",
            "name": "Kassadin"
        },
        "Sona": {
            "title": "Maven of the Strings",
            "id": 37,
            "key": "Sona",
            "name": "Sona"
        },
        "Irelia": {
            "title": "the Blade Dancer",
            "id": 39,
            "key": "Irelia",
            "name": "Irelia"
        },
        "Viktor": {
            "title": "the Machine Herald",
            "id": 112,
            "key": "Viktor",
            "name": "Viktor"
        },
        "Rakan": {
            "title": "The Charmer",
            "id": 497,
            "key": "Rakan",
            "name": "Rakan"
        },
        "Kindred": {
            "title": "The Eternal Hunters",
            "id": 203,
            "key": "Kindred",
            "name": "Kindred"
        },
        "Cassiopeia": {
            "title": "the Serpent's Embrace",
            "id": 69,
            "key": "Cassiopeia",
            "name": "Cassiopeia"
        },
        "Maokai": {
            "title": "the Twisted Treant",
            "id": 57,
            "key": "Maokai",
            "name": "Maokai"
        },
        "Ornn": {
            "title": "The Fire below the Mountain",
            "id": 516,
            "key": "Ornn",
            "name": "Ornn"
        },
        "Thresh": {
            "title": "the Chain Warden",
            "id": 412,
            "key": "Thresh",
            "name": "Thresh"
        },
        "Kayle": {
            "title": "The Judicator",
            "id": 10,
            "key": "Kayle",
            "name": "Kayle"
        },
        "Hecarim": {
            "title": "the Shadow of War",
            "id": 120,
            "key": "Hecarim",
            "name": "Hecarim"
        },
        "Khazix": {
            "title": "the Voidreaver",
            "id": 121,
            "key": "Khazix",
            "name": "Kha'Zix"
        },
        "Olaf": {
            "title": "the Berserker",
            "id": 2,
            "key": "Olaf",
            "name": "Olaf"
        },
        "Ziggs": {
            "title": "the Hexplosives Expert",
            "id": 115,
            "key": "Ziggs",
            "name": "Ziggs"
        },
        "Syndra": {
            "title": "the Dark Sovereign",
            "id": 134,
            "key": "Syndra",
            "name": "Syndra"
        },
        "DrMundo": {
            "title": "the Madman of Zaun",
            "id": 36,
            "key": "DrMundo",
            "name": "Dr. Mundo"
        },
        "Karma": {
            "title": "the Enlightened One",
            "id": 43,
            "key": "Karma",
            "name": "Karma"
        },
        "Annie": {
            "title": "the Dark Child",
            "id": 1,
            "key": "Annie",
            "name": "Annie"
        },
        "Akali": {
            "title": "the Rogue Assassin",
            "id": 84,
            "key": "Akali",
            "name": "Akali"
        },
        "Volibear": {
            "title": "the Thunder's Roar",
            "id": 106,
            "key": "Volibear",
            "name": "Volibear"
        },
        "Yasuo": {
            "title": "the Unforgiven",
            "id": 157,
            "key": "Yasuo",
            "name": "Yasuo"
        },
        "Kennen": {
            "title": "the Heart of the Tempest",
            "id": 85,
            "key": "Kennen",
            "name": "Kennen"
        },
        "Rengar": {
            "title": "the Pridestalker",
            "id": 107,
            "key": "Rengar",
            "name": "Rengar"
        },
        "Ryze": {
            "title": "the Rune Mage",
            "id": 13,
            "key": "Ryze",
            "name": "Ryze"
        },
        "Shen": {
            "title": "the Eye of Twilight",
            "id": 98,
            "key": "Shen",
            "name": "Shen"
        },
        "Zac": {
            "title": "the Secret Weapon",
            "id": 154,
            "key": "Zac",
            "name": "Zac"
        },
        "Talon": {
            "title": "the Blade's Shadow",
            "id": 91,
            "key": "Talon",
            "name": "Talon"
        },
        "Swain": {
            "title": "the Noxian Grand General",
            "id": 50,
            "key": "Swain",
            "name": "Swain"
        },
        "Bard": {
            "title": "the Wandering Caretaker",
            "id": 432,
            "key": "Bard",
            "name": "Bard"
        },
        "Sion": {
            "title": "The Undead Juggernaut",
            "id": 14,
            "key": "Sion",
            "name": "Sion"
        },
        "Vayne": {
            "title": "the Night Hunter",
            "id": 67,
            "key": "Vayne",
            "name": "Vayne"
        },
        "Nasus": {
            "title": "the Curator of the Sands",
            "id": 75,
            "key": "Nasus",
            "name": "Nasus"
        },
        "Kayn": {
            "title": "the Shadow Reaper",
            "id": 141,
            "key": "Kayn",
            "name": "Kayn"
        },
        "TwistedFate": {
            "title": "the Card Master",
            "id": 4,
            "key": "TwistedFate",
            "name": "Twisted Fate"
        },
        "Chogath": {
            "title": "the Terror of the Void",
            "id": 31,
            "key": "Chogath",
            "name": "Cho'Gath"
        },
        "Udyr": {
            "title": "the Spirit Walker",
            "id": 77,
            "key": "Udyr",
            "name": "Udyr"
        },
        "Lucian": {
            "title": "the Purifier",
            "id": 236,
            "key": "Lucian",
            "name": "Lucian"
        },
        "Ivern": {
            "title": "the Green Father",
            "id": 427,
            "key": "Ivern",
            "name": "Ivern"
        },
        "Leona": {
            "title": "the Radiant Dawn",
            "id": 89,
            "key": "Leona",
            "name": "Leona"
        },
        "Caitlyn": {
            "title": "the Sheriff of Piltover",
            "id": 51,
            "key": "Caitlyn",
            "name": "Caitlyn"
        },
        "Sejuani": {
            "title": "Fury of the North",
            "id": 113,
            "key": "Sejuani",
            "name": "Sejuani"
        },
        "Nocturne": {
            "title": "the Eternal Nightmare",
            "id": 56,
            "key": "Nocturne",
            "name": "Nocturne"
        },
        "Zilean": {
            "title": "the Chronokeeper",
            "id": 26,
            "key": "Zilean",
            "name": "Zilean"
        },
        "Azir": {
            "title": "the Emperor of the Sands",
            "id": 268,
            "key": "Azir",
            "name": "Azir"
        },
        "Rumble": {
            "title": "the Mechanized Menace",
            "id": 68,
            "key": "Rumble",
            "name": "Rumble"
        },
        "Morgana": {
            "title": "Fallen Angel",
            "id": 25,
            "key": "Morgana",
            "name": "Morgana"
        },
        "Taliyah": {
            "title": "the Stoneweaver",
            "id": 163,
            "key": "Taliyah",
            "name": "Taliyah"
        },
        "Teemo": {
            "title": "the Swift Scout",
            "id": 17,
            "key": "Teemo",
            "name": "Teemo"
        },
        "Urgot": {
            "title": "the Dreadnought",
            "id": 6,
            "key": "Urgot",
            "name": "Urgot"
        },
        "Amumu": {
            "title": "the Sad Mummy",
            "id": 32,
            "key": "Amumu",
            "name": "Amumu"
        },
        "Galio": {
            "title": "the Colossus",
            "id": 3,
            "key": "Galio",
            "name": "Galio"
        },
        "Heimerdinger": {
            "title": "the Revered Inventor",
            "id": 74,
            "key": "Heimerdinger",
            "name": "Heimerdinger"
        },
        "Anivia": {
            "title": "the Cryophoenix",
            "id": 34,
            "key": "Anivia",
            "name": "Anivia"
        },
        "Ashe": {
            "title": "the Frost Archer",
            "id": 22,
            "key": "Ashe",
            "name": "Ashe"
        },
        "Velkoz": {
            "title": "the Eye of the Void",
            "id": 161,
            "key": "Velkoz",
            "name": "Vel'Koz"
        },
        "Singed": {
            "title": "the Mad Chemist",
            "id": 27,
            "key": "Singed",
            "name": "Singed"
        },
        "Skarner": {
            "title": "the Crystal Vanguard",
            "id": 72,
            "key": "Skarner",
            "name": "Skarner"
        },
        "Varus": {
            "title": "the Arrow of Retribution",
            "id": 110,
            "key": "Varus",
            "name": "Varus"
        },
        "Twitch": {
            "title": "the Plague Rat",
            "id": 29,
            "key": "Twitch",
            "name": "Twitch"
        },
        "Garen": {
            "title": "The Might of Demacia",
            "id": 86,
            "key": "Garen",
            "name": "Garen"
        },
        "Blitzcrank": {
            "title": "the Great Steam Golem",
            "id": 53,
            "key": "Blitzcrank",
            "name": "Blitzcrank"
        },
        "MasterYi": {
            "title": "the Wuju Bladesman",
            "id": 11,
            "key": "MasterYi",
            "name": "Master Yi"
        },
        "Pyke": {
            "title": "the Bloodharbor Ripper",
            "id": 555,
            "key": "Pyke",
            "name": "Pyke"
        },
        "Elise": {
            "title": "the Spider Queen",
            "id": 60,
            "key": "Elise",
            "name": "Elise"
        },
        "Alistar": {
            "title": "the Minotaur",
            "id": 12,
            "key": "Alistar",
            "name": "Alistar"
        },
        "Katarina": {
            "title": "the Sinister Blade",
            "id": 55,
            "key": "Katarina",
            "name": "Katarina"
        },
        "Ekko": {
            "title": "the Boy Who Shattered Time",
            "id": 245,
            "key": "Ekko",
            "name": "Ekko"
        },
        "Mordekaiser": {
            "title": "the Iron Revenant",
            "id": 82,
            "key": "Mordekaiser",
            "name": "Mordekaiser"
        },
        "Lulu": {
            "title": "the Fae Sorceress",
            "id": 117,
            "key": "Lulu",
            "name": "Lulu"
        },
        "Camille": {
            "title": "the Steel Shadow",
            "id": 164,
            "key": "Camille",
            "name": "Camille"
        },
        "Aatrox": {
            "title": "the Darkin Blade",
            "id": 266,
            "key": "Aatrox",
            "name": "Aatrox"
        },
        "Draven": {
            "title": "the Glorious Executioner",
            "id": 119,
            "key": "Draven",
            "name": "Draven"
        },
        "TahmKench": {
            "title": "the River King",
            "id": 223,
            "key": "TahmKench",
            "name": "Tahm Kench"
        },
        "Pantheon": {
            "title": "the Artisan of War",
            "id": 80,
            "key": "Pantheon",
            "name": "Pantheon"
        },
        "XinZhao": {
            "title": "the Seneschal of Demacia",
            "id": 5,
            "key": "XinZhao",
            "name": "Xin Zhao"
        },
        "AurelionSol": {
            "title": "The Star Forger",
            "id": 136,
            "key": "AurelionSol",
            "name": "Aurelion Sol"
        },
        "LeeSin": {
            "title": "the Blind Monk",
            "id": 64,
            "key": "LeeSin",
            "name": "Lee Sin"
        },
        "Taric": {
            "title": "the Shield of Valoran",
            "id": 44,
            "key": "Taric",
            "name": "Taric"
        },
        "Malzahar": {
            "title": "the Prophet of the Void",
            "id": 90,
            "key": "Malzahar",
            "name": "Malzahar"
        },
        "Kaisa": {
            "title": "Daughter of the Void",
            "id": 145,
            "key": "Kaisa",
            "name": "Kai'Sa"
        },
        "Diana": {
            "title": "Scorn of the Moon",
            "id": 131,
            "key": "Diana",
            "name": "Diana"
        },
        "Tristana": {
            "title": "the Yordle Gunner",
            "id": 18,
            "key": "Tristana",
            "name": "Tristana"
        },
        "RekSai": {
            "title": "the Void Burrower",
            "id": 421,
            "key": "RekSai",
            "name": "Rek'Sai"
        },
        "Vladimir": {
            "title": "the Crimson Reaper",
            "id": 8,
            "key": "Vladimir",
            "name": "Vladimir"
        },
        "JarvanIV": {
            "title": "the Exemplar of Demacia",
            "id": 59,
            "key": "JarvanIV",
            "name": "Jarvan IV"
        },
        "Nami": {
            "title": "the Tidecaller",
            "id": 267,
            "key": "Nami",
            "name": "Nami"
        },
        "Jhin": {
            "title": "the Virtuoso",
            "id": 202,
            "key": "Jhin",
            "name": "Jhin"
        },
        "Soraka": {
            "title": "the Starchild",
            "id": 16,
            "key": "Soraka",
            "name": "Soraka"
        },
        "Veigar": {
            "title": "the Tiny Master of Evil",
            "id": 45,
            "key": "Veigar",
            "name": "Veigar"
        },
        "Janna": {
            "title": "the Storm's Fury",
            "id": 40,
            "key": "Janna",
            "name": "Janna"
        },
        "Nautilus": {
            "title": "the Titan of the Depths",
            "id": 111,
            "key": "Nautilus",
            "name": "Nautilus"
        },
        "Evelynn": {
            "title": "Agony's Embrace",
            "id": 28,
            "key": "Evelynn",
            "name": "Evelynn"
        },
        "Gragas": {
            "title": "the Rabble Rouser",
            "id": 79,
            "key": "Gragas",
            "name": "Gragas"
        },
        "Zed": {
            "title": "the Master of Shadows",
            "id": 238,
            "key": "Zed",
            "name": "Zed"
        },
        "Vi": {
            "title": "the Piltover Enforcer",
            "id": 254,
            "key": "Vi",
            "name": "Vi"
        },
        "KogMaw": {
            "title": "the Mouth of the Abyss",
            "id": 96,
            "key": "KogMaw",
            "name": "Kog'Maw"
        },
        "Ahri": {
            "title": "the Nine-Tailed Fox",
            "id": 103,
            "key": "Ahri",
            "name": "Ahri"
        },
        "Quinn": {
            "title": "Demacia's Wings",
            "id": 133,
            "key": "Quinn",
            "name": "Quinn"
        },
        "Leblanc": {
            "title": "the Deceiver",
            "id": 7,
            "key": "Leblanc",
            "name": "LeBlanc"
        },
        "Ezreal": {
            "title": "the Prodigal Explorer",
            "id": 81,
            "key": "Ezreal",
            "name": "Ezreal"
        }
    }
}
        self.ssdict = {
    "type": "summoner",
    "version": "8.15.1",
    "data": {
        "SummonerSiegeChampSelect2": {
            "id": 34,
            "summonerLevel": 1,
            "name": "Nexus Siege: Siege Weapon Slot",
            "key": "SummonerSiegeChampSelect2",
            "description": "In Nexus Siege, Summoner Spells are replaced with Siege Weapon Slots. Spend Crystal Shards to buy single-use Siege Weapons from the item shop, then use your Summoner Spell keys to activate them!"
        },
        "SummonerTeleport": {
            "id": 12,
            "summonerLevel": 7,
            "name": "Teleport",
            "key": "SummonerTeleport",
            "description": "After channeling for 4.5 seconds, teleports your champion to target allied structure, minion, or ward."
        },
        "SummonerSiegeChampSelect1": {
            "id": 33,
            "summonerLevel": 1,
            "name": "Nexus Siege: Siege Weapon Slot",
            "key": "SummonerSiegeChampSelect1",
            "description": "In Nexus Siege, Summoner Spells are replaced with Siege Weapon Slots. Spend Crystal Shards to buy single-use Siege Weapons from the item shop, then use your Summoner Spell keys to activate them!"
        },
        "SummonerExhaust": {
            "id": 3,
            "summonerLevel": 4,
            "name": "Exhaust",
            "key": "SummonerExhaust",
            "description": "Exhausts target enemy champion, reducing their Movement Speed by 30%, and their damage dealt by 40% for 2.5 seconds."
        },
        "SummonerBarrier": {
            "id": 21,
            "summonerLevel": 4,
            "name": "Barrier",
            "key": "SummonerBarrier",
            "description": "Shields your champion from 115-455 damage (depending on champion level) for 2 seconds."
        },
        "SummonerMana": {
            "id": 13,
            "summonerLevel": 6,
            "name": "Clarity",
            "key": "SummonerMana",
            "description": "Restores 50% of your champion's maximum Mana. Also restores allies for 25% of their maximum Mana."
        },
        "SummonerSnowURFSnowball_Mark": {
            "id": 39,
            "summonerLevel": 6,
            "name": "Ultra (Rapidly Flung) Mark",
            "key": "SummonerSnowURFSnowball_Mark",
            "description": "It's a snowball! It's a Poro! It's...uh...one of those."
        },
        "SummonerFlash": {
            "id": 4,
            "summonerLevel": 7,
            "name": "Flash",
            "key": "SummonerFlash",
            "description": "Teleports your champion a short distance toward your cursor's location."
        },
        "SummonerSnowball": {
            "id": 32,
            "summonerLevel": 6,
            "name": "Mark",
            "key": "SummonerSnowball",
            "description": "Throw a snowball in a straight line at your enemies. If it hits an enemy, they become marked, granting True Sight, and your champion can quickly travel to the marked target as a follow up."
        },
        "SummonerDot": {
            "id": 14,
            "summonerLevel": 9,
            "name": "Ignite",
            "key": "SummonerDot",
            "description": "Ignites target enemy champion, dealing 80-505 true damage (depending on champion level) over 5 seconds, grants you vision of the target, and reduces healing effects on them for the duration."
        },
        "SummonerDarkStarChampSelect2": {
            "id": 36,
            "summonerLevel": 1,
            "name": "Disabled Summoner Spells",
            "key": "SummonerDarkStarChampSelect2",
            "description": "Summoner spells are disabled in this mode."
        },
        "SummonerDarkStarChampSelect1": {
            "id": 35,
            "summonerLevel": 1,
            "name": "Disabled Summoner Spells",
            "key": "SummonerDarkStarChampSelect1",
            "description": "Summoner spells are disabled in this mode."
        },
        "SummonerPoroRecall": {
            "id": 30,
            "summonerLevel": 1,
            "name": "To the King!",
            "key": "SummonerPoroRecall",
            "description": "Quickly travel to the Poro King's side."
        },
        "SummonerHaste": {
            "id": 6,
            "summonerLevel": 1,
            "name": "Ghost",
            "key": "SummonerHaste",
            "description": "Your champion gains increased Movement Speed and can move through units for 10 seconds. Grants a maximum of 28-45% (depending on champion level) Movement Speed after accelerating for 2 seconds."
        },
        "SummonerHeal": {
            "id": 7,
            "summonerLevel": 1,
            "name": "Heal",
            "key": "SummonerHeal",
            "description": "Restores 90-345 Health (depending on champion level) and grants 30% Movement Speed for 1 second to you and target allied champion. This healing is halved for units recently affected by Summoner Heal."
        },
        "SummonerPoroThrow": {
            "id": 31,
            "summonerLevel": 1,
            "name": "Poro Toss",
            "key": "SummonerPoroThrow",
            "description": "Toss a Poro at your enemies. If it hits, you can quickly travel to your target as a follow up."
        },
        "SummonerBoost": {
            "id": 1,
            "summonerLevel": 9,
            "name": "Cleanse",
            "key": "SummonerBoost",
            "description": "Removes all disables (excluding suppression and airborne) and summoner spell debuffs affecting your champion and lowers the duration of incoming disables by 65% for 3 seconds."
        },
        "SummonerSmite": {
            "id": 11,
            "summonerLevel": 9,
            "name": "Smite",
            "key": "SummonerSmite",
            "description": "Deals 390-1000 true damage (depending on champion level) to target epic, large, or medium monster or enemy minion. Restores Health based on your maximum life when used against monsters."
        }
    }
}

    def get_emote_strings(self, name: str):
        for guild_id in self.servers:
            server = self.bot.get_guild(guild_id)
            for emote in server.emojis:
                if emote.name.lower() == name.lower():
                    return str(emote)

    def get_champ_from_id(self, id: int):
        for _ in self.champdict["data"].values():
            if _["id"] == id:
                return _["key"]

    def get_ss_from_id(self, id: int):
        for _ in self.ssdict["data"].values():
            if _["id"] == id:
                return _["name"]

    @commands.command(aliases=["bl"])
    async def profile(self, ctx, region: str, *, name: str):
        try:
            embed = discord.Embed(title=f"Basic lookup for {name.capitalize()}", color=0xA90000)
            DAO = LeagueLookup(name, region)
            DAO.get_summoner_info()
            embed.set_thumbnail(url=DAO.icon_url)
            embed.add_field(name="Summoner name", value=DAO.name)
            embed.add_field(name="SoloQ rank", value=DAO.rank)
            embed.add_field(name="SoloQ winrate", value=DAO.winrate)
            embed.add_field(name="Mastery", value=DAO.mastery)
            embed.add_field(name="Summoner ID", value=DAO.summoner_id)
            embed.add_field(name="Summoner level", value=DAO.summoner_level)
            embed.add_field(name="Account ID", value=DAO.account_id)
            embed.add_field(name="Profile icon ID", value=DAO.profile_icon_id)
            embed.add_field(name="Region", value=DAO.region)
            await ctx.send(embed=embed)
        except:
            await ctx.send("Ratelimit exceeded, try again in about 10 minutes. To prevent this from happening, don't spam the command.")

    @commands.command()
    async def game(self, ctx, region: str, *, name: str):
        embed = discord.Embed(color=0xA90000)
        try:
            DAO = LeagueLookup(name, region)
            DAO.get_summoner_info()
            team1 = "__**Blue team**__:\n"
            team2 = "__**Red team**__:\n"
            ssteam1 = "\u200b\n"
            ssteam2 = "\u200b\n"
            rankteam1 = "\u200b\n"
            rankteam2 = "\u200b\n"
            for x in DAO.gameparticipantslist:
                DAO2 = LeagueLookup(x[1], region)
                DAO2.get_rank()
                champ_name = self.get_champ_from_id(x[0])
                ss1_name = self.get_ss_from_id(x[2])
                ss2_name = self.get_ss_from_id(x[3])
                champ_emote = self.get_emote_strings(champ_name)
                ss1_emote = self.get_emote_strings(ss1_name)
                ss2_emote = self.get_emote_strings(ss2_name)
                if x[4] == 100:
                    team1 += "{}{:20}\n".format(champ_emote, x[1])
                    ssteam1 += "\t{}{}\n".format(ss1_emote, ss2_emote)
                    rankteam1 += f"{DAO2.rank}\n"
                else:
                    team2 += f"{champ_emote} {x[1]}\n"
                    ssteam2 += "\t{}{}\n".format(ss1_emote, ss2_emote)
                    rankteam2 += f"{DAO2.rank}\n"
            teams = team1 + team2
            ssteams = ssteam1 + ssteam2
            rankteams = rankteam1 + rankteam2
            embed.add_field(name="Teams", value=teams)
            embed.add_field(name="Ranks", value=rankteams)
            embed.add_field(name="Summoners", value=ssteams)
            await ctx.send(embed=embed)


        except Exception as e:
            await ctx.send(f"{e}\n"
                           f"This player is either not in game or some other error occurred")

class LeagueLookup:
    def __init__(self, name: str, region: str):
        self.name = name
        self.rank = None
        self.winrate = None
        self.mastery = None
        self.summoner_id = None
        self.account_id = None
        self.profile_icon_id = None
        self.icon_url = None
        self.summoner_level = None
        self.rankemotes = {"CHALLENGER": "<:challenger:475632110984757249>", "MASTER": "<:master:475632110917386241>",
                           "DIAMOND": "<:diamond:475632111408250880>", "PLATINUM": "<:platinum:475632111307718656>",
                           "GOLD": "<:gold:475632110955397140>", "SILVER": "<:silver:475632111273902090>",
                           "BRONZE": "<:bronze:475632110645018635>", "NONE": "<:None:475722325602336768>"}
        self.gameparticipantslist = None
        if region.lower() == "kr" or region.lower() == "ru":
            self.region = region
        else:
            self.region = region + "1"
        self.riotwatcher = RiotWatcher("RGAPI-343dae2c-e864-4795-962e-ed0691a3fcfc")

    def get_summoner_info(self):
        # Load in the basic information about a summoner
        x = self.riotwatcher.summoner.by_name(self.region, self.name)
        self.summoner_id = x["id"]
        self.account_id = x["accountId"]
        self.profile_icon_id = x["profileIconId"]
        self.summoner_level = x["summonerLevel"]
        self.icon_url = f"https://opgg-static.akamaized.net/images/profile_icons/profileIcon{self.profile_icon_id}.jpg"
        y = self.riotwatcher.league.positions_by_summoner(self.region, self.summoner_id)
        if not bool(y):
            self.rank = "<:None:475722325602336768> Unranked"
            self.winrate = "No soloQ ranked games"
        for _ in y:
            if _["queueType"] == "RANKED_SOLO_5x5":
                self.rank = f"{self.rankemotes[_['tier']]} {_['tier'].capitalize()}  {_['rank']} "
                self.winrate = str(_["wins"]) + "W/" + str(_["losses"]) + "L: " + str(math.ceil(_["wins"]/(_["wins"]+_["losses"])*100)) + "% WR"
                break


        all_strings = []
        x = self.riotwatcher.spectator.by_summoner(self.region, self.summoner_id)
        for y in x["participants"]:
            new_list = []
            new_list.append(y["championId"])
            new_list.append(y["summonerName"])
            new_list.append(y["spell1Id"])
            new_list.append(y["spell2Id"])
            new_list.append(y["teamId"])
            all_strings.append(new_list)
        self.gameparticipantslist = all_strings

    def get_rank(self):
        x = self.riotwatcher.summoner.by_name(self.region, self.name)
        self.summoner_id = x["id"]
        y = self.riotwatcher.league.positions_by_summoner(self.region, self.summoner_id)
        if not bool(y):
            self.rank = "<:None:475722325602336768> Unranked"
            self.winrate = "No soloQ ranked games"
        for _ in y:
            if _["queueType"] == "RANKED_SOLO_5x5":
                self.rank = f"{self.rankemotes[_['tier']]} {_['tier'].capitalize()}  {_['rank']} " \
                            f"**{_['wins']}W/{_['losses']}L**"
                # f"**{str(math.ceil(_['wins']/(_['wins']+_['losses'])*100))}% WR**"

    def get_champ_from_id(self, id: int):
        x = self.riotwatcher.static_data.champion(self.region, id)
        return x["name"]

    def get_ss_from_id(self, id: int):
        x = self.riotwatcher.static_data.summoner_spell(self.region, id)
        return x["name"]





### Form of spectator return
# {
#     "gameId": 3724169986,
#     "gameStartTime": 1533478689431,
#     "platformId": "EUW1",
#     "gameMode": "CLASSIC",
#     "mapId": 11,
#     "gameType": "MATCHED_GAME",
#     "gameQueueConfigId": 420,
#     "observers": {
#         "encryptionKey": "zGn4Z8nXB6d3SufKrI5KnjzUieWEiFzH"
#     },
#     "participants": [
#         {
#             "profileIconId": 3398,
#             "championId": 28,
#             "summonerName": "Bärgarn",
#             "gameCustomizationObjects": [],
#             "bot": false,
#             "perks": {
#                 "perkStyle": 8100,
#                 "perkIds": [
#                     8112,
#                     8143,
#                     8138,
#                     8105,
#                     8236,
#                     8234
#                 ],
#                 "perkSubStyle": 8200
#             },
#             "spell2Id": 11,
#             "teamId": 100,
#             "spell1Id": 4,
#             "summonerId": 21466270
#         },
#         {
#             "profileIconId": 3369,
#             "championId": 99,
#             "summonerName": "Ukaly",
#             "gameCustomizationObjects": [],
#             "bot": false,
#             "perks": {
#                 "perkStyle": 8200,
#                 "perkIds": [
#                     8214,
#                     8226,
#                     8234,
#                     8236,
#                     8126,
#                     8135
#                 ],
#                 "perkSubStyle": 8100
#             },
#             "spell2Id": 14,
#             "teamId": 100,
#             "spell1Id": 4,
#             "summonerId": 23598870
#         },
#         {
#             "profileIconId": 3379,
#             "championId": 62,
#             "summonerName": "Hesselbjerg",
#             "gameCustomizationObjects": [],
#             "bot": false,
#             "perks": {
#                 "perkStyle": 8100,
#                 "perkIds": [
#                     8112,
#                     8143,
#                     8138,
#                     8106,
#                     8473,
#                     8472
#                 ],
#                 "perkSubStyle": 8400
#             },
#             "spell2Id": 4,
#             "teamId": 100,
#             "spell1Id": 12,
#             "summonerId": 61992932
#         },
#         {
#             "profileIconId": 654,
#             "championId": 136,
#             "summonerName": "MIKE0015",
#             "gameCustomizationObjects": [],
#             "bot": false,
#             "perks": {
#                 "perkStyle": 8200,
#                 "perkIds": [
#                     8230,
#                     8224,
#                     8234,
#                     8232,
#                     8316,
#                     8352
#                 ],
#                 "perkSubStyle": 8300
#             },
#             "spell2Id": 4,
#             "teamId": 100,
#             "spell1Id": 14,
#             "summonerId": 53708534
#         },
#         {
#             "profileIconId": 2076,
#             "championId": 222,
#             "summonerName": "Eli055",
#             "gameCustomizationObjects": [],
#             "bot": false,
#             "perks": {
#                 "perkStyle": 8000,
#                 "perkIds": [
#                     8008,
#                     9101,
#                     9103,
#                     8014,
#                     8234,
#                     8236
#                 ],
#                 "perkSubStyle": 8200
#             },
#             "spell2Id": 4,
#             "teamId": 100,
#             "spell1Id": 7,
#             "summonerId": 41617194
#         },
#         {
#             "profileIconId": 1448,
#             "championId": 202,
#             "summonerName": "Lyf",
#             "gameCustomizationObjects": [],
#             "bot": false,
#             "perks": {
#                 "perkStyle": 8100,
#                 "perkIds": [
#                     9923,
#                     8139,
#                     8138,
#                     8135,
#                     8234,
#                     8236
#                 ],
#                 "perkSubStyle": 8200
#             },
#             "spell2Id": 4,
#             "teamId": 200,
#             "spell1Id": 7,
#             "summonerId": 33797436
#         },
#         {
#             "profileIconId": 1391,
#             "championId": 80,
#             "summonerName": "Steckrübe",
#             "gameCustomizationObjects": [],
#             "bot": false,
#             "perks": {
#                 "perkStyle": 8100,
#                 "perkIds": [
#                     8112,
#                     8139,
#                     8138,
#                     8106,
#                     9111,
#                     8014
#                 ],
#                 "perkSubStyle": 8000
#             },
#             "spell2Id": 14,
#             "teamId": 200,
#             "spell1Id": 4,
#             "summonerId": 24772114
#         },
#         {
#             "profileIconId": 19,
#             "championId": 104,
#             "summonerName": "Succubiitch",
#             "gameCustomizationObjects": [],
#             "bot": false,
#             "perks": {
#                 "perkStyle": 8000,
#                 "perkIds": [
#                     8021,
#                     9111,
#                     9104,
#                     8014,
#                     8234,
#                     8232
#                 ],
#                 "perkSubStyle": 8200
#             },
#             "spell2Id": 11,
#             "teamId": 200,
#             "spell1Id": 4,
#             "summonerId": 105641935
#         },
#         {
#             "profileIconId": 508,
#             "championId": 150,
#             "summonerName": "Karisas",
#             "gameCustomizationObjects": [],
#             "bot": false,
#             "perks": {
#                 "perkStyle": 8200,
#                 "perkIds": [
#                     8214,
#                     8224,
#                     8234,
#                     8236,
#                     8473,
#                     8472
#                 ],
#                 "perkSubStyle": 8400
#             },
#             "spell2Id": 12,
#             "teamId": 200,
#             "spell1Id": 4,
#             "summonerId": 26151048
#         },
#         {
#             "profileIconId": 1387,
#             "championId": 143,
#             "summonerName": "KOALAFUEHR3R",
#             "gameCustomizationObjects": [],
#             "bot": false,
#             "perks": {
#                 "perkStyle": 8200,
#                 "perkIds": [
#                     8229,
#                     8226,
#                     8210,
#                     8237,
#                     8313,
#                     8347
#                 ],
#                 "perkSubStyle": 8300
#             },
#             "spell2Id": 4,
#             "teamId": 200,
#             "spell1Id": 14,
#             "summonerId": 53556971
#         }
#     ],
#     "gameLength": 679,
#     "bannedChampions": [
#         {
#             "teamId": 100,
#             "championId": 64,
#             "pickTurn": 1
#         },
#         {
#             "teamId": 100,
#             "championId": 145,
#             "pickTurn": 2
#         },
#         {
#             "teamId": 100,
#             "championId": 84,
#             "pickTurn": 3
#         },
#         {
#             "teamId": 100,
#             "championId": 157,
#             "pickTurn": 4
#         },
#         {
#             "teamId": 100,
#             "championId": 119,
#             "pickTurn": 5
#         },
#         {
#             "teamId": 200,
#             "championId": 266,
#             "pickTurn": 6
#         },
#         {
#             "teamId": 200,
#             "championId": 555,
#             "pickTurn": 7
#         },
#         {
#             "teamId": 200,
#             "championId": 11,
#             "pickTurn": 8
#         },
#         {
#             "teamId": 200,
#             "championId": 119,
#             "pickTurn": 9
#         },
#         {
#             "teamId": 200,
#             "championId": 238,
#             "pickTurn": 10
#         }
#     ]
# }

