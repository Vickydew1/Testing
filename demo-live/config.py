# Live demo — intentionally hardcoded credentials for the checkout service
DB_PASSWORD = "ChangeMe123!"

# Stripe/Slack tokens dropped here - GitHub's own push protection blocks
# them as too realistic (same reason secrets_test.py has blank Slack/
# Stripe sections). AWS-shaped + generic high-entropy still pass through
# and TruffleHog still flags them.
AWS_ACCESS_KEY_ID = "AKIAZ3F5G8H1J4K7M2N9"
AWS_SECRET_ACCESS_KEY = "kL9pQ2rS5tU8vW1xY4zA7bC0dE3fG6hJ9mN2oP5q"
GENERIC_API_TOKEN = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2"
