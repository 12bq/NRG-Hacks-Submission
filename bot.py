import discord
import random

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
deck = [f'{rank} of {suit}' for suit in suits for rank in ranks]

def deal_hands(num_players):
    random.shuffle(deck)
    hands = []
    for i in range(num_players):
        hand = [deck.pop() for _ in range(2)]
        hands.append(hand)
    return hands

def deal_river():
    random.shuffle(deck)
    river = []
    for i in range(3):
        print(i)
        river.append(deck.pop())
    print(river)
    return river

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

checkInPhase = False
gameStart = False
phaseOne = False
phaseTwo = False
pokerUsers = []
pokerHands = []
theRiver = []

@client.event
async def on_message(message):
    global checkInPhase
    global phaseOne
    global phaseTwo
    global gameStart
    global pokerUsers
    global pokerHands
    global theRiver

    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')


    if message.content.startswith('$poker'):
        checkInPhase = True
        await message.channel.send('All players send $checkin to be dealt in')

    if message.content.startswith('$checkin'):
        if checkInPhase:
            await message.channel.send(f'{message.author.name} checked in.')
            print(message.author.id)
            pokerUsers.append(message.author.id)
            print(pokerUsers)
        else:
            await message.channel.send('Game didnt start yet dumbass')

    if message.content.startswith('$play'):
        if checkInPhase:
            gameStart = True
            await message.channel.send('Game started!\nCommands: $deal, $check, $raise')
            print(pokerHands)
        else:
            await message.channel.send('Game didnt start yet dumbass')

    if(gameStart):
        if message.content.startswith('$deal'):
            pokerHands = deal_hands(len(pokerUsers))
            print(pokerHands)
            playerCounter = 0
            for user_id in pokerUsers:
                print(user_id)
                user = await client.fetch_user(user_id)
                await user.send(pokerHands[playerCounter])
                playerCounter = playerCounter + 1

            print(len(deck))
            theRiver = deal_river()
            print(theRiver)
            print(len(deck))

            await message.channel.send(theRiver)
            phaseOne = True
        else:
            print('Enter $play to start game')