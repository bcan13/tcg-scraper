import yagmail
import os
from pathlib import Path
import dotenv
import random
from typing import Optional, List, Union
from dataclasses import dataclass


@dataclass
class EmailConfig:
    """Configuration for email client settings."""

    email_user: str
    email_password: str
    templates_dir: Path
    our_name: str
    cc_email: Optional[str] = None


@dataclass
class EmailTemplate:
    """Container for email template content."""

    body: str
    subject: str
    signature_path: Path
    brochure_path: Path


class TemplateManager:
    """Handles loading and managing email templates."""

    def __init__(self, templates_dir: Path):
        """Initialize template manager with templates directory."""
        self.templates_dir = templates_dir

    def read_template_file(self, filename: str) -> str:
        """Read template file content.

        Args:
            filename: Name of the template file to read

        Returns:
            Content of the template file

        Raises:
            FileNotFoundError: If template file doesn't exist
            IOError: If template file can't be read
        """
        try:
            with open(self.templates_dir / filename, "r") as file:
                return file.read()
        except Exception as e:
            raise IOError(f"Failed to read template {filename}: {e}")

    def load_templates(self) -> EmailTemplate:
        """Load all required email templates.

        Returns:
            EmailTemplate object containing all loaded templates

        Raises:
            IOError: If any template fails to load
        """
        try:
            return EmailTemplate(
                body=self.read_template_file("cold_outreach.txt"),
                subject=self.read_template_file("subject.txt"),
                signature_path=self.templates_dir / "signature.jpg",
                brochure_path=self.templates_dir / "brochure.pdf",
            )
        except Exception as e:
            raise IOError(f"Failed to load templates: {e}")


class EmailContentBuilder:
    """Handles creation and formatting of email content."""

    def __init__(self, template: EmailTemplate):
        """Initialize content builder with templates."""
        self.template = template

    def create_subject(self, company_name: str) -> str:
        """Create email subject line.

        Args:
            company_name: Name of the target company

        Returns:
            Formatted subject line
        """
        try:
            return self.template.subject.format(company_name=company_name)
        except Exception as e:
            raise ValueError(f"Failed to create subject: {e}")

    def create_body(
        self, recipient_name: str, our_name: str, company_name: str
    ) -> List[Union[str, yagmail.inline]]:
        """Create email body with signature.

        Args:
            recipient_name: Name of the recipient
            our_name: Sender's name
            company_name: Target company name

        Returns:
            List containing body text and inline signature

        Raises:
            ValueError: If body creation fails
        """
        try:
            body = self.template.body.format(
                recipient_name=recipient_name,
                our_name=our_name,
                company_name=company_name,
            )
            signature = yagmail.inline(str(self.template.signature_path))
            return [body, signature]
        except Exception as e:
            raise ValueError(f"Failed to create body: {e}")


class EmailClient:
    """Main email client for sending outreach emails."""

    def __init__(self, config: EmailConfig):
        """Initialize email client with configuration.

        Args:
            config: EmailConfig object containing all necessary settings
        """
        self.config = config
        self.template_manager = TemplateManager(config.templates_dir)
        self.templates = self.template_manager.load_templates()
        self.content_builder = EmailContentBuilder(self.templates)
        self.session = self._create_session()

    @staticmethod
    def from_env(
        our_name: str, env_path: Optional[str] = None
    ) -> "EmailClient":
        """Create EmailClient instance from environment variables.

        Args:
            our_name: Sender's name
            env_path: Optional path to .env file

        Returns:
            Configured EmailClient instance
        """
        if env_path:
            dotenv.load_dotenv(env_path)
        else:
            dotenv.load_dotenv()

        config = EmailConfig(
            email_user=os.getenv("EMAIL_USER", ""),
            email_password=os.getenv("EMAIL_PASS", ""),
            templates_dir=Path(__file__).parent.parent.parent / "templates",
            our_name=our_name,
            cc_email=os.getenv("CC_EMAIL"),
        )
        return EmailClient(config)

    def _create_session(self) -> Optional[yagmail.SMTP]:
        """Create authenticated SMTP session.

        Returns:
            Authenticated SMTP session or None if authentication fails
        """
        try:
            session = yagmail.SMTP(
                user=self.config.email_user,
                password=self.config.email_password,
            )
            print("Authenticated the email sender.")
            return session
        except Exception as e:
            print(f"Failed to authenticate the email sender: {e}")
            return None

    def send_email(
        self, recipient_email: str, recipient_name: str, company_name: str
    ) -> bool:
        """Send outreach email to recipient.

        Args:
            recipient_email: Recipient's email address
            recipient_name: Recipient's name
            company_name: Target company name

        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.session:
            print("Failed to send email: No authenticated session.")
            return False

        try:
            body = self.content_builder.create_body(
                recipient_name=recipient_name,
                our_name=self.config.our_name,
                company_name=company_name,
            )
            subject = self.content_builder.create_subject(
                company_name=company_name
            )

            email_args = {
                "to": recipient_email,
                "subject": subject,
                "contents": body,
                "attachments": str(self.templates.brochure_path),
            }

            if self.config.cc_email:
                email_args["cc"] = self.config.cc_email

            self.session.send(**email_args)
            print(
                f"Email sent successfully to {recipient_name} from {company_name} ({recipient_email})!"
            )
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
