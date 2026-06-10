"""Create or promote an admin user (first-admin bootstrap, Admin Slice 1 A2).

There is no public signup, so the first superadmin is created with this script.
Run from the project root:

    python -m scripts.create_admin --email you@example.com --role superadmin

The password is read interactively (never passed on the command line, so it
won't land in your shell history).
"""

from __future__ import annotations

import argparse
import asyncio
import getpass

from sqlalchemy import select

from core.db import AsyncSessionLocal
from core.models.auth import User
from core.security import hash_password


async def _run(email: str, display_name: str | None, role: str) -> None:
    email = email.strip().lower()
    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        raise SystemExit("Passwords do not match.")
    if len(password) < 8:
        raise SystemExit("Use a password of at least 8 characters.")

    async with AsyncSessionLocal() as db:
        existing = (
            await db.execute(select(User).where(User.email == email))
        ).scalar_one_or_none()
        if existing is not None:
            existing.password_hash = hash_password(password)
            existing.role = role
            existing.is_active = True
            if display_name:
                existing.display_name = display_name
            action = "Updated"
        else:
            db.add(
                User(
                    email=email,
                    display_name=display_name,
                    password_hash=hash_password(password),
                    role=role,
                    is_active=True,
                )
            )
            action = "Created"
        await db.commit()
    print(f"{action} {role}: {email}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or promote an admin user.")
    parser.add_argument("--email", required=True)
    parser.add_argument("--display-name", default=None)
    parser.add_argument("--role", default="superadmin", choices=["admin", "superadmin"])
    args = parser.parse_args()
    asyncio.run(_run(args.email, args.display_name, args.role))


if __name__ == "__main__":
    main()
