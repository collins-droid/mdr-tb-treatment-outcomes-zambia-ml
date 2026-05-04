"""Frontend configuration and option lists."""

from __future__ import annotations

import os


DEFAULT_API_URL = os.getenv("MDRTB_API_URL", "http://localhost:8000")
LOGO_PATH = "frontend/assets/Proudly-Zambia-Logo_017500741_6736.webp"

AGE_GROUPS = ["0-15", "16-25", "26-35", "36-45", "Above45"]
GENDERS = ["Female", "Male"]
HIV_STATUSES = ["Positive", "Negative", "Unknown"]
REGISTRATION_GROUPS = ["New", "Relapse", "After loss to FU", "Transfer in", "Other"]
DRTB_TYPES = ["RR-TB", "MDR-TB", "IR-TB", "XDR-TB"]
DISTRICTS = [
    "Kabwe",
    "Kapiri Mposhi",
    "Chibombo",
    "Chisamba",
    "Mumbwa",
    "Mkushi",
    "Serenje",
    "Chitambo",
    "Other",
]

VALIDITY_WARNING = (
    "Research prototype only. Outputs are for review, testing, and model-development planning. "
    "Do not use for clinical decisions until externally validated and approved."
)
