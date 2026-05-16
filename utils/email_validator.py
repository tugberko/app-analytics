import re
import asyncio
import dns.resolver


class EmailValidator:

    def __init__(self):
        self.email_regex = re.compile(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )

        self.disposable_domains = {
            "mailinator.com",
            "tempmail.com",
            "10minutemail.com",
            "guerrillamail.com",
            "yopmail.com",
        }

        # Trusted domains: skip MX lookup entirely
        self.trusted_domains = {
            "gmail.com",
            "googlemail.com",
            "outlook.com",
            "hotmail.com",
            "live.com",
            "yahoo.com",
            "icloud.com",
            "aol.com",
        }

    def _get_domain(self, email: str):
        try:
            return email.split("@")[1].lower()
        except Exception:
            return None

    def check_if_regex_match(self, email: str) -> bool:
        return bool(self.email_regex.match(email or ""))

    def check_if_disposable_email(self, email: str) -> bool:
        domain = self._get_domain(email)
        if not domain:
            return False
        return domain in self.disposable_domains

    def _is_trusted_domain(self, domain: str) -> bool:
        return domain in self.trusted_domains

    async def check_if_mx_record_exists(self, email: str) -> bool:
        domain = self._get_domain(email)
        if not domain:
            return False

        # 🚀 Skip DNS for trusted providers
        if self._is_trusted_domain(domain):
            return True

        def _lookup():
            try:
                dns.resolver.resolve(domain, "MX")
                return True
            except Exception:
                return False

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _lookup)

    async def check_if_valid_email(self, email: str) -> bool:
        if not self.check_if_regex_match(email):
            return False

        if self.check_if_disposable_email(email):
            return False

        return await self.check_if_mx_record_exists(email)