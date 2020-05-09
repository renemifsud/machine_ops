from flask import (
    Blueprint,
    render_template,
    session,
    current_app,
    g,
    request,
    make_response,
    redirect,
)
from app import db
from app.models import User, Alert, Solution, Var_Group
from app.alerts.forms import CreateAlert
from app.var_groups.forms import CreateVarGroup
import json

main = Blueprint("main", __name__)


@main.before_request
def before_request():
    if current_app.config.get("IGNORE_AUTH") is True:
        g.user = User.query.get(1)
    else:
        g.user = User.verify_auth_token(session.get("token"))
        if g.user is not None:
            pass
        else:
            return redirect("/login")


@main.route("/home", methods=["GET"])
def home():
    return render_template("home.html")


@main.route("/alerts", methods=["GET"])
def list_alerts():
    alerts = Alert.query.all()
    return render_template("list_alerts.html", alerts=alerts, selected="alerts")


@main.route("/alerts/<int:id>", methods=["GET", "POST"])
def alert(id):
    alert = Alert.query.get_or_404(id)
    form = CreateVarGroup(select=alert.solution_id)
    form.solutions_list.choices = [solution.name for solution in Solution.query.all()]

    if request.method == "GET":
        if alert:
            return render_template(
                "alert.html", alert=alert, data=alert.data, form=form
            )
    if request.method == "POST":
        solution = Solution.query.filter_by(name=form.solutions_list.data).first()
        updated = Alert.query.filter_by(id=id).update({"solution_id": solution.id})
        alert.check_import(request.form["data"], request.form["name"])
        db.session.add(alert)
        db.session.commit()
        return render_template(
            "alert.html", alert=alert, data=alert.data, form=form, saved=True
        )


@main.route("/alerts/solved", methods=["GET"])
def solved():
    alerts = Alert.query.filter_by(solved=True).all()
    if alert:
        return render_template("list_alerts.html", alerts=alerts, selected="alerts")


@main.route("/alerts/triggering", methods=["GET"])
def triggering():
    alerts = Alert.query.filter_by(solved=False).all()
    return render_template("list_alerts.html", alerts=alerts, selected="alerts")


@main.route("/alerts/search", methods=["POST"])
def search_alerts():
    alerts = Alert.query.whoosh_search(request.args.get("query")).all()
    return render_template("list_alerts.html", alerts=alerts, selected="alerts")


@main.route("/alerts/create", methods=["GET", "POST"])
def create_alert():
    if request.method == "GET":
        return render_template("create_alert.html", selected="solutions")
    elif request.method == "POST":
        alert = Alert(creator=g.user)
        alert.check_import(request.form["data"], request.form["name"])
        db.session.add(alert)
        db.session.commit()
        return render_template("create_alert.html", selected="alert")


##''.join(e for e in request.form['var_list'] if e.isalnum())


@main.route("/solutions", methods=["GET"])
def list_solutions():
    solutions = Solution.query.all()
    return render_template(
        "list_solutions.html", solutions=solutions, selected="solutions"
    )


@main.route("/solutions/<int:id>", methods=["GET", "POST"])
def get_solution(id):
    solution = Solution.query.get_or_404(id)
    if request.method == "GET":
        if solution:
            return render_template("solution.html", solution=solution)
    if request.method == "POST":
        solution = Solution.query.filter_by(id=id).first()
        solution.check_import_app(
            request.form["name"], request.form["playbook"], request.form["var_list"]
        )
        db.session.add(solution)
        db.session.commit()
        return render_template("solution.html", solution=solution, saved=True)


@main.route("/solutions/create", methods=["GET", "POST"])
def create_solution():
    if request.method == "GET":
        return render_template("create_solution.html", selected="solutions")
    elif request.method == "POST":
        solution = Solution(creator=g.user)
        solution.check_import_app(
            request.form["name"], request.form["playbook"], request.form["var_list"]
        )
        db.session.add(solution)
        db.session.commit()
        return render_template("create_solution.html", selected="solutions")


@main.route("/solutions/search", methods=["POST"])
def search_solutions():
    solutions = Solution.query.whoosh_search(request.form["query"]).all()
    return render_template(
        "list_solutions.html", solutions=solutions, selected="solutions"
    )


@main.route("/var_groups", methods=["GET"])
def list_var_groups():
    var_groups = Var_Group.query.all()
    return render_template(
        "list_var_groups.html", var_groups=var_groups, selected="groups"
    )


@main.route("/var_groups/<int:id>", methods=["GET"])
def var_group(id):
    group = Solution.query.get_or_404(id)
    if group:
        return render_template("var_group.html", group=group)


@main.route("/var_groups/create", methods=["GET", "POST"])
def create_var_group():
    form = CreateVarGroup()
    form.solutions_list.choices = [solution.name for solution in Solution.query.all()]

    if request.method == "GET":
        return render_template("create_var_group.html", form=form, selected="solutions")
    elif request.method == "POST":
        if request.form.get("solutions_list"):
            solution = Solution.query.filter_by(name=form.solutions_list.data).first()
            session["solution"] = form.solutions_list.data
            var_list = json.loads(solution.var_list)
            return render_template(
                "create_var_group.html",
                form=form,
                var_list=var_list,
                selected="solutions",
            )
        else:
            solution = Solution.query.filter_by(name=session["solution"]).first()
            var_group = Var_Group(creator=g.user)
            var_dict = {}
            var_list = json.loads(solution.var_list)
            for var in json.loads(solution.var_list):
                var_dict[var] = request.form.get(var)

            var_group.check_import_app(request.form.get("groupName"), var_dict)
            db.session.add(var_group)
            db.session.commit()
            return render_template(
                "create_var_group.html",
                form=form,
                var_list=var_list,
                selected="solutions",
                saved=True,
            )

    # elif request.method == "POST":
    #     alert = Alert(creator=g.user)
    #     alert.check_import(request.json)
    #     db.session.add(alert)
    #     db.session.commit()
    #     return render_template(
    #         "create_var_group.html", form=form, vars="", selected="solutions"
    #     )


@main.route("/var_groups/search", methods=["POST"])
def search_var_groups():
    var_group = Var_Group.query.whoosh_search(request.form["query"]).all()
    return render_template(
        "list_var_groups.html", var_group=var_group, selected="groups"
    )
