from flask import render_template, redirect, url_for, request
from . import main


@main.route("/login", methods=["GET", "POST"])
def login():
    return render_template("index.html", form=form)

