import discord
import random

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
deck = [f'{rank} of {suit}' for suit in suits for rank in ranks]

def shuffle_deck():
    random.shuffle(deck)

def deal_hands(num_players):
    return [[deck.pop(), deck.pop()] for _ in range(num_players)]

def deal_card():
    return deck.pop() if deck else None

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

# Game State Variables
checkInPhase = False
gameStart = False
phaseOne = False
phaseTwo = False
phaseThree = False
pokerUsers = []
pokerHands = []
communityCards = []
currentBets = {}

@client.event
async def on_message(message):
    global checkInPhase, gameStart, phaseOne, phaseTwo, phaseThree
    global pokerUsers, pokerHands, communityCards, currentBets
    
    if message.author == client.user:
        return

    if message.content.startswith('$poker'):
        checkInPhase = True
        await message.channel.send('All players send $checkin to be dealt in')
    
    if message.content.startswith('$checkin') and checkInPhase:
        if message.author.id not in pokerUsers:
            pokerUsers.append(message.author.id)
            await message.channel.send(f'{message.author.name} checked in.')
    
    if message.content.startswith('$play') and checkInPhase:
        gameStart = True
        shuffle_deck()
        await message.channel.send('Game started! Commands: $deal, $check, $raise <amount>, $fold')
    
    if gameStart:
        if message.content.startswith('$deal') and not phaseOne:
            pokerHands = deal_hands(len(pokerUsers))
            for i, user_id in enumerate(pokerUsers):
                user = await client.fetch_user(user_id)
                await user.send(f'Your hand: {", ".join(pokerHands[i])}')
            
            communityCards.clear()
            communityCards.extend([deal_card() for _ in range(3)])
            await message.channel.send(f'Flop: {", ".join(communityCards)}')

            phaseOne = True
            currentBets = {user: 0 for user in pokerUsers}
        
        elif message.content.startswith('$check') and phaseOne:
            await message.channel.send(f'{message.author.name} checks.')
        
        elif message.content.startswith('$raise') and phaseOne:
            try:
                amount = int(message.content.split()[1])
                currentBets[message.author.id] += amount
                await message.channel.send(f'{message.author.name} raises by {amount}.')
            except:
                await message.channel.send('Invalid raise format. Use $raise <amount>')
        
        elif message.content.startswith('$fold') and phaseOne:
            pokerUsers.remove(message.author.id)
            await message.channel.send(f'{message.author.name} folds.')
        
        elif message.content.startswith('$turn') and phaseOne and not phaseTwo:
            communityCards.append(deal_card())
            await message.channel.send(f'Flop: {", ".join(communityCards)}')
            phaseTwo = True
        
        elif message.content.startswith('$river') and phaseTwo and not phaseThree:
            communityCards.append(deal_card())
            await message.channel.send(f'Flop: {", ".join(communityCards)}')
            phaseThree = True
        
        elif message.content.startswith('$showdown') and phaseThree:
            await message.channel.send('Showdown time! Evaluating hands...')
            await message.channel.send('Winner determination is not implemented yet!')
