import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import sys
from typing import List, Optional

# 加入專案根目錄
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# 讀取設定檔
from app.config import Settings


EMAIL_HOST = Settings.EMAIL_HOST
EMAIL_PORT = Settings.EMAIL_PORT

EMAIL_PASSWORD = Settings.EMAIL_PASSWORD
EMAIL_FROM = Settings.EMAIL_FROM
EMAIL_VERIFY_DOMAIN = Settings.EMAIL_VERIFY_DOMAIN  # 替換為你的域名


class GmailSender:
    def __init__(self, email: str, password: str):
        """
        初始化 Gmail 發送器

        Args:
            email: Gmail 帳號
            password: Gmail 應用程式密碼 (不是登入密碼)

        注意：需要開啟 Gmail 的兩步驟驗證並生成應用程式密碼
        """
        self.email = EMAIL_FROM
        self.password = EMAIL_PASSWORD
        self.smtp_server = EMAIL_HOST
        self.smtp_port = EMAIL_PORT

    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        is_html: bool = False,
        attachments: Optional[List[str]] = None,
    ) -> bool:
        """
        發送郵件

        Args:
            to_emails: 收件人列表
            subject: 郵件主題
            body: 郵件內容
            is_html: 是否為 HTML 格式
            attachments: 附件文件路徑列表

        Returns:
            bool: 發送成功返回 True，失敗返回 False
        """
        try:
            # 建立郵件物件
            msg = MIMEMultipart()
            msg["From"] = self.email
            msg["To"] = ", ".join(to_emails)
            msg["Subject"] = subject

            # 添加郵件內容
            if is_html:
                msg.attach(MIMEText(body, "html", "utf-8"))
            else:
                msg.attach(MIMEText(body, "plain", "utf-8"))

            # 添加附件
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                "Content-Disposition",
                                f"attachment; filename= {os.path.basename(file_path)}",
                            )
                            msg.attach(part)

            # 連接到 Gmail SMTP 伺服器
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # 啟用 TLS 加密
            server.login(self.email, self.password)

            # 發送郵件
            text = msg.as_string()
            server.sendmail(self.email, to_emails, text)
            server.quit()

            print(f"郵件已成功發送到: {', '.join(to_emails)}")
            return True

        except Exception as e:
            print(f"發送郵件時發生錯誤: {str(e)}")
            return False

    def send_verification_email(
        self, email: str, token: str, domain: str = EMAIL_VERIFY_DOMAIN
    ) -> bool:
        """
        發送驗證郵件

        Args:
            email: 收件人 email
            token: 驗證 token
            domain: 網域名稱

        Returns:
            bool: 發送成功返回 True，失敗返回 False
        """
        verification_link = f"http://{domain}/auth/verifyEmail?token={token}"
        print(f"發送驗證郵件到: {email}  : {verification_link}")

        subject = "📩 請驗證您的 Email"

        # 純文字版本
        text_body = f"""
親愛的用戶，

感謝您註冊我們的服務！

請點擊以下連結完成 Email 驗證：
{verification_link}

如果您無法點擊連結，請複製並貼上到瀏覽器中。

此驗證連結將在 24 小時後過期。

如果您沒有註冊我們的服務，請忽略此郵件。

謝謝！
        """

        # HTML 版本
        html_body = f"""
        <html>
        <body>
            <h2>Email 驗證</h2>
            <p>親愛的用戶，</p>
            <p>感謝您註冊我們的服務！</p>
            <p>請點擊以下按鈕完成 Email 驗證：</p>
            <div style="text-align: center; margin: 20px;">
                <a href="{verification_link}" 
                   style="background-color: #4CAF50; color: white; padding: 15px 32px; 
                          text-decoration: none; display: inline-block; border-radius: 4px;">
                    驗證 Email
                </a>
            </div>
            <p>如果按鈕無法點擊，請複製以下連結到瀏覽器：</p>
            <p><a href="{verification_link}">{verification_link}</a></p>
            <p><strong>此驗證連結將在 24 小時後過期。</strong></p>
            <p>如果您沒有註冊我們的服務，請忽略此郵件。</p>
            <p>謝謝！</p>
        </body>
        </html>
        """

        return self.send_email(
            to_emails=[email], subject=subject, body=html_body, is_html=True
        )


# 使用範例
def main():
    # Gmail 配置
    GMAIL_EMAIL = EMAIL_FROM
    GMAIL_PASSWORD = EMAIL_PASSWORD  # 使用應用程式密碼，不是登入密碼
    SEND_MAIL = "dino5168@gmail.com"

    # 建立 Gmail 發送器
    gmail_sender = GmailSender(GMAIL_EMAIL, GMAIL_PASSWORD)
    gmail_sender.send_verification_email(SEND_MAIL, "token123456", EMAIL_VERIFY_DOMAIN)

    # 範例 1: 發送簡單文字郵件

    # 範例 2: 發送 HTML 郵件
    html_content = """
    <h1>歡迎使用我們的服務！</h1>
    <p>這是一封 <strong>HTML 格式</strong> 的郵件。</p>
    <ul>
        <li>功能 1</li>
        <li>功能 2</li>
        <li>功能 3</li>
    </ul>
    """


if __name__ == "__main__":
    main()
