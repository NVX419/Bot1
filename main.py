from flask import Flask, request, render_template_string
import threading
import os
import discord
from discord.ext import commands
from discord import app_commands, Interaction, ButtonStyle, TextStyle
from discord.ui import View, Button, Modal, TextInput, Select
import datetime
import asyncio

app = Flask(__name__)
bot_thread = None

# Template HTML with professional RTL design
html_template = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>نظام التذاكر الاحترافي</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; text-align: center; padding: 2rem; margin: 0; }
        .container { max-width: 800px; margin: 0 auto; background: #1e293b; padding: 2.5rem; border-radius: 1.5rem; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); border: 1px solid #334155; }
        h1 { color: #38bdf8; font-size: 2.5rem; margin-bottom: 1.5rem; border-bottom: 2px solid #38bdf8; padding-bottom: 1rem; }
        .input-group { margin-bottom: 1.5rem; text-align: right; }
        label { display: block; margin-bottom: 0.5rem; font-weight: 500; color: #94a3b8; font-size: 1.1rem; }
        input { width: 100%; padding: 0.85rem 1.1rem; border-radius: 0.75rem; border: 1px solid #334155; background: #0f172a; color: white; box-sizing: border-box; transition: all 0.3s; font-size: 1rem; }
        input:focus { outline: none; border-color: #38bdf8; box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2); }
        button { width: 100%; background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%); color: white; padding: 1rem 1.5rem; border: none; border-radius: 0.75rem; cursor: pointer; font-size: 1.1rem; font-weight: 600; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
        button:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2); }
        .status { margin-top: 1.5rem; padding: 1.25rem; border-radius: 0.75rem; background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; color: #10b981; font-weight: 500; font-size: 1.1rem; }
        .instructions { margin-top: 2.5rem; text-align: right; background: #1e293b; padding: 2rem; border-radius: 1.25rem; border: 1px solid #334155; box-shadow: inset 0 2px 4px 0 rgba(0,0,0,0.06); }
        .instructions h3 { color: #38bdf8; margin-top: 0; font-size: 1.4rem; margin-bottom: 1rem; }
        .instructions ul { list-style: none; padding: 0; }
        .instructions li { margin-bottom: 1rem; padding-right: 1.5rem; position: relative; }
        .instructions li::before { content: '←'; position: absolute; right: 0; color: #38bdf8; }
        .instructions code { background: #0f172a; padding: 0.3rem 0.6rem; border-radius: 0.4rem; color: #f472b6; font-family: 'Consolas', monospace; font-size: 0.95rem; }
        .features { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 2rem; text-align: right; }
        .feature-card { background: #0f172a; padding: 1rem; border-radius: 0.75rem; border: 1px solid #334155; }
        .feature-card h4 { color: #38bdf8; margin: 0 0 0.5rem 0; }
        .feature-card p { margin: 0; font-size: 0.9rem; color: #94a3b8; }
    </style>
</head>
<body>
    <div class="container">
        <h1>نظام التذاكر المتقدم 🎫</h1>
        <p style="color: #94a3b8; margin-bottom: 2rem;">لوحة التحكم الشاملة لإدارة التذاكر عبر الديسكورد</p>
        
        <form method="POST">
            <div class="input-group">
                <label>توكن البوت الخاص بك</label>
                <input type="text" name="token" placeholder="أدخل التوكن هنا (MTA...)" required value="{{ token }}">
            </div>
            <button type="submit">تفعيل نظام التذاكر</button>
        </form>
        
        {% if message %}
        <div class="status">{{ message }}</div>
        {% endif %}

        <div class="features">
            <div class="feature-card">
                <h4>سلاش كوماند ⚡</h4>
                <p>أوامر تفاعلية حديثة وسهلة الاستخدام</p>
            </div>
            <div class="feature-card">
                <h4>إحصائيات مباشرة 📊</h4>
                <p>تحديث لحظي لعدد التذاكر المفتوحة</p>
            </div>
            <div class="feature-card">
                <h4>تخصيص كامل 🛠️</h4>
                <p>تعديل الرسائل، الصور، والمنيو بسهولة</p>
            </div>
            <div class="feature-card">
                <h4>نظام لوق 📝</h4>
                <p>تتبع كل ما يحدث في التذاكر</p>
            </div>
        </div>

        <div class="instructions">
            <h3>دليل الأوامر:</h3>
            <ul>
                <li><code>/setup_ticket</code> - إرسال رسالة التذاكر الأساسية في الروم الحالي.</li>
                <li><code>/ticket_manager</code> - تخصيص المنيو، الأزرار، الصور، ورسالة الترحيب.</li>
                <li><code>/ticket_stats</code> - عرض رسالة إحصائيات تتحدث تلقائياً كل ثانية لتعطيك العدد الدقيق.</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

class TicketModal(Modal, title='فتح تذكرة جديدة'):
    name = TextInput(label='الاسم المستعار', placeholder='أدخل اسمك...', required=True)
    reason = TextInput(label='سبب فتح التذكرة', style=TextStyle.paragraph, placeholder='اكتب التفاصيل هنا...', required=True)

    async def on_submit(self, interaction: Interaction):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            overwrites=overwrites
        )
        
        await interaction.response.send_message(f"تم إنشاء تذكرتك بنجاح: {channel.mention}", ephemeral=True)
        
        embed = discord.Embed(title="تذكرة جديدة 🎫", color=discord.Color.blue(), timestamp=datetime.datetime.now())
        embed.add_field(name="بواسطة", value=interaction.user.mention)
        embed.add_field(name="الاسم", value=self.name.value)
        embed.add_field(name="السبب", value=self.reason.value, inline=False)
        
        view = View()
        view.add_item(Button(label="إغلاق التذكرة", style=ButtonStyle.danger, custom_id="close_ticket"))
        
        await channel.send(embed=embed, view=view)

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(label="فتح تذكرة", style=ButtonStyle.primary, emoji="🎫", custom_id="persistent_view:open")
    async def open_ticket(self, interaction: Interaction, button: Button):
        await interaction.response.send_modal(TicketModal())

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(TicketView())
        await self.tree.sync()

bot = Bot()

@bot.tree.command(name="setup_ticket", description="إعداد رسالة فتح التذاكر")
async def setup_ticket(interaction: Interaction):
    embed = discord.Embed(
        title="نظام الدعم الفني 🎫",
        description="لفتح تذكرة جديدة، يرجى الضغط على الزر أدناه وسيتم التواصل معك من قبل فريق العمل.",
        color=discord.Color.blue()
    )
    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("تم إرسال لوحة التذاكر بنجاح ✅", ephemeral=True)

@bot.tree.command(name="ticket_manager", description="تخصيص منيو التذاكر والأزرار")
@app_commands.describe(message="نص الرسالة", image_url="رابط صورة الهيدر")
async def ticket_manager(interaction: Interaction, message: str = None, image_url: str = None):
    embed = discord.Embed(title="تخصيص نظام التذاكر 🛠️", color=discord.Color.gold())
    embed.description = message if message else "اختر الإعداد الذي تريد تعديله أدناه."
    if image_url: embed.set_image(url=image_url)
    
    class ManagerView(View):
        @discord.ui.select(placeholder="اختر نوع التذكرة الافتراضي...", options=[
            discord.SelectOption(label="دعم فني", emoji="🛠️", value="support"),
            discord.SelectOption(label="تقديم شكوى", emoji="⚠️", value="complaint"),
            discord.SelectOption(label="استفسار عام", emoji="❓", value="general")
        ])
        async def select_callback(self, select_interaction: Interaction, select: Select):
            await select_interaction.response.send_message(f"تم تحديث النوع الافتراضي إلى: {select.values[0]}", ephemeral=True)

    await interaction.response.send_message("قائمة إدارة التذاكر", view=ManagerView(), ephemeral=True)

@bot.tree.command(name="ticket_stats", description="عرض إحصائيات التذاكر المباشرة (تحديث كل ثانية)")
async def ticket_stats(interaction: Interaction):
    await interaction.response.send_message("جاري تشغيل عداد التذاكر المباشر... 📊")
    msg = await interaction.original_response()
    
    while True:
        try:
            count = len([c for c in interaction.guild.text_channels if c.name.startswith("ticket-")])
            
            embed = discord.Embed(title="إحصائيات التذاكر المباشرة 📊", color=discord.Color.green())
            embed.add_field(name="عدد التذاكر المفتوحة الآن", value=f"```fix\n{count} تذكرة\n```", inline=False)
            embed.set_footer(text=f"آخر تحديث: {datetime.datetime.now().strftime('%H:%M:%S')} | يتحدث كل ثانية")
            
            await msg.edit(content=None, embed=embed)
            await asyncio.sleep(1)
        except Exception:
            break

def run_bot(token):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        bot.run(token)
    except Exception as e:
        print(f"Bot execution error: {e}")

@app.route("/", methods=["GET", "POST"])
def index():
    global bot_thread
    message = ''
    token = ''
    if request.method == "POST":
        token = request.form.get("token")
        if token:
            if not bot_thread or not bot_thread.is_alive():
                bot_thread = threading.Thread(target=run_bot, args=(token,), daemon=True)
                bot_thread.start()
                message = "تم تشغيل نظام التذاكر بنجاح! راجع سيرفر الديسكورد ✅"
            else:
                message = "النظام يعمل بالفعل 🔄"
    return render_template_string(html_template, message=message, token=token)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
