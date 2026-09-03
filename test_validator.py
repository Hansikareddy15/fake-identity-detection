from document_validator import validate_document


# Sample document
document = {
    "name": "RAHUL KUMAR",
    "passport_number": "A1234567",
    "nationality": "IND",
    "dob": "12-04-2002",
    "gender": "M",
    "expiry": "15-08-2030"
}


# Send document to Module 2
result = validate_document(document)


# Display result
print("DOCUMENT VALIDATION RESULT")
print("----------------------------")

print("Status:", result["status"])

print("Score:", result["score"], "/100")

print("Issues:")

if result["issues"]:

    for issue in result["issues"]:
        print("-", issue)

else:

    print("No issues detected.")