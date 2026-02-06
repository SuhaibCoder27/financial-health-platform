from flask import Flask, request, render_template, send_file
from finance_engine import financial_analysis
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from textwrap import wrap
import io
import os

app = Flask(__name__, template_folder="../frontend")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---------- Helper for PDF paragraph wrapping ---------- #
def draw_paragraph(pdf, text, x, y, max_chars=90, line_height=14):
    lines = wrap(text, max_chars)
    for line in lines:
        if y < 80:
            pdf.showPage()
            y = A4[1] - 50
            pdf.setFont("Helvetica", 11)
        pdf.drawString(x, y, line)
        y -= line_height
    return y


# ---------------- MAIN DASHBOARD ---------------- #
@app.route("/", methods=["GET", "POST"])
def home():
    data = None

    if request.method == "POST":
        file = request.files.get("file")
        industry = request.form.get("industry")

        if file and file.filename:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(file_path)

            data = financial_analysis(file_path, industry=industry)

    return render_template("dashboard.html", data=data)


# ---------------- PDF DOWNLOAD ---------------- #
@app.route("/download-report")
def download_report():

    lang = request.args.get("lang", "en")

    files = os.listdir(UPLOAD_FOLDER)
    if not files:
        return "No uploaded financial data found."

    latest_file = os.path.join(UPLOAD_FOLDER, sorted(files)[-1])

    data = financial_analysis(latest_file)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    x, y = 50, height - 50

    # -------- LANGUAGE TEXT -------- #
    if lang == "hi":
        title = "निवेशक वित्तीय स्वास्थ्य रिपोर्ट"
        executive = f"यह रिपोर्ट {data['industry']} व्यवसाय के वित्तीय प्रदर्शन का विश्लेषण करती है।"
        outlook = "व्यवसाय की वित्तीय स्थिति मजबूत है और जोखिम कम है।"
    elif lang == "ta":
        title = "முதலீட்டாளர் நிதி ஆரோக்கிய அறிக்கை"
        executive = f"இந்த அறிக்கை {data['industry']} நிறுவனத்தின் நிதி செயல்திறனை மதிப்பீடு செய்கிறது."
        outlook = "நிறுவனத்தின் நிதி நிலை வலுவாக உள்ளது மற்றும் ஆபத்து குறைவாக உள்ளது."
    else:
        title = "Investor-Ready Financial Health Report"
        executive = (
            f"This report evaluates the financial performance of a {data['industry']} business "
            f"using uploaded financial data and analytics."
        )
        outlook = (
            "The business demonstrates strong financial stability with consistent revenue growth "
            "and manageable risk exposure."
        )

    # -------- PDF CONTENT -------- #
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(x, y, title)
    y -= 40

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(x, y, "1. Executive Summary")
    y -= 20

    pdf.setFont("Helvetica", 11)
    y = draw_paragraph(pdf, executive, x, y)

    y -= 15

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(x, y, "2. Financial Highlights")
    y -= 20

    pdf.setFont("Helvetica", 11)
    highlights = [
        f"Total Revenue: {data['total_revenue']}",
        f"Total Expenses: {data['total_expenses']}",
        f"Net Profit: {data['profit']}",
        f"Forecasted Revenue: {data['forecasted_revenue_next_month']}",
        f"Health Score: {data['financial_health_score']}",
        f"Credit Rating: {data['credit_rating']}"
    ]

    for h in highlights:
        pdf.drawString(x, y, h)
        y -= 16

    y -= 20

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(x, y, "3. Risk Assessment")
    y -= 20

    pdf.setFont("Helvetica", 11)
    for r in data["risks"]:
        pdf.drawString(x + 10, y, f"- {r}")
        y -= 16

    y -= 15

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(x, y, "4. Strategic Recommendations")
    y -= 20

    pdf.setFont("Helvetica", 11)
    for rec in data["recommendations"]:
        pdf.drawString(x + 10, y, f"- {rec}")
        y -= 16

    y -= 15

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(x, y, "5. Investment Outlook")
    y -= 20

    pdf.setFont("Helvetica", 11)
    draw_paragraph(pdf, outlook, x, y)

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="Investor_Financial_Report.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
