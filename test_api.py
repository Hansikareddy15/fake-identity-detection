import requests

URL = "http://127.0.0.1:5000/validate"


# ==========================================
# FUNCTION TO CREATE 44-CHARACTER MRZ
# ==========================================

def make_mrz(line1, line2):

    line1 = line1.ljust(44, "<")
    line2 = line2.ljust(44, "<")

    return line1[:44] + "\n" + line2[:44]


# ==========================================
# DOCUMENT 1 - VALID
# ==========================================

document1 = {
    "name": "RAHUL KUMAR",
    "passport_number": "A1234567",
    "nationality": "IND",
    "dob": "12-04-2002",
    "gender": "M",
    "expiry": "15-08-2030",

    "mrz": make_mrz(
        "P<INDRAHUL<KUMAR",
        "A1234567<6IND0204129M3008155"
    )
}


# ==========================================
# DOCUMENT 2 - INVALID NATIONALITY
# ==========================================

document2 = {
    "name": "ARJUN REDDY",
    "passport_number": "B7654321",
    "nationality": "XYZ",
    "dob": "10-05-2001",
    "gender": "M",
    "expiry": "20-10-2030",

    "mrz": make_mrz(
        "P<INDARJUN<REDDY",
        "B7654321<1IND0105101M3010208"
    )
}


# ==========================================
# DOCUMENT 3 - EXPIRED DOCUMENT
# ==========================================

document3 = {
    "name": "PRIYA SHARMA",
    "passport_number": "C9876543",
    "nationality": "IND",
    "dob": "25-08-2000",
    "gender": "F",
    "expiry": "15-08-2020",

    "mrz": make_mrz(
        "P<INDPRIYA<SHARMA",
        "C9876543<8IND0008257F2008158"
    )
}


# ==========================================
# TEST FUNCTION
# ==========================================

def test_document(document, number):

    print("\n==============================")
    print("TEST DOCUMENT", number)
    print("==============================")

    try:

        response = requests.post(
            URL,
            json=document
        )

        print("Status Code:", response.status_code)
        print("Result:")
        print(response.json())

    except requests.exceptions.ConnectionError:

        print("ERROR: Flask server is not running.")
        print("Start app.py first.")


# ==========================================
# RUN ALL TESTS
# ==========================================

test_document(document1, 1)
test_document(document2, 2)
test_document(document3, 3)