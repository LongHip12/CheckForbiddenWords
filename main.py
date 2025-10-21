import discord
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime
from colorama import init, Fore, Back, Style

# Khởi tạo colorama
init(autoreset=True)

# Load Dotenv
load_dotenv()

# Cấu hình
USER_ID_TO_REPORT = 1130115056395362404  # User ID để gửi báo cáo
BANNED_WORDS = [
    "ass", "bắc kì", "bắc kỳ", "béo", "buồi", "cặc", "clm", "cứt", "dick", 
    "dm", "đái", "đéo", "đĩ", "địt", "địt mẹ", "đỗn lì", "đụ", "fuck", 
    "lồn", "mẹ mày béo", "nam kì", "nam kỳ", "namky", "parky", "rape", 
    "trung kì", "trung kỳ", "trungky"
]

# Table quản lý kênh check chửi bậy
CHANNEL_MONITORING_TABLE = {
    "enabled_channels": [
        1407335793000714391,  # Kênh 1
        1409896785610018816,  # Kênh 2  
        1407357297939845131,  # Kênh 3
        1409791680864850001   # Kênh 4
    ],
    "excluded_channels": [], # ID các kênh bỏ qua
    "enabled_servers": [],   # ID server được theo dõi (để trống = theo dõi tất cả)
    "excluded_servers": []   # ID server bỏ qua
}

class SelfBot(discord.Client):
    def log_info(self, message):
        """Log thông tin với màu xanh lá"""
        print(f"{Fore.GREEN}[Info]{Style.RESET_ALL} {message}")
    
    def log_warn(self, message):
        """Log cảnh báo với màu vàng"""
        print(f"{Fore.YELLOW}[Warn]{Style.RESET_ALL} {message}")
    
    def log_error(self, message):
        """Log lỗi với màu đỏ"""
        print(f"{Fore.RED}[Error]{Style.RESET_ALL} {message}")
    
    async def on_ready(self):
        self.log_info(f'Selfbot đã đăng nhập với tên: {self.user.name}')
        self.log_info(f'Đang theo dõi {len(BANNED_WORDS)} từ cấm')
        self.log_info(f'Sẽ gửi báo cáo đến user: {USER_ID_TO_REPORT}')
        self.log_info(f'Đang theo dõi {len(CHANNEL_MONITORING_TABLE["enabled_channels"])} kênh cụ thể')
        self.log_warn('Đang theo dõi cả tin nhắn của chính mình')
        
    async def on_message(self, message):
        # KHÔNG bỏ qua tin nhắn của chính bot - theo dõi cả chính mình
        # if message.author.id == self.user.id:
        #     return
            
        # Kiểm tra cài đặt kênh/server
        if not self.should_monitor_channel(message.channel, message.guild):
            return
            
        # Kiểm tra từ cấm
        detected_words = self.check_banned_words(message.content)
        
        if detected_words:
            await self.handle_violation(message, detected_words)
    
    def should_monitor_channel(self, channel, guild):
        """Kiểm tra xem kênh/server có nên được theo dõi không"""
        
        # Chỉ theo dõi các kênh trong danh sách enabled_channels
        if channel.id not in CHANNEL_MONITORING_TABLE["enabled_channels"]:
            return False
            
        # Kiểm tra server exclusion (nếu có)
        if guild and guild.id in CHANNEL_MONITORING_TABLE["excluded_servers"]:
            return False
            
        return True
    
    def check_banned_words(self, content):
        """Kiểm tra và trả về danh sách từ vi phạm"""
        content_lower = content.lower()
        detected = []
        
        for word in BANNED_WORDS:
            if word.lower() in content_lower:
                detected.append(word)
                
        return detected if detected else None
    
    async def handle_violation(self, message, detected_words):
        try:
            # Tạo tin nhắn text thay vì embed
            report_msg = f"""
🚨 **PHÁT HIỆN TỪ NGỮ VI PHẠM**
👤 **Người gửi:** {message.author} (`{message.author.id}`)
📝 **Tin nhắn:** {message.content[:500]}
🚫 **Từ vi phạm:** {", ".join(detected_words)}
🔗 **Link:** {message.jump_url}
🕒 **Thời gian:** <t:{int(message.created_at.timestamp())}:F>
📁 **Kênh:** {message.channel.name} (`{message.channel.id}`)
"""
            
            # Gửi đến user chỉ định
            try:
                target_user = await self.fetch_user(USER_ID_TO_REPORT)
                if target_user:
                    await target_user.send(report_msg)
                    self.log_info(f'Đã gửi báo cáo đến {target_user.name}')
            except Exception as e:
                self.log_error(f'Lỗi gửi DM đến user chỉ định: {e}')
                    
        except Exception as e:
            self.log_error(f'Lỗi xử lý vi phạm: {e}')

# Chạy selfbot
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    
    if not token:
        token = input("Nhập Discord token: ")
    
    # Không cần cấu hình intents cho selfbot
    client = SelfBot()
    client.run(token)
