import aiohttp
import asyncio
import os
import dotenv

dotenv.load_dotenv(".env")


MJ_APIKEY_PUBLIC = os.getenv("MAILJET_API_KEY")
MJ_APIKEY_PRIVATE = os.getenv("MAILJET_SECRET_KEY")

URL = "https://api.mailjet.com/v3.1/send"

PAYLOAD = {
    "Messages": [
        {
            "From": {
                "Email": "pilot@tugberk.cloud",
                "Name": "Mailjet Pilot"
            },
            "To": [
                {
                    "Email": "tugberkozdemir@gmail.com",
                    "Name": "passenger 1"
                }
            ],
            "Subject": "Your email flight plan!",
            "TextPart": "Dear passenger 1, welcome to Mailjet! May the delivery force be with you!",
            "HTMLPart": (
                '<h3>Dear passenger 1, welcome to '
                '<a href="https://www.mailjet.com/">Mailjet</a>!</h3>'
                "<br />May the delivery force be with you!"
            )
        }
    ]
}

async def send_email():
    auth = aiohttp.BasicAuth(MJ_APIKEY_PUBLIC, MJ_APIKEY_PRIVATE)

    async with aiohttp.ClientSession(auth=auth) as session:
        async with session.post(URL, json=PAYLOAD) as resp:
            status = resp.status
            data = await resp.json()

            print("Status:", status)
            print("Response:", data)

            if status >= 400:
                raise Exception(f"Mailjet error {status}: {data}")

async def main():
    await send_email()

if __name__ == "__main__":
    asyncio.run(main())