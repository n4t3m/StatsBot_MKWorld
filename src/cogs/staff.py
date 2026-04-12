import datetime as dt
import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

import common.data_handler as data_handler

load_dotenv()
mods_role_ids = [int(role_id) for role_id in os.getenv("Mods_Role_ID").split(",")]


class Staff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="data", description="Display player data")
    @app_commands.describe(name="Player name, discord id, or mkc id (optional)")
    async def data(self, interaction: discord.Interaction, name: str | None = None):
        if name is None:
            name = str(interaction.user.id)
        player = await data_handler.fetch_player(
            name, season=os.getenv("CURRENT_SEASON"), game_mode="24p"
        )

        if player is None:
            await interaction.response.send_message(
                f"Player '{name}' not found.", ephemeral=True
            )
            return

        mkc_url = (
            os.getenv("MKCentral_Site_URL")
            + f"/registry/players/profile?id={player['mkcId']}"
        )
        mkc_field = f"[{player['mkcId']}]({mkc_url})"

        embed = discord.Embed(
            title="Player Data",
            url=f"https://lounge.mkcentral.com/mkworld/PlayerDetails/{player['id']}",
            description=player["name"],
            timestamp=dt.datetime.now(dt.UTC),
        )

        embed.add_field(name="MKC ID", value=mkc_field, inline=False)

        embed.set_footer(
            text="MKCentral Lounge",
            icon_url="https://raw.githubusercontent.com/VikeMK/Lounge-API/refs/heads/main/src/Lounge.Web/wwwroot/favicon.ico",
        )

        try:
            discordid = player["discordId"]
        except KeyError:
            discordid = "Null"
        embed.add_field(name="Discord ID", value=discordid, inline=False)
        embed.add_field(name="Mention", value=f"<@!{discordid}>", inline=False)
        try:
            country_code = player["countryCode"]
        except KeyError:
            country_code = "Null"
        embed.add_field(name="Country Code", value=country_code, inline=False)
        embed.add_field(name="Hidden", value=player["isHidden"], inline=False)
        embed.set_footer(
            text="MKCentral Lounge",
            icon_url="https://raw.githubusercontent.com/VikeMK/Lounge-API/refs/heads/main/src/Lounge.Web/wwwroot/favicon.ico",
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Staff(bot))
