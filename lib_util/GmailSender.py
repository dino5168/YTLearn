import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import sys
from pathlib import Path
from app.config import settings

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 把專案根目錄加入 sys.path
# BASE_DIR = Path(__file__).resolve().parent.parent  # 根據實際位置調整
# sys.path.append(str(BASE_DIR))

# 讀取設定檔
# from app.config import Settings


@dataclass
class EmailConfig:
    """郵件設定類別"""

    host: str
    port: int
    username: str
    password: str
    from_email: str
    verify_domain: str
    use_tls: bool = True

    @classmethod
    def from_settings(cls) -> "EmailConfig":
        """從設定檔載入郵件設定"""
        return cls(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.ADMIN_EMAIL,
            password=settings.EMAIL_PASSWORD,
            from_email=settings.ADMIN_EMAIL,
            verify_domain=settings.EMAIL_VERIFY_DOMAIN,
        )


@dataclass
class EmailMessage:
    """郵件訊息類別"""

    to_emails: List[str]
    subject: str
    body: str
    is_html: bool = False
    attachments: Optional[List[str]] = None

    def __post_init__(self):
        """驗證郵件訊息"""
        if not self.to_emails:
            raise ValueError("收件人不能為空")
        if not self.subject:
            raise ValueError("主題不能為空")
        if not self.body:
            raise ValueError("郵件內容不能為空")


class EmailSenderResult:
    """郵件發送結果類別"""

    def __init__(
        self, success: bool, message: str = "", error: Optional[Exception] = None
    ):
        self.success = success
        self.message = message
        self.error = error

    def __bool__(self):
        return self.success


class EmailSender(ABC):
    """抽象郵件發送器基類"""

    @abstractmethod
    def send_email(self, email_message: EmailMessage) -> EmailSenderResult:
        """發送郵件"""
        pass


class SMTPEmailSender(EmailSender):
    """SMTP 郵件發送器"""

    def __init__(self, config: EmailConfig):
        self.config = config

    def send_email(self, email_message: EmailMessage) -> EmailSenderResult:
        """
        發送郵件

        Args:
            email_message: 郵件訊息物件

        Returns:
            EmailSenderResult: 發送結果
        """
        try:
            # 建立郵件物件
            msg = self._create_message(email_message)

            # 添加附件
            if email_message.attachments:
                self._add_attachments(msg, email_message.attachments)

            # 發送郵件
            self._send_message(msg, email_message.to_emails)

            success_message = f"郵件已成功發送到: {', '.join(email_message.to_emails)}"
            logger.info(success_message)
            return EmailSenderResult(success=True, message=success_message)

        except Exception as e:
            error_message = f"發送郵件時發生錯誤: {str(e)}"
            logger.error(error_message)
            return EmailSenderResult(success=False, message=error_message, error=e)

    def _create_message(self, email_message: EmailMessage) -> MIMEMultipart:
        """建立郵件訊息物件"""
        msg = MIMEMultipart()
        msg["From"] = self.config.from_email
        msg["To"] = ", ".join(email_message.to_emails)
        msg["Subject"] = email_message.subject

        # 添加郵件內容
        content_type = "html" if email_message.is_html else "plain"
        msg.attach(MIMEText(email_message.body, content_type, "utf-8"))

        return msg

    def _add_attachments(self, msg: MIMEMultipart, attachments: List[str]) -> None:
        """添加附件"""
        for file_path in attachments:
            if not os.path.exists(file_path):
                logger.warning(f"附件檔案不存在: {file_path}")
                continue

            try:
                with open(file_path, "rb") as attachment_file:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment_file.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {os.path.basename(file_path)}",
                    )
                    msg.attach(part)
            except Exception as e:
                logger.error(f"添加附件時發生錯誤 {file_path}: {str(e)}")

    def _send_message(self, msg: MIMEMultipart, to_emails: List[str]) -> None:
        """發送郵件訊息"""
        with smtplib.SMTP(self.config.host, self.config.port) as server:
            if self.config.use_tls:
                server.starttls()
            server.login(self.config.username, self.config.password)
            text = msg.as_string()
            server.sendmail(self.config.from_email, to_emails, text)


class EmailTemplateService:
    """郵件範本服務"""

    @staticmethod
    def create_verification_email(email: str, token: str, domain: str) -> EmailMessage:
        """
        建立驗證郵件

        Args:
            email: 收件人信箱
            token: 驗證令牌
            domain: 網域名稱

        Returns:
            EmailMessage: 郵件訊息物件
        """
        verification_link = f"{domain}/auth/verifyEmail?token={token}"
        logger.info(f"建立驗證郵件: {email} -> {verification_link}")

        subject = "📩 請驗證您的 Email"

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4CAF50; text-align: center;">Email 驗證</h2>
                <p>親愛的用戶，</p>
                <p>感謝您註冊我們的服務！</p>
                <p>請點擊以下按鈕完成 Email 驗證：</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_link}" 
                       style="background-color: #4CAF50; color: white; padding: 15px 32px; 
                              text-decoration: none; display: inline-block; border-radius: 4px;
                              font-size: 16px; font-weight: bold;">
                        驗證 Email
                    </a>
                </div>
                <p>如果按鈕無法點擊，請複製以下連結到瀏覽器：</p>
                <p style="word-break: break-all; background-color: #f4f4f4; padding: 10px; border-radius: 4px;">
                    <a href="{verification_link}">{verification_link}</a>
                </p>
                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 4px; margin: 20px 0;">
                    <p style="margin: 0; font-weight: bold; color: #856404;">
                        ⚠️ 此驗證連結將在 30 分鐘後過期。
                    </p>
                </div>
                <p style="color: #666; font-size: 14px;">
                    如果您沒有註冊我們的服務，請忽略此郵件。
                </p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="text-align: center; color: #666; font-size: 12px;">
                    此郵件由系統自動發送，請勿回覆。
                </p>
            </div>
        </body>
        </html>
        """

        return EmailMessage(
            to_emails=[email], subject=subject, body=html_body, is_html=True
        )


class EmailService:
    """郵件服務主類別"""

    def __init__(self, sender: EmailSender, template_service: EmailTemplateService):
        self.sender = sender
        self.template_service = template_service

    def send_email(self, email_message: EmailMessage) -> EmailSenderResult:
        """發送郵件"""
        return self.sender.send_email(email_message)

    def send_verification_email(
        self, email: str, token: str, domain: str
    ) -> EmailSenderResult:
        """
        發送驗證郵件

        Args:
            email: 收件人信箱
            token: 驗證令牌
            domain: 網域名稱

        Returns:
            EmailSenderResult: 發送結果
        """
        email_message = self.template_service.create_verification_email(
            email, token, domain
        )
        return self.send_email(email_message)

    def send_welcome_email(self, email: str, username: str) -> EmailSenderResult:
        """
        發送歡迎郵件

        Args:
            email: 收件人信箱
            username: 用戶名稱

        Returns:
            EmailSenderResult: 發送結果
        """
        subject = "🎉 歡迎加入我們的服務"
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #4CAF50; text-align: center;">歡迎 {username}！</h1>
                <p>感謝您加入我們的服務！</p>
                <p>您已成功完成註冊，現在可以開始使用所有功能。</p>
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #495057; margin-top: 0;">主要功能：</h3>
                    <ul style="color: #6c757d;">
                        <li>功能 1</li>
                        <li>功能 2</li>
                        <li>功能 3</li>
                    </ul>
                </div>
                <p>如有任何問題，歡迎隨時聯繫我們的客服團隊。</p>
                <p>謝謝！</p>
            </div>
        </body>
        </html>
        """

        email_message = EmailMessage(
            to_emails=[email], subject=subject, body=html_body, is_html=True
        )

        return self.send_email(email_message)


class EmailForgotPasswordService:
    """郵件服務寄送重設密碼"""

    def __init__(self, sender: EmailSender, template_service: EmailTemplateService):
        self.sender = sender
        self.template_service = template_service

    def send_email(self, email_message: EmailMessage) -> EmailSenderResult:
        """發送郵件"""
        return self.sender.send_email(email_message)

    def send_password_email(
        self, email: str, token: str, domain: str
    ) -> EmailSenderResult:
        """
        發送驗證郵件

        Args:
            email: 收件人信箱
            token: 驗證令牌
            domain: 網域名稱

        Returns:
            EmailSenderResult: 發送結果
        """
        email_message = self.template_service.create_verification_email(
            email, token, domain
        )
        return self.send_email(email_message)

    def send_welcome_email(self, email: str, username: str) -> EmailSenderResult:
        """
        發送歡迎郵件

        Args:
            email: 收件人信箱
            username: 用戶名稱

        Returns:
            EmailSenderResult: 發送結果
        """
        subject = "🎉 重設密碼-多媒體英語教學"
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <p>感謝您加入我們的服務！</p>
                <p>您已成功完成註冊，現在可以開始使用所有功能。</p>
                <p>如有任何問題，歡迎隨時聯繫我們的客服團隊。</p>
                <p>謝謝！</p>
            </div>
        </body>
        </html>
        """

        email_message = EmailMessage(
            to_emails=[email], subject=subject, body=html_body, is_html=True
        )

        return self.send_email(email_message)


def create_email_service() -> EmailService:
    """建立郵件服務實例"""
    config = EmailConfig.from_settings()
    sender = SMTPEmailSender(config)
    template_service = EmailTemplateService()
    return EmailService(sender, template_service)


def main():
    """主函式 - 使用範例"""
    try:
        # 建立郵件服務
        email_service = create_email_service()

        # 測試收件人
        test_email = "dino5168@gmail.com"

        # 範例 1: 發送驗證郵件
        print("發送驗證郵件...")
        result = email_service.send_verification_email(
            email=test_email, token="token123456", domain="http://localhost:3000"
        )
        print(f"驗證郵件發送結果: {result.success} - {result.message}")

        # 範例 2: 發送歡迎郵件
        print("\n發送歡迎郵件...")
        result = email_service.send_welcome_email(email=test_email, username="測試用戶")
        print(f"歡迎郵件發送結果: {result.success} - {result.message}")

        # 範例 3: 發送自定義郵件
        print("\n發送自定義郵件...")
        custom_email = EmailMessage(
            to_emails=[test_email],
            subject="自定義郵件測試",
            body="這是一封自定義的測試郵件。",
            is_html=False,
        )
        result = email_service.send_email(custom_email)
        print(f"自定義郵件發送結果: {result.success} - {result.message}")

    except Exception as e:
        logger.error(f"主程式執行錯誤: {str(e)}")


if __name__ == "__main__":
    main()
