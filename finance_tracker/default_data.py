"""
This model contains default data
"""

account = [
    {"name": "Me"},
]

category = [
    {"name": item}
    for item
    in (
        "Home Expenses",
        "Transportation",
        "Health",
        "Gifts",
        "Subscriptions",
        "Daily Living",
        "Entertainment",
        "Savings",
        "Obligations",
        "Other",
    )
]

subcategory = {
    "Home Expenses": [
        {"name": item}
        for item
        in (
            "Mortgage/Rent",
            "Home/Rental Insurance",
            "Electricity",
            "Gas/Oil",
            "Water/Sewer/Trash",
            "Phone",
            "Cable/Satellite",
            "Internet",
            "Furnishings/Appliances",
            "Lawn/Garden",
            "Maintenance/Supplies",
            "Improvements",
            "Other",
        )
    ],

    "Transportation": [
        {"name": item}
        for item
        in (
            "Vehicle Payments",
            "Auto Insurance",
            "Fuel",
            "Bus/Taxi/Train Fare",
            "Repairs",
            "Registration/License",
            "Other",
        )
    ],

    "Health": [
        {"name": item}
        for item
        in (
            "Health Insurance",
            "Doctor/Dentist",
            "Medicine/Drugs",
            "Health Club Dues",
            "Life Insurance",
            "Veterinarian/Pet Care",
            "Other",
        )
    ],

    "Gifts": [
        {"name": item}
        for item
        in (
            "Gifts Given",
            "Charitable Donations",
            "Religious Donations",
            "Other",
        )
    ],

    "Subscriptions": [
        {"name": item}
        for item
        in (
            "Newspaper",
            "Magazines",
            "Dues/Memberships",
            "Other",
        )
    ],

    "Daily Living": [
        {"name": item}
        for item
        in (
            "Groceries",
            "Personal Supplies",
            "Clothing",
            "Cleaning",
            "Education/Lessons",
            "Dining/Eating Out",
            "Salon/Barber",
            "Pet Food",
            "Other",
        )
    ],

    "Entertainment": [
        {"name": item}
        for item
        in (
            "Videos/DVDs",
            "Music",
            "Games",
            "Rentals",
            "Movies/Theater",
            "Concerts/Plays",
            "Books",
            "Hobbies",
            "Film/Photos",
            "Sports",
            "Outdoor Recreation",
            "Toys/Gadgets",
            "Vacation/Travel",
            "Other",
        )
    ],

    "Savings": [
        {"name": item}
        for item
        in (
            "Emergency Fund",
            "Transfer to Savings",
            "Retirement (401k, IRA)",
            "Investments",
            "Education",
            "Other",
        )
    ],

    "Obligations": [
        {"name": item}
        for item
        in (
            "Student Loan",
            "Other Loan",
            "Credit Cards",
            "Alimony/Child Support",
            "Federal Taxes",
            "State/Local Taxes",
            "Other",
        )
    ],

    "Other": [
        {"name": item}
        for item
        in (
            "Bank Fees",
            "Postage",
            "Other",
        )
    ],
}
