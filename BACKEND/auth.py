from BACKEND.database import Database
import hashlib
import hmac
import os
import re
import sqlite3

class AuthManager(Database):
    _ITERATIONS = 310_000
    _HASH_ALG = "sha256"
    _SALT_BYTES = 32

    # only uni.edu.ge emails
    _EMAIL_PATTERN = re.compile(
        r"^[a-zA-Z0-9._%+\-]+@uni\.edu\.ge$"
    )

    def _validate_email(self, email: str) -> bool:
        if not email or not isinstance(email, str):
            return False

        email = email.strip().lower()
        return bool(self._EMAIL_PATTERN.fullmatch(email))

    def _hash_password(self, password: str) -> tuple[str, str]:
        if not password or not isinstance(password, str):
            raise ValueError("Password must be a non-empty string.")

        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters.")

        salt = os.urandom(self._SALT_BYTES)

        password_hash = hashlib.pbkdf2_hmac(
            self._HASH_ALG,
            password.encode("utf-8"),
            salt,
            self._ITERATIONS
        )

        return salt.hex(), password_hash.hex()

    def _verify_password(
        self,
        password: str,
        salt_hex: str,
        saved_hash: str
    ) -> bool:
        if not password or not isinstance(password, str):
            return False

        try:
            salt = bytes.fromhex(salt_hex)
        except ValueError:
            return False

        candidate_hash = hashlib.pbkdf2_hmac(
            self._HASH_ALG,
            password.encode("utf-8"),
            salt,
            self._ITERATIONS
        )

        return hmac.compare_digest(candidate_hash.hex(), saved_hash)

    def register(self, full_name, email, password):
        if not full_name or not isinstance(full_name, str):
            return {
                "ok": False,
                "message": "Full name is required."
            }

        if not email or not isinstance(email, str):
            return {
                "ok": False,
                "message": "Email is required."
            }

        if not password or not isinstance(password, str):
            return {
                "ok": False,
                "message": "Password is required."
            }

        full_name = full_name.strip()
        email = email.strip().lower()

        if not full_name:
            return {
                "ok": False,
                "message": "Full name is required."
            }

        if not self._validate_email(email):
            return {
                "ok": False,
                "message": "Please use your university email: @uni.edu.ge"
            }

        try:
            password_salt, password_hash = self._hash_password(password)

        except ValueError as error:
            return {
                "ok": False,
                "message": str(error)
            }

        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users 
                    (full_name, email, password_salt, password_hash)
                    VALUES (?, ?, ?, ?)
                """, (
                    full_name,
                    email,
                    password_salt,
                    password_hash
                ))

                conn.commit()

                return {
                    "ok": True,
                    "message": "Account created successfully.",
                    "user_id": cursor.lastrowid
                }

        except sqlite3.IntegrityError:
            return {
                "ok": False,
                "message": "An account with that email already exists."
            }

    def login(self, email: str, password: str) -> dict:
        generic_error = {
            "ok": False,
            "message": "Invalid email or password."
        }

        if not email or not isinstance(email, str):
            return generic_error

        if not password or not isinstance(password, str):
            return generic_error

        email = email.strip().lower()

        if not self._validate_email(email):
            return generic_error

        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, full_name, email, password_salt, password_hash
                FROM users
                WHERE email = ?
            """, (email,))

            row = cursor.fetchone()

        if row is None:
            self._verify_password(password, "00" * 32, "00" * 32)
            return generic_error

        password_is_correct = self._verify_password(
            password,
            row["password_salt"],
            row["password_hash"]
        )

        if not password_is_correct:
            return generic_error

        return {
            "ok": True,
            "message": "Login successful.",
            "user": {
                "id": row["id"],
                "full_name": row["full_name"],
                "email": row["email"]
            }
        }