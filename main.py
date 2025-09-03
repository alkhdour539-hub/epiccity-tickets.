import discord
from discord.ext import commands
from discord.ui import Select, View, Button
import os
import asyncio
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

CATEGORY_NAME = "Support Tickets"
POLICE_CATEGORY_NAME = "Police Tickets"
MEDICAL_CATEGORY_NAME = "🚑 Medical Tickets"
ADMIN_ROLE_NAME = "Admin"

# الأزرار
class TicketButtons(View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.user = user

    # زر الإغلاق
    @discord.ui.button(label="CLOSE Ticket", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user_id = interaction.channel.topic
        user = guild.get_member(int(user_id))

        if interaction.user.guild_permissions.manage_channels or str(interaction.user.id) == user_id:
            await interaction.channel.set_permissions(user, send_messages=False, view_channel=False)
            await interaction.channel.edit(name=f"closed-{interaction.channel.name}")
            await interaction.response.send_message("✅ تم إغلاق التذكرة بشكل نهائي.", ephemeral=True)
            await interaction.channel.send("🔒 تم إغلاق هذه التذكرة ولا يمكن إعادة فتحها.")
        else:
            await interaction.response.send_message("❌ ما عندك صلاحية تغلق التذكرة.", ephemeral=True)

    # زر الحذف (للأدمن فقط)
    @discord.ui.button(label="DELETE Ticket", style=discord.ButtonStyle.red)
    async def delete_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.guild_permissions.manage_channels:  # بس الأدمن
            embed = discord.Embed(
                title="⏳ حذف التذكرة",
                description="هذه التذكرة سيتم حذفها بعد **5 ثواني** بواسطة الإدارة.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            await asyncio.sleep(5)
            await interaction.channel.delete()
        else:
            await interaction.response.send_message("❌ هذا الزر مخصص للإدارة فقط.", ephemeral=True)


# عند تشغيل البوت
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


# بانل الدعم العام
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    embed = discord.Embed(
        title="🎫 EPIC CITY TICKETS",
        description=(
            "اختر نوع التذكرة من القائمة 👇\n\n"
            "🔴 لمراجعة الباند أو التحذير\n"
            "🟢 لطلب التعويض\n"
            "🔧 للمشاكل التقنية والبرمجية\n"
            "📌 لرفع الثغرات والملاحظات\n"
            "📞 للتواصل مع الإدارة العليا\n"
            "🛒 للاستفسار بخصوص المتجر"
        ),
        color=discord.Color.purple()
    )
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/attachments/1408914593694089360/1409632446563221617/ec_logo.png"
    )

    select = Select(
        placeholder="📩 اختر نوع التذكرة...",
        options=[
            discord.SelectOption(label="مراجعة باند / تحذير", emoji="🔴", value="ban"),
            discord.SelectOption(label="طلب تعويض", emoji="🟢", value="comp"),
            discord.SelectOption(label="مشكلة تقنية / برمجية", emoji="🔧", value="tech"),
            discord.SelectOption(label="رفع ثغرة / ملاحظة", emoji="📌", value="bug"),
            discord.SelectOption(label="التواصل مع الإدارة العليا", emoji="📞", value="admin"),
            discord.SelectOption(label="الاستفسار عن المتجر", emoji="🛒", value="store"),
        ]
    )

    async def my_callback(interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        ticket_type = interaction.data['values'][0]

        type_names = {
            "ban": "مراجعة باند / تحذير",
            "comp": "طلب تعويض",
            "tech": "مشكلة تقنية / برمجية",
            "bug": "رفع ثغرة / ملاحظة",
            "admin": "التواصل مع الإدارة العليا",
            "store": "الاستفسار عن المتجر",
        }

        category = discord.utils.get(guild.categories, name=CATEGORY_NAME)
        if category is None:
            category = await guild.create_category(CATEGORY_NAME)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True),
        }

        admin_role = discord.utils.get(guild.roles, name=ADMIN_ROLE_NAME)
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(
            name=f"{ticket_type}-ticket-{user.name}",
            category=category,
            overwrites=overwrites,
            topic=str(user.id)
        )

        await ticket_channel.send(
            f"👋 مرحبا {user.mention}!\n"
            f"تم فتح تذكرتك من نوع: **{type_names[ticket_type]}**\n"
            f"سيتم الرد عليك من قبل فريق الإدارة بأقرب وقت.",
            view=TicketButtons(user)
        )

        await interaction.response.send_message(
            f"✅ تم إنشاء تذكرتك في الروم: {ticket_channel.mention}", ephemeral=True
        )

    select.callback = my_callback
    view = View()
    view.add_item(select)

    await ctx.send(embed=embed, view=view)


# بانل الشرطة
@bot.command()
@commands.has_permissions(administrator=True)
async def setup_police(ctx):
    embed = discord.Embed(
        title="👮 POLICE TICKETS",
        description=(
            "اختر نوع التذكرة الخاصة بالشرطة 👇\n\n"
            "🎖️ تقديم شكوى عسكرية\n"
            "🏛️ تقديم طلب إلى المحكمة\n"
            "📞 التواصل مع قيادة الشرطة"
        ),
        color=discord.Color.blue()
    )
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/attachments/1408914593694089360/1409632446563221617/ec_logo.png"
    )

    select = Select(
        placeholder="📩 اختر نوع التذكرة...",
        options=[
            discord.SelectOption(label="تقديم شكوى عسكرية", emoji="🎖️", value="military"),
            discord.SelectOption(label="تقديم طلب إلى المحكمة", emoji="🏛️", value="court"),
            discord.SelectOption(label="التواصل مع قيادة الشرطة", emoji="📞", value="police"),
        ]
    )

    async def police_callback(interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        ticket_type = interaction.data['values'][0]

        type_names = {
            "military": "تقديم شكوى عسكرية",
            "court": "تقديم طلب إلى المحكمة",
            "police": "التواصل مع قيادة الشرطة",
        }

        category = discord.utils.get(guild.categories, name=POLICE_CATEGORY_NAME)
        if category is None:
            category = await guild.create_category(POLICE_CATEGORY_NAME)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True),
        }

        admin_role = discord.utils.get(guild.roles, name=ADMIN_ROLE_NAME)
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(
            name=f"{ticket_type}-ticket-{user.name}",
            category=category,
            overwrites=overwrites,
            topic=str(user.id)
        )

        await ticket_channel.send(
            f"👮 مرحبا {user.mention}!\n"
            f"تم فتح تذكرتك من نوع: **{type_names[ticket_type]}**\n"
            f"سيتم الرد عليك من قبل المسؤولين في أقرب وقت.",
            view=TicketButtons(user)
        )

        await interaction.response.send_message(
            f"✅ تم إنشاء تذكرتك في روم الشرطة: {ticket_channel.mention}", ephemeral=True
        )

    select.callback = police_callback
    view = View()
    view.add_item(select)

    await ctx.send(embed=embed, view=view)


# بانل الإسعاف
@bot.command()
@commands.has_permissions(administrator=True)
async def setup_medical(ctx):
    embed = discord.Embed(
        title="🩺 MEDICAL TICKETS",
        description=(
            "اختر نوع التذكرة الخاصة بالإسعاف 👇\n\n"
            "🩺 لفتح تيكت رئاسة الإسعاف\n"
            "🏥 لفتح تيكت شكوى على مسعف"
        ),
        color=0xFFFFFF  # اللون الأبيض
    )
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/attachments/1408914593694089360/1409632446563221617/ec_logo.png"
    )

    select = Select(
        placeholder="📩 اختر نوع التذكرة...",
        options=[
            discord.SelectOption(label="فتح تيكت رئاسة الإسعاف", emoji="🩺", value="chief"),
            discord.SelectOption(label="فتح تيكت شكوى على مسعف", emoji="🏥", value="complaint"),
        ]
    )

    async def medical_callback(interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        ticket_type = interaction.data['values'][0]

        type_names = {
            "chief": "فتح تيكت رئاسة الإسعاف",
            "complaint": "فتح تيكت شكوى على مسعف",
        }

        category = discord.utils.get(guild.categories, name=MEDICAL_CATEGORY_NAME)
        if category is None:
            category = await guild.create_category(MEDICAL_CATEGORY_NAME)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True),
        }

        admin_role = discord.utils.get(guild.roles, name=ADMIN_ROLE_NAME)
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(
            name=f"medical-{ticket_type}-{user.name}",
            category=category,
            overwrites=overwrites,
            topic=str(user.id)
        )

        await ticket_channel.send(
            f"🩺 مرحبا {user.mention}!\n"
            f"تم فتح تذكرتك من نوع: **{type_names[ticket_type]}**\n"
            f"سيتم الرد عليك من قبل إدارة الإسعاف قريباً.",
            view=TicketButtons(user)
        )

        await interaction.response.send_message(
            f"✅ تم إنشاء تذكرتك الطبية في الروم: {ticket_channel.mention}", ephemeral=True
        )

    select.callback = medical_callback
    view = View()
    view.add_item(select)

    await ctx.send(embed=embed, view=view)


# تشغيل البوت
keep_alive()
bot.run(os.getenv("TOKEN"))
