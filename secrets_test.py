# 🚨 Intentionally vulnerable file for testing Secret Scanning
# DO NOT USE THESE KEYS IN PRODUCTION

# AWS - matches AKIA + 16 random chars
AWS_ACCESS_KEY_ID = "AKIAQ7XVQH3MFJYV8KZN"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYzEXAMPLEKEY"

# GitHub PAT - matches ghp_ + exactly 36 chars
GITHUB_TOKEN = "ghp_aBcD1234EfGh5678IjKl9012MnOp3456QrSt"

# Slack - matches xoxb-/xoxp- + numeric segments


# Stripe - matches sk_live_ + 24 chars


# Generic high-entropy string TruffleHog also flags
API_KEY = "f8b3c7a9d2e1f4b6c8a0e3d5f7b9c2a4e6d8f0b2c4a6e8d0f2b4c6a8e0d2f4b6"

print("This file contains fake hardcoded secrets for testing only.")
