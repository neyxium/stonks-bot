import json
from saving import load, save, reset
from API import getPass
from datetime import datetime
import discord
from discord import app_commands
from discord.ui import View, Button

data = load() or {"user_data": {}, "transactions": {}}
user_data = data.get("user_data", {})
transactions = data.get("transactions", {})

def save_user_data():
    save({"user_data": user_data, "transactions": transactions})

def add_transaction(sender_id, receiver_id, value):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Sender
    transactions.setdefault(sender_id, []).append({
        "type": "gave",
        "target": receiver_id,
        "value": value,
        "timestamp": timestamp
    })
    # Receiver
    transactions.setdefault(receiver_id, []).append({
        "type": "received",
        "target": sender_id,
        "value": value,
        "timestamp": timestamp
    })
    
    user_data[sender_id] = user_data.get(sender_id, 0) - value
    user_data[receiver_id] = user_data.get(receiver_id, 0) + value
    save_user_data()

def calculate_final_balances(user_id):
    balances = {}
    user_transactions = transactions.get(user_id, [])

    for tx in user_transactions:
        target = tx["target"]
        value = tx["value"]

        if tx["type"] == "gave":
            balances[user_id] = balances.get(user_id, 0) - value
            balances[target] = balances.get(target, 0) + value

        elif tx["type"] == "received":
            balances[user_id] = balances.get(user_id, 0) + value
            balances[target] = balances.get(target, 0) - value
    
    return balances

def get_value_from_reason(reason):
    if(reason == "eatsmart"):
        return 3.70
    elif(reason == "mm"):
        return 2.50
    elif(reason == "burger"):
        return 4
    elif(reason == "kitajska"):
        return 4

def register_slash_commands(bot: discord.Client):
    @bot.tree.command(name="hello", description="Greets the user")
    async def slash_hello(interaction: discord.Interaction):
        await interaction.response.send_message(f"Hello, {interaction.user.mention}!")

    @bot.tree.command(
        name="receive",
        description="Receive money from someone"
    )
    async def slash_receive(interaction: discord.Interaction, value: float, user: discord.Member):
        receiver = interaction.user
        sender = user
        receiver_id = str(receiver.id)
        sender_id = str(sender.id)

        add_transaction(sender_id, receiver_id, abs(value))
        await interaction.response.send_message(
            f"{sender} gave {value}€ to {receiver}. \n"
            f"{sender} has {user_data[sender_id]}€. \n"
            f"{receiver} has {user_data[receiver_id]}€."
        )

    @bot.tree.command(
        name="give",
        description="Give money to someone"
    )
    async def slash_give(interaction: discord.Interaction, value: float, user: discord.Member):
        receiver = user
        sender = interaction.user
        receiver_id = str(receiver.id)
        sender_id = str(sender.id)

        add_transaction(sender_id, receiver_id, abs(value))
        await interaction.response.send_message(
            f"{sender} gave {value}€ to {receiver}. \n"
            f"{sender} has {user_data[sender_id]}€. \n"
            f"{receiver} has {user_data[receiver_id]}€."
        )
    
    @bot.tree.command(
        name = "pay",
        description = "pay a meal to someone"
    )
    async def pay_meal(interaction: discord.Interaction, reason: str, user: discord.Member):
        sender = user
        receiver = interaction.user
        receiver_id = str(receiver.id)
        sender_id = str(sender.id)

        value = get_value_from_reason(reason)
        
        add_transaction(receiver_id, sender_id, abs(value))
        await interaction.response.send_message(
            f"{receiver} gave {value}€ to {sender}. \n"
            f"{sender} has {user_data[sender_id]}€. \n"
            f"{receiver} has {user_data[receiver_id]}€."
        )

    @bot.tree.command(
    name="reset",
    description="Resets your counter or mentioned user's counter"
    )
    async def slash_reset(interaction: discord.Interaction, user: discord.Member = None):
        target_user = user or interaction.user
        user_id = str(target_user.id)

        related_users = set()
        if user_id in transactions:
            for tx in transactions[user_id]:
                related_users.add(tx["target"])
            del transactions[user_id]

        for related_user in related_users:
            updated_transactions = []
            for tx in transactions.get(related_user, []):
                if tx["target"] == user_id:
                    if tx["type"] == "gave":
                        user_data[related_user] = user_data.get(related_user, 0) + tx["value"]
                    elif tx["type"] == "received":
                        user_data[related_user] = user_data.get(related_user, 0) - tx["value"]
                else:
                    updated_transactions.append(tx)
            transactions[related_user] = updated_transactions

        user_data[user_id] = 0

        save_user_data()

        if user:
            await interaction.response.send_message(f"{target_user.mention}'s counter and all related transactions have been reset to 0.")
        else:
            await interaction.response.send_message("Your counter and all related transactions have been reset to 0.")


    @bot.tree.command(
        name="value", 
        description="Shows your counter value or another user's value"
    )
    async def slash_value(interaction: discord.Interaction, user: discord.Member = None):
        target_user = user or interaction.user
        user_id = str(target_user.id)
        current_value = user_data.get(user_id, 0)
        if user:
            await interaction.response.send_message(f"{target_user.mention}'s current counter value: {current_value}€")
        else:
            await interaction.response.send_message(f"Your current counter value: {current_value}€")

    @bot.tree.command(
        name="transations",
        description="Shows your transaction history"
    )
    async def slash_transations(interaction: discord.Interaction, user: discord.Member = None):
        target_user = user or interaction.user
        user_id = str(target_user.id)
        user_transactions = transactions.get(user_id, [])
        if not user_transactions:
            if user:
                await interaction.response.send_message(f"{target_user.mention} has no transaction history.")
            else:
                await interaction.response.send_message("You have no transaction history.")
            return

        if user:
            history = f"**{target_user.mention}'s Transaction History:**\n"
        else:
            history = "**Your Transaction History:**\n"
        for tx in user_transactions:
            direction = "to" if tx["type"] == "gave" else "from"
            target = tx["target"]
            history += f"- {tx['type'].capitalize()} {tx['value']}€ {direction} <@{target}> on {tx['timestamp']}\n"

        await interaction.response.send_message(history)
        
    @bot.tree.command(
        name = "restart",
        description = "Resets everything"
    )
    async def reset_everything(interaction: discord.Interaction, reason: str):
        if(reason == getPass()):
            reset()
            global data
            global user_data
            global transactions
            data = load() or {"user_data": {}, "transactions": {}}
            user_data = data.get("user_data", {})
            transactions = data.get("transactions", {})
            await interaction.response.send_message("Everything was reset")
        else:
            await interaction.response.send_message("Everything was not reset :)")
    
    @bot.tree.command(
    name="status",
    description="Shows the final balances of users you interacted with in embed"
    )
    async def slash_status(interaction: discord.Interaction, user: discord.Member = None):
        target_user = user or interaction.user
        user_id = str(target_user.id)
        balances = calculate_final_balances(user_id)

        if not balances:
            if user:
                await interaction.response.send_message(f"{target_user.mention} has no transactions to display.")
            else:
                await interaction.response.send_message(
                    f"You have no transactions to display.\nCurrent balance: {user_data.get(user_id, 0)}€"
                )
            return

        embed = discord.Embed(
            title=f"{target_user.display_name}'s Transaction Summary" if user else "Your Transaction Summary",
            description="Here's how much you owe or are owed by others:",
            color=discord.Color.blue()
        )

        for target_id, balance in balances.items():
            if target_id != user_id:
                mention = f"<@{target_id}>"
                if(balance > 0):
                    embed.add_field(name="User:", value=f"{mention} owes: {balance}€", inline=False)
                else:
                    embed.add_field(name="User:", value=f"{mention} is owed: {abs(balance)}€", inline=False)

        embed.set_footer(text=f"Current balance: {user_data.get(user_id, 0)}€")

        class StatusView(View):
            def __init__(self):
                super().__init__(timeout=None)

            @discord.ui.button(label="Reset Transactions", style=discord.ButtonStyle.danger)
            async def reset_button(self, interaction: discord.Interaction, button: Button):
                if interaction.user.id != target_user.id:
                    await interaction.response.send_message(
                        "You are not authorized to reset these transactions.", ephemeral=True
                    )
                    return

                related_users = set()
                if user_id in transactions:
                    for tx in transactions[user_id]:
                        related_users.add(tx["target"])
                    del transactions[user_id]

                for related_user in related_users:
                    for tx in transactions.get(related_user, []):
                        if tx["target"] == user_id:
                            if tx["type"] == "gave":
                                user_data[related_user] = user_data.get(related_user, 0) + tx["value"]
                            elif tx["type"] == "received":
                                user_data[related_user] = user_data.get(related_user, 0) - tx["value"]
                    transactions[related_user] = [
                        tx for tx in transactions.get(related_user, []) if tx["target"] != user_id
                    ]

                user_data[user_id] = 0
                save_user_data()

                await interaction.response.edit_message(
                    content=f"{target_user.mention}'s transactions and balance have been reset.",
                    embed=None,
                    view=None
                )
            # Gumb za prikaz trenutnega stanja
            @discord.ui.button(label="View Current Balance", style=discord.ButtonStyle.primary)
            async def view_balance_button(self, interaction: discord.Interaction, button: Button):
                current_balance = user_data.get(user_id, 0)
                await interaction.response.send_message(
                    f"{target_user.mention}'s current balance is: {current_balance}€",
                    ephemeral=True
                )
            
            @discord.ui.button(label="View All Transactions", style=discord.ButtonStyle.success)
            async def view_transactions_button(self, interaction: discord.Interaction, button: Button):
                user_transactions = transactions.get(user_id, [])
                if not user_transactions:
                    await interaction.response.send_message(
                        "You have no transactions to display.", ephemeral=True
                    )
                    return

                # Pripravi seznam transakcij
                transaction_history = "**Your Transactions:**\n"
                for tx in user_transactions:
                    direction = "to" if tx["type"] == "gave" else "from"
                    transaction_history += f"- {tx['type'].capitalize()} {tx['value']}€ {direction} <@{tx['target']}> on {tx['timestamp']}\n"

                await interaction.response.send_message(
                    transaction_history, ephemeral=True
                )

        await interaction.response.send_message(embed=embed, view=StatusView())


    @bot.tree.command(name="help", description="Displays the help menu")
    async def slash_help(interaction: discord.Interaction):
        help_menu = (
            "## Help Menu\n"
            "- /hello - Greets the user with ping\n"
            "- /receive [value] [member] - Increment your money and decrement mentioned user's money\n"
            "- /give [value] [member] - Decrement your money and increment mentioned user's money\n"
            "- /pay [reason] [member] - Pay someone else's meal example for reason: eatsmart, mm, burger, kitajska\n"
            "- /reset [member] - Resets your personal or mentioned user's counter\n"
            "- /value [member] - Shows your current or mentioned user's counter value\n"
            "- /transations [member] - Shows your's or mentioned user's transaction history\n"
            "- /status [member] - Shows how much each person owes you or how much you owe to someone\n"
            "- /restart - Resets everything\n"
            "- /help - Displays this help menu"
        )
        await interaction.response.send_message(help_menu)