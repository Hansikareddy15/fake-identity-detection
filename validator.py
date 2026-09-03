from datetime import datetime
import re

print("SIH DOCUMENT VALIDATION MODULE")
print("--------------------------------")


# ==========================================
# DOCUMENT DATA
# ==========================================

document = {
    "name": "RAHUL KUMAR",
    "passport_number": "A1234567",
    "nationality": "IND",
    "dob": "12-04-2002",
    "gender": "M",
    "expiry": "15-08-2030"
}


# ==========================================
# VALIDATION FUNCTIONS
# ==========================================

def check_missing_fields(document):

    required_fields = [
        "name",
        "passport_number",
        "nationality",
        "dob",
        "gender",
        "expiry"
    ]

    missing_fields = []

    for field in required_fields:

        if not document.get(field):
            missing_fields.append(field)

    return missing_fields


def validate_date(date_string):

    try:

        datetime.strptime(date_string, "%d-%m-%Y")
        return True

    except (ValueError, TypeError):

        return False


def check_expiry(expiry_date):

    try:

        expiry_date = datetime.strptime(
            expiry_date,
            "%d-%m-%Y"
        )

        today = datetime.today()

        return expiry_date >= today

    except (ValueError, TypeError):

        return False


# ==========================================
# NATIONALITY VALIDATION
# ==========================================

valid_nationalities = {
    "IND": "India",
    "USA": "United States",
    "GBR": "United Kingdom",
    "AUS": "Australia",
    "CAN": "Canada",
    "JPN": "Japan",
    "DEU": "Germany",
    "FRA": "France"
}


def validate_nationality(nationality):

    return nationality in valid_nationalities


# ==========================================
# PASSPORT NUMBER VALIDATION
# ==========================================

def validate_passport_number(passport_number):

    if not passport_number:
        return False

    pattern = r"^[A-Z][0-9]{7}$"

    return re.match(pattern, passport_number) is not None


# ==========================================
# GENDER VALIDATION
# ==========================================

def validate_gender(gender):

    valid_genders = ["M", "F", "X"]

    return gender in valid_genders


# ==========================================
# RUN VALIDATION
# ==========================================

issues = []

score = 100


# ==========================================
# 1. MISSING FIELDS
# ==========================================

missing_fields = check_missing_fields(document)

if missing_fields:

    for field in missing_fields:

        issues.append("Missing field: " + field)

        score -= 15


# ==========================================
# 2. DATE OF BIRTH
# ==========================================

if not validate_date(document.get("dob")):

    issues.append("Invalid date of birth")

    score -= 15


# ==========================================
# 3. EXPIRY DATE
# ==========================================

if not validate_date(document.get("expiry")):

    issues.append("Invalid expiry date format")

    score -= 15

else:

    if not check_expiry(document.get("expiry")):

        issues.append("Passport has expired")

        score -= 25


# ==========================================
# 4. NATIONALITY
# ==========================================

if not validate_nationality(
    document.get("nationality")
):

    issues.append("Invalid nationality code")

    score -= 15


# ==========================================
# 5. PASSPORT NUMBER
# ==========================================

if not validate_passport_number(
    document.get("passport_number")
):

    issues.append("Invalid passport number format")

    score -= 20


# ==========================================
# 6. GENDER
# ==========================================

if not validate_gender(
    document.get("gender")
):

    issues.append("Invalid gender value")

    score -= 10


# ==========================================
# KEEP SCORE BETWEEN 0 AND 100
# ==========================================

if score < 0:

    score = 0


# ==========================================
# FINAL STATUS
# ==========================================

if score >= 80:

    status = "VALID"

elif score >= 50:

    status = "SUSPICIOUS"

else:

    status = "INVALID"


# ==========================================
# DISPLAY REPORT
# ==========================================

print("\nDOCUMENT VALIDATION REPORT")
print("============================")

print("Name:", document.get("name"))

print("Passport Number:",
      document.get("passport_number"))

print("Nationality:",
      document.get("nationality"))

print("Date of Birth:",
      document.get("dob"))

print("Gender:",
      document.get("gender"))

print("Expiry Date:",
      document.get("expiry"))


print("\nVALIDATION SCORE")
print("================")

print(str(score) + "/100")


print("\nFINAL STATUS")
print("============")

print(status)


# ==========================================
# DISPLAY ISSUES
# ==========================================

if issues:

    print("\nISSUES DETECTED")
    print("---------------")

    for number, issue in enumerate(
        issues,
        start=1
    ):

        print(str(number) + ".", issue)

else:

    print("\nNo validation issues detected.")


print("\n--------------------------------")
print("Validation completed.")
print("--------------------------------")