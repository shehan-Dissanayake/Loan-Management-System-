"""
The knowledge base for the Rohana Credit RAG chatbot.
Each entry in DOCUMENTS is a standalone chunk of knowledge.
Add more entries here as the system grows.
"""

DOCUMENTS = [
    # --- System overview ---
    {
        "id": "overview_1",
        "text": """
Rohana Credit is a credit loan management system built for a small lending business
that provides short-term cash loans to shop owners. The lender visits shops in person
on weekdays to collect daily installment payments. The system manages customers, loans,
payments, and reports. It is accessible as a web app on desktop and as a PWA (Progressive
Web App) installed on an Android phone for field use.
        """.strip(),
        "topic": "overview"
    },
    {
        "id": "overview_2",
        "text": """
The system has the following main sections: Dashboard, Customers, Loans, Reports, and
Assistant. The Dashboard shows a summary of active loans, today's collection target,
total outstanding balance, and overdue loans. The system supports dark and light themes
which can be toggled from the top right corner.
        """.strip(),
        "topic": "overview"
    },

    # --- Customers ---
    {
        "id": "customers_1",
        "text": """
Customers in Rohana Credit are shops or businesses, not individual consumers. Each
customer record stores: shop name (required), phone number (required), and optionally
owner name, address, NIC, and location. To add a new customer, go to the Customers
page and click the Add Customer button. Fill in the shop name and phone number at
minimum, then click Save.
        """.strip(),
        "topic": "customers"
    },
    {
        "id": "customers_2",
        "text": """
A customer (shop) can only have one active loan at a time. If you try to create a
second loan for a customer who already has an active loan, the system will show an
error message. You must wait until the current loan is completed or manually mark it
as completed before creating a new loan for that customer.
        """.strip(),
        "topic": "customers"
    },

    # --- Loans ---
    {
        "id": "loans_1",
        "text": """
To create a loan, go to the Loans page and click New Loan. Select the shop from the
dropdown, enter the principal amount (the cash amount given to the shop), and click
Create. The system automatically calculates the interest, total payable, daily
installment, and due date. No approval step is needed — the lender decides on the spot.
        """.strip(),
        "topic": "loans"
    },
    {
        "id": "loans_2",
        "text": """
Loan interest is calculated as a flat 20% of the principal (which equals 6.67% per
month times 3 months). For example, if the principal is Rs 10,000, the interest is
Rs 2,000 and the total payable is Rs 12,000. This interest is fixed at the time the
loan is created and never changes, even if the loan is paid early.
        """.strip(),
        "topic": "loans"
    },
    {
        "id": "loans_3",
        "text": """
Every loan has a 60-day term. The due date is automatically set to 60 days after the
disbursement date. The daily installment is calculated as total payable divided by 60.
For a Rs 10,000 loan with Rs 12,000 total payable, the daily installment is Rs 200.
The lender visits each shop on weekdays to collect this daily installment.
        """.strip(),
        "topic": "loans"
    },
    {
        "id": "loans_4",
        "text": """
Loan statuses: active means the loan is ongoing and payments are being collected.
completed means the loan has been fully paid off (balance reached zero). overdue means
the 60-day due date has passed but the balance is not yet zero. There is no automatic
penalty for overdue loans — the lender handles these case by case. A loan can be
settled early but still requires the full total payable amount including all interest.
        """.strip(),
        "topic": "loans"
    },

    # --- Payments ---
    {
        "id": "payments_1",
        "text": """
To record a payment, click on a shop name from the Loans page or Dashboard route list
to open the Loan Detail page. Enter the amount collected today in the Record Payment
form and click Record Payment. The date defaults to today but can be changed to backdate
a payment if needed. The balance due updates immediately after recording.
        """.strip(),
        "topic": "payments"
    },
    {
        "id": "payments_2",
        "text": """
The system tracks arrears — missed or short payments. Arrears count is the number of
weekdays where the amount collected was less than the daily installment amount. Arrears
amount is the total shortfall in rupees (arrears count multiplied by the installment).
For example, if the daily installment is Rs 200 and a shop paid Rs 100 on one day and
nothing on another day, arrears count is 2 and arrears amount is Rs 300 (100 + 200).
        """.strip(),
        "topic": "payments"
    },
    {
        "id": "payments_3",
        "text": """
Once a loan's balance reaches zero, it is automatically marked as completed. No further
payments can be recorded on a completed loan. If you try to record a payment on a
completed loan, the system will show an error: Loan is already completed — cannot record
further payments. To give a shop a new loan after completing one, create a new loan from
the Loans page.
        """.strip(),
        "topic": "payments"
    },

    # --- Receipt printing ---
    {
        "id": "printing_1",
        "text": """
Rohana Credit supports Bluetooth receipt printing using a portable 58mm thermal printer.
To print a receipt, open the Loan Detail page for the shop, click Connect Printer to pair
the Bluetooth printer, then record a payment and click Print Last Receipt. The receipt
shows: Rohana Credit header, customer shop name, loan number, disbursement date, due date,
loan total amount, amount paid today, and remaining balance.
        """.strip(),
        "topic": "printing"
    },
    {
        "id": "printing_2",
        "text": """
Bluetooth printing requires Chrome browser on Android. It does not work on iPhone or
Safari because Apple has not implemented the Web Bluetooth API. The printer must be
nearby and powered on when connecting. If the printer does not appear in the device list,
make sure Bluetooth is enabled on the phone and the printer is in pairing mode.
        """.strip(),
        "topic": "printing"
    },

    # --- Reports ---
    {
        "id": "reports_1",
        "text": """
The Reports section has six reports. Today's Route shows all shops with active loans
that need to be visited today, with their balance, installment amount, days remaining,
and whether they have already been visited. Daily Collection shows all payments collected
on a specific date with the total amount. Outstanding Loans shows all active loans with
balance remaining and days left until due date.
        """.strip(),
        "topic": "reports"
    },
    {
        "id": "reports_2",
        "text": """
Overdue Loans report shows loans that have passed their 60-day due date but still have
a balance remaining. Customer History shows the full loan and payment history for a
specific shop. Cash Flow Summary shows total principal disbursed versus total payments
collected over a date range, and calculates the net amount, which represents the
lender's profit minus outstanding loans.
        """.strip(),
        "topic": "reports"
    },

    # --- Loan management best practices ---
    {
        "id": "bestpractice_1",
        "text": """
Best practice for daily collection: start each day by checking the Today's Route report
to see which shops need visiting. After visiting each shop and collecting payment, record
it immediately on the Loan Detail page and print a receipt for the shop owner. At the end
of the day, check the Daily Collection report to verify all collections are recorded.
        """.strip(),
        "topic": "best_practices"
    },
    {
        "id": "bestpractice_2",
        "text": """
Best practice for managing overdue loans: check the Overdue Loans report weekly. Contact
overdue shops and arrange a payment plan. You can backdate payments using the date field
on the Loan Detail page if a shop pays for missed days. There is no automatic penalty
interest — the lender decides how to handle overdue cases individually.
        """.strip(),
        "topic": "best_practices"
    },
    {
        "id": "bestpractice_3",
        "text": """
When giving a new loan, consider the shop's payment history. If a shop has many arrears
on a previous loan, review their Customer History report before issuing a new loan.
The Cash Flow Summary report is useful for understanding the overall financial health
of the lending business — compare total disbursed against total collected to see
how much of the lent money has been recovered.
        """.strip(),
        "topic": "best_practices"
    },

    # --- Technical / login ---
    {
        "id": "technical_1",
        "text": """
To log in to Rohana Credit, go to the web app URL and enter your username and password.
The system uses JWT authentication with a 7-day token — you will stay logged in for 7
days without needing to re-enter your password. To log out, click the Log Out button at
the bottom of the left sidebar. The app can be installed on an Android phone home screen
as a PWA by opening it in Chrome and selecting Add to Home Screen.
        """.strip(),
        "topic": "technical"
    },
    {
        "id": "technical_2",
        "text": """
The system works offline on the Android phone — you can view loan details and record
payments without internet. Data syncs automatically when the phone reconnects to the
internet. This is useful when visiting shops in areas with poor mobile signal. The web
version on desktop requires an active internet connection to the backend server.
        """.strip(),
        "topic": "technical"
    },
]