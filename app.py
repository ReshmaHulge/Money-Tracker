from flask import Flask, render_template, request, redirect, session, send_from_directory, send_file
import sqlite3
import os
import database

from openpyxl import load_workbook
from pypdf import PdfReader
from werkzeug.utils import secure_filename
from reportlab.pdfgen import canvas


app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "local-development-only-key")


# ---------------- Upload Folder ----------------

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)



# =================================================
# HOME PAGE
# =================================================

@app.route("/")
def home():

    if "user" not in session:
        return redirect("/login")


    conn = sqlite3.connect("expense.db")

    cursor = conn.cursor()



    # Total Income

    cursor.execute("""
    SELECT SUM(amount)
    FROM expenses
    WHERE user_id=? AND type='Income'
    """,
    (session["user_id"],))


    total_income = cursor.fetchone()[0] or 0



    # Total Expense

    cursor.execute("""
    SELECT SUM(amount)
    FROM expenses
    WHERE user_id=? AND type='Expense'
    """,
    (session["user_id"],))


    total_expense = cursor.fetchone()[0] or 0



    # Total Transactions

    cursor.execute("""
    SELECT COUNT(*)
    FROM expenses
    WHERE user_id=?
    """,
    (session["user_id"],))


    total_transactions = cursor.fetchone()[0]



    # Budget Alert

    cursor.execute("""
    SELECT amount
    FROM budget
    WHERE user_id=?
    ORDER BY id DESC
    LIMIT 1
    """,
    (session["user_id"],))


    budget = cursor.fetchone()


    alert = ""


    if budget:

        budget_amount = budget[0]


        if budget_amount > 0:

            percentage = (total_expense / budget_amount) * 100


            if percentage >= 90:

                alert = "⚠ Your monthly expense reached 90% of budget"



    conn.close()


    balance = total_income - total_expense



    return render_template(

        "index.html",

        total_income=total_income,

        total_expense=total_expense,

        balance=balance,

        total_transactions=total_transactions,

        alert=alert

    )





# =================================================
# SAVE EXPENSE
# =================================================

@app.route("/save", methods=["POST"])
def save():


    if "user" not in session:
        return redirect("/login")



    date = request.form["date"]

    expense_type = request.form["type"]

    category = request.form["category"]

    description = request.form["description"]

    amount = request.form["amount"]



    receipt = request.files["receipt"]


    filename = ""



    if receipt and receipt.filename != "":


        filename = secure_filename(receipt.filename)


        receipt.save(

            os.path.join(

                app.config["UPLOAD_FOLDER"],

                filename

            )

        )




    conn = sqlite3.connect("expense.db")

    cursor = conn.cursor()



    cursor.execute("""

    INSERT INTO expenses

    (user_id,date,type,category,description,amount,receipt)

    VALUES(?,?,?,?,?,?,?)

    """,

    (

        session["user_id"],

        date,

        expense_type,

        category,

        description,

        amount,

        filename

    ))



    conn.commit()

    conn.close()



    return redirect("/")







# =================================================
# HISTORY
# =================================================

@app.route("/history")
def history():


    if "user" not in session:
        return redirect("/login")



    conn = sqlite3.connect("expense.db")

    cursor = conn.cursor()



    cursor.execute("""

    SELECT *

    FROM expenses

    WHERE user_id=?

    ORDER BY id DESC

    """,

    (session["user_id"],))



    expenses = cursor.fetchall()



    conn.close()



    return render_template(

        "history.html",

        expenses=expenses

    )







# =================================================
# DELETE EXPENSE
# =================================================

@app.route("/delete/<int:id>")
def delete(id):


    if "user" not in session:
        return redirect("/login")



    conn = sqlite3.connect("expense.db")

    cursor = conn.cursor()



    cursor.execute("""

    DELETE FROM expenses

    WHERE id=? AND user_id=?

    """,

    (

        id,

        session["user_id"]

    ))



    conn.commit()

    conn.close()



    return redirect("/history")







# =================================================
# EDIT EXPENSE
# =================================================

@app.route("/edit/<int:id>")
def edit(id):


    if "user" not in session:
        return redirect("/login")



    conn = sqlite3.connect("expense.db")

    cursor = conn.cursor()



    cursor.execute("""

    SELECT *

    FROM expenses

    WHERE id=? AND user_id=?

    """,

    (

        id,

        session["user_id"]

    ))



    expense = cursor.fetchone()



    conn.close()



    return render_template(

        "edit.html",

        expense=expense

    )







# =================================================
# UPDATE EXPENSE
# =================================================

@app.route("/update/<int:id>", methods=["POST"])
def update(id):


    if "user" not in session:
        return redirect("/login")



    date = request.form["date"]

    expense_type = request.form["type"]

    category = request.form["category"]

    description = request.form["description"]

    amount = request.form["amount"]



    conn = sqlite3.connect("expense.db")

    cursor = conn.cursor()



    cursor.execute("""

    UPDATE expenses

    SET date=?,

    type=?,

    category=?,

    description=?,

    amount=?

    WHERE id=? AND user_id=?

    """,

    (

        date,

        expense_type,

        category,

        description,

        amount,

        id,

        session["user_id"]

    ))



    conn.commit()

    conn.close()



    return redirect("/history")


# =================================================
# REGISTER
# =================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":


        fullname = request.form["fullname"]

        email = request.form["email"]

        password = request.form["password"]



        conn = sqlite3.connect("expense.db")

        cursor = conn.cursor()



        # Check Email

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )


        existing_user = cursor.fetchone()



        if existing_user:

            conn.close()

            return "Email already registered"




        cursor.execute("""

        INSERT INTO users

        (fullname,email,password)

        VALUES(?,?,?)

        """,

        (

            fullname,

            email,

            password

        ))



        conn.commit()

        conn.close()



        return redirect("/login")



    return render_template("register.html")







# =================================================
# LOGIN
# =================================================

@app.route("/login", methods=["GET","POST"])
def login():


    if request.method == "POST":


        email = request.form["email"]

        password = request.form["password"]



        conn = sqlite3.connect("expense.db")

        cursor = conn.cursor()



        cursor.execute("""

        SELECT *

        FROM users

        WHERE email=? AND password=?

        """,

        (

            email,

            password

        ))



        user = cursor.fetchone()



        conn.close()




        if user:


            session["user"] = user[1]

            session["user_id"] = user[0]


            return redirect("/")


        else:

            return "Invalid Email or Password"



    return render_template("login.html")









# =================================================
# REPORTS
# =================================================

@app.route("/reports")
def reports():


    if "user" not in session:

        return redirect("/login")



    conn = sqlite3.connect("expense.db")

    cursor = conn.cursor()



    # Income

    cursor.execute("""

    SELECT SUM(amount)

    FROM expenses

    WHERE user_id=? AND type='Income'

    """,

    (session["user_id"],))



    total_income = cursor.fetchone()[0] or 0





    # Expense

    cursor.execute("""

    SELECT SUM(amount)

    FROM expenses

    WHERE user_id=? AND type='Expense'

    """,

    (session["user_id"],))



    total_expense = cursor.fetchone()[0] or 0





    balance = total_income - total_expense





    # Category Wise Expense

    cursor.execute("""

    SELECT category, SUM(amount)

    FROM expenses

    WHERE user_id=? AND type='Expense'

    GROUP BY category

    ORDER BY SUM(amount) DESC

    """,

    (session["user_id"],))



    category_data = cursor.fetchall()



    conn.close()




    return render_template(

        "reports.html",

        total_income=total_income,

        total_expense=total_expense,

        balance=balance,

        category_data=category_data

    )









# =================================================
# EXPORT PDF
# =================================================

@app.route("/export_pdf")
def export_pdf():


    if "user" not in session:

        return redirect("/login")



    conn = sqlite3.connect("expense.db")

    cursor = conn.cursor()



    cursor.execute("""

    SELECT date,type,category,description,amount

    FROM expenses

    WHERE user_id=?

    ORDER BY date DESC

    """,

    (session["user_id"],))



    expenses = cursor.fetchall()



    conn.close()





    pdf_file = "Expense_Report.pdf"



    c = canvas.Canvas(pdf_file)





    # Title

    c.setFont(

        "Helvetica-Bold",

        18

    )


    c.drawString(

        170,

        810,

        "Expense Tracker Report"

    )





    c.setFont(

        "Helvetica",

        12

    )


    c.drawString(

        40,

        785,

        f"User : {session['user']}"

    )





    y = 750





    # Header

    c.setFont(

        "Helvetica-Bold",

        10

    )



    c.drawString(40,y,"Date")

    c.drawString(110,y,"Type")

    c.drawString(180,y,"Category")

    c.drawString(290,y,"Description")

    c.drawString(480,y,"Amount")





    y -= 20





    c.setFont(

        "Helvetica",

        10

    )





    for expense in expenses:



        c.drawString(

            40,

            y,

            str(expense[0])

        )


        c.drawString(

            110,

            y,

            str(expense[1])

        )


        c.drawString(

            180,

            y,

            str(expense[2])

        )


        c.drawString(

            290,

            y,

            str(expense[3])[:20]

        )


        c.drawString(

            480,

            y,

            "Rs. "+str(expense[4])

        )



        y -= 20




        if y < 50:

            c.showPage()

            y = 780




    c.save()



    return send_file(

        pdf_file,

        as_attachment=True

    )









# =================================================
# UPLOAD EXCEL
# =================================================


@app.route("/upload", methods=["GET", "POST"])
def upload():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        file = request.files["file"]

        if file.filename == "":
            return "No file selected"

        filename = secure_filename(file.filename)

        path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(path)

        workbook = load_workbook(path)
        sheet = workbook.active

        total_expense = 0
        category = {}

        for row in sheet.iter_rows(
            min_row=2,
            values_only=True
        ):

            expense_category = row[1]
            amount = row[2]

            if amount is not None:

                try:
                    amount = float(amount)
                except (ValueError, TypeError):
                    continue

                total_expense += amount

                if expense_category in category:
                    category[expense_category] += amount
                else:
                    category[expense_category] = amount

        return render_template(
            "analysis.html",
            total_expense=total_expense,
            category=category
        )

    return render_template("upload.html")





# =================================================
# UPLOAD PDF
# =================================================

@app.route("/upload_pdf", methods=["GET","POST"])
def upload_pdf():


    if "user" not in session:

        return redirect("/login")



    if request.method == "POST":


        file = request.files["file"]



        if file.filename == "":

            return "No file selected"




        filename = secure_filename(

            file.filename

        )



        path = os.path.join(

            app.config["UPLOAD_FOLDER"],

            filename

        )



        file.save(path)





        # -------- Read PDF --------


        reader = PdfReader(path)



        text = ""



        for page in reader.pages:


            page_text = page.extract_text()



            if page_text:

                text += page_text + "\n"






        # -------- Convert Text To Lines --------


        lines = []



        for line in text.split("\n"):


            line = line.strip()



            if line != "":

                lines.append(line)





        print(lines)





        # -------- Create Records --------


        records = []



        i = 0



        while i + 2 < len(lines):


            try:


                date = lines[i]

                category = lines[i+1]

                amount = float(lines[i+2])



                records.append({

                    "date": date,

                    "category": category,

                    "amount": amount

                })



                i += 3



            except:


                i += 1






        print(records)







        # -------- Analysis --------

        # -------- Analysis --------

        total_records = len(records)

        total_expense = sum(
            row["amount"] for row in records
        )

        highest_expense = max(
            (row["amount"] for row in records),
            default=0
        )

        lowest_expense = min(
            (row["amount"] for row in records),
            default=0
        )

        if total_records > 0:
            average_expense = total_expense / total_records
        else:
            average_expense = 0

        # -------- Print Analysis --------

        print("PDF ANALYSIS PAGE OPENING")
        print("TOTAL RECORDS:", total_records)
        print("TOTAL EXPENSE:", total_expense)


        print("TEMPLATE PATH:", app.jinja_loader.searchpath)
        print("PDF TEMPLATE:", app.jinja_env.get_template("pdf_analysis.html").filename)



        return render_template(
            "pdf_analysis.html",
            records=records,
            total_records=total_records,
            total_expense=total_expense,
            highest_expense=highest_expense,
            lowest_expense=lowest_expense,
            average_expense=round(average_expense, 2)
        )

    return render_template("upload_pdf.html")


# =================================================
# VIEW UPLOADED RECEIPT
# =================================================

@app.route("/uploads/<filename>")
def uploaded_file(filename):


    return send_from_directory(

        app.config["UPLOAD_FOLDER"],

        filename

    )









# =================================================
# LOGOUT
# =================================================

@app.route("/logout")
def logout():


    session.pop(

        "user",

        None

    )


    session.pop(

        "user_id",

        None

    )



    return redirect("/login")




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)



# =================================================
# RUN APPLICATION
# ================================================

    
