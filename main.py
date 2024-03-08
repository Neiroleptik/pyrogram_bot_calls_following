from pyrogram import Client, filters
import json

api_id = "your api id"
api_hash = "your api hash"
session_name = "YOUR_SESSION_NAME"

your_user_id = '' # like "121315346"
your_nickname = '@' # like @username

group_id = -0000000000 # here group id type: Integer

def load_subscriptions():
    try:
        with open("subscriptions.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_subscriptions(subscriptions):
    with open("subscriptions.json", "w") as file:
        json.dump(subscriptions, file)


subscriptions = load_subscriptions()

app = Client(session_name, api_id=api_id, api_hash=api_hash)


@app.on_message(filters.group & filters.chat(group_id) & filters.command("sid"))
async def follow_user(client, message):
    await message.reply("Yo, This bot can follow your lovely alpha callers!\nCommands:\n/follow @username\n/unfollow @username")


@app.on_message(filters.group & filters.chat(group_id) & filters.command("follow"))
async def follow_user(client, message):
    if len(message.command) > 1:
        username = message.command[1].replace("@", "")
        try:
            user = await app.get_users(username)
            user_id = str(user.id)
            follower_id = str(message.from_user.id)

            already_following = False
            if user_id in subscriptions:
                if follower_id in subscriptions[user_id]:
                    already_following = True
                else:
                    subscriptions[user_id].append(follower_id)
            else:
                subscriptions[user_id] = [follower_id]

            save_subscriptions(subscriptions)

            if already_following:
                await message.reply(f"You are already following.")
            else:
                await message.reply(f"You are now following @{username}.")
        except Exception as e:
            await message.reply("Failed to find user. Please make sure the username is correct.")
    else:
        await message.reply("Please specify the username you want to follow after the command.")



@app.on_message(filters.group & filters.chat(group_id) & filters.command("unfollow"))
async def unfollow_user(client, message):
    if len(message.command) > 1:
        username = message.command[1].replace("@", "")
        try:
            user = await app.get_users(username)
            user_id = str(user.id)
            follower_id = str(message.from_user.id)

            if user_id in subscriptions and follower_id in subscriptions[user_id]:
                subscriptions[user_id].remove(follower_id)
                if not subscriptions[user_id]:
                    subscriptions.pop(user_id)
                save_subscriptions(subscriptions)
                await message.reply(f"You have unfollowed @{username}.")
            else:
                await message.reply("You're not following this user.")
        except Exception as e:
            await message.reply("Failed to find user. Please make sure the username is correct.")
    else:
        await message.reply("Please specify the username you want to unfollow after the command.")



@app.on_message(filters.group & filters.chat(group_id))
async def notify_followers(client, message):
    sender_id = str(message.from_user.id)
    if sender_id in subscriptions and message.text:
        words = message.text.split()
        trigger_words = [word for word in words if len(word) in [43, 44] or word[0] == "$"]

        if trigger_words:
            followers = subscriptions[sender_id]
            if followers:
                users_info = await app.get_users(followers)
                mentions = ", ".join([f"@{user.username}" for user in users_info if user.username])
                sid_message = ''
                for follower in followers:
                    if follower == your_user_id:
                        sid_message = f'TAG ME PLEASE {your_nickname}'
                if mentions:
                    await message.reply(f"🔔 {mentions}!\n{sid_message}")


if __name__ == "__main__":
    app.run()
