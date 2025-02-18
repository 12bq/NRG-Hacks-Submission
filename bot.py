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

checkInPhase = False
gameStart = False
phaseOne = False
phaseTwo = False
phaseThree = False
pokerUsers = []
pokerHands = []
communityCards = []
currentBets = {}
playerActions = {}

@client.event
async def on_message(message):
    global checkInPhase, gameStart, phaseOne, phaseTwo, phaseThree
    global pokerUsers, pokerHands, communityCards, currentBets
    
    if message.author == client.user:
        return

    if message.content.startswith('$poker'):
        checkInPhase = True
        await message.channel.send('All players send $register to be dealt in')
    
    if message.content.startswith('$register') and checkInPhase:
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

            embed = discord.Embed(
                title="Flop Dealt!",
                description=f"Community Cards: {', '.join(communityCards)}",
                color=discord.Color.green()
            )
            embed.set_footer(text="Next: Use $turn to reveal the turn card")

            await message.channel.send(embed=embed)
            phaseOne = True
            currentBets = {user: 0 for user in pokerUsers}
            await display_game_status(message.channel)
            
            communityCards.clear()
            communityCards.extend([deal_card() for _ in range(3)])

            phaseOne = True
            currentBets = {user: 0 for user in pokerUsers}
        
        elif message.content.startswith('$check') and phaseOne:
            playerActions[message.author.id] = "Checked"
            await message.channel.send(f'{message.author.name} checks.')
            await display_game_status(message.channel)
        
        elif message.content.startswith('$raise') and phaseOne:
            try:
                amount = int(message.content.split()[1])
                currentBets[message.author.id] += amount
                playerActions[message.author.id] = f"Raised ${amount}"
                await message.channel.send(f'{message.author.name} raises by ${amount}.')
                await display_game_status(message.channel)
            except:
                await message.channel.send('Invalid raise format. Use $raise <amount>')
        
        elif message.content.startswith('$fold') and phaseOne:
            pokerUsers.remove(message.author.id)
            playerActions[message.author.id] = "Folded"
            await message.channel.send(f'{message.author.name} folds.')
            await display_game_status(message.channel)
        
        elif message.content.startswith('$turn') and phaseOne and not phaseTwo:
            theTurn = deal_card()
            communityCards.append(theTurn)
            
            embed = discord.Embed(
                title="Turn Card Dealt!",
                description=f"Community Cards: {', '.join(communityCards)}",
                color=discord.Color.orange()
            )
            embed.set_footer(text="Next: Use $river to reveal the final card")

            await message.channel.send(embed=embed)
            phaseTwo = True
            await display_game_status(message.channel)  # Show updated game status
        
        elif message.content.startswith('$river') and phaseTwo and not phaseThree:
            theFinalRiver = deal_card()
            communityCards.append(theFinalRiver)  # Add river to community cards

            embed = discord.Embed(
                title="Final River Card Dealt!",
                description=f"Community Cards: {', '.join(communityCards)}",
                color=discord.Color.red()
            )
            embed.set_footer(text="Next: Use $showdown to reveal player hands")

            await message.channel.send(embed=embed)
            phaseThree = True
            await display_game_status(message.channel)
        
        elif message.content.startswith('$showdown') and phaseThree:
            await message.channel.send('Showdown time! Evaluating hands...')
            await message.channel.send('Winner determination is not implemented yet!')

            checkInPhase = False
            gameStart = False
            phaseOne = False
            phaseTwo = False
            phaseThree = False
            pokerUsers.clear()
            pokerHands.clear()
            communityCards.clear()
            currentBets.clear()
            playerActions.clear()

            shuffle_deck()

            await message.channel.send('Game has ended! Type `$poker` to start a new game.')

async def display_game_status(channel):
    embed = discord.Embed(
        title="Poker Game Status",
        color=discord.Color.blue()
    )

    if not pokerUsers:
        embed.description = "No players remaining."
    else:
        for user_id in pokerUsers:
            user = await client.fetch_user(user_id)
            action = playerActions.get(user_id, "No action")
            bet = currentBets.get(user_id, 0)
            embed.add_field(name=user.name, value=f"**{action}** | Bet: **${bet}**", inline=False)

    await channel.send(embed=embed)

client.run('MTM0MTQzMTg5NTUzNTM5MDc3MQ.GYk0Oe.RkwwN0uGz_6g8pI0ox5iRTWBXxIT5vYOH8X92Q')
