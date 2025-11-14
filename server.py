# -*- coding: utf-8 -*-
from flask import Flask, render_template, make_response
from livereload import Server

from referenznummer import to_qr_reference
from invoice import render, BASE_DIR, calculate_totals, test_data, swiss_number
from swiss_bill_generator import create_qr_svg

app = Flask(
    __name__,
    template_folder=str(BASE_DIR),
    static_folder=str(BASE_DIR),
    static_url_path=""
)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.jinja_env.auto_reload = True

@app.route("/html")
def invoice():
    data_ = calculate_totals(test_data)
    data_["reference"] = to_qr_reference(data_["invoice"]["number"])
    qr_ = create_qr_svg(data_)
    return render_template("templates/invoice.html", **data_, qr_svg=qr_)

@app.route("/")
def pdf():
    pdf_bytes = render(test_data)
    resp = make_response(pdf_bytes)
    resp.headers["Content-Type"] = "application/pdf"
    resp.headers["Content-Disposition"] = 'inline; filename="invoice.pdf"'
    return resp

if __name__ == "__main__":
    app.jinja_env.filters["swiss"] = swiss_number
    server = Server(app.wsgi_app)

    server.watch(str(BASE_DIR / "templates/invoice.html"), delay=1)
    server.watch(str(BASE_DIR / "styles/styles.css"), delay=1)

    server.serve(port=5000, debug=True)
