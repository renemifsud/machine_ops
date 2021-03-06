from flask import (
    Blueprint,
    render_template,
    session,
    current_app,
    g,
    request,
    Response,
    make_response,
    redirect,
    jsonify,
    url_for,
    make_response,
)
from app import db
from app.models import User, Alert, Solution, Playbook, VariableGroup, Algorithms, AlgorithmsTypes
from app.alerts.forms import CreateAlert
import json, csv
from sqlalchemy import exc
from io import StringIO

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
    alerts = Alert.query.all()
    return render_template("home.html", alerts=alerts)


@main.route("/alerts", methods=["GET"])
def list_alerts():
    alerts = Alert.query.all()
    return render_template("list_alerts.html", alerts=alerts, selected="alerts")


@main.route("/alerts/<int:id>", methods=["GET", "POST"])
def alert(id):
    alert = Alert.query.get_or_404(id)
    solution = None

    if alert.solution_id and not alert.solution_id == "":
        solution = Solution.query.get_or_404(alert.solution_id)

    if request.method == "GET":
        if alert:
            return render_template(
                "alert.html", alert=alert, solution=solution, session=session["token"]
            )
    if request.method == "POST":
        solution = Solution.query.filter_by(id=request.form["solution"]).first()
        updated = Alert.query.filter_by(id=id).update({"solution_id": solution.id})
        alert.check_import(request.form["data"], request.form["name"])
        db.session.add(alert)
        db.session.commit()
        return jsonify(alert.export_data())


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
    alerts = Alert.query.whoosh_search(request.form.get("query")).all()
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


@main.route("/alerts/bulk", methods=["GET", "POST"])
def bulk_alerts():
    if request.method == "GET":
        return render_template("bulk_alerts.html", selected="alerts", uploaded=False)
    elif request.method == "POST":
        if request.files:
            csv_file = request.files["csv"]
            csv_string = csv_file.read().decode("utf8")
            csv_dicts = [
                {k: v for k, v in row.items()}
                for row in csv.DictReader(
                    csv_string.splitlines(), skipinitialspace=True
                )
            ]
            uploaded_alerts = []
            for alert_dict in csv_dicts:
                alert = Alert.query.filter_by(name=alert_dict["name"])
                if alert.count() == 0:
                    alert = Alert(creator=g.user)
                    alert.check_import(
                        alert_dict["data"],
                        alert_dict["name"],
                        alert_dict.get("solution_id", None),
                        True,
                    )
                    try:
                        db.session.add(alert)
                        db.session.commit()
                    except exc.IntegrityError:
                        db.session.rollback()
                        return redirect(url_for("main.bulk_alerts"))
                    uploaded_alerts.append(alert)

            return render_template("bulk_alerts.html", selected="alerts", uploaded=True)


@main.route("/alerts/bulk_select", methods=["GET"])
def bulk_select_alerts():
    solutions = Solution.query.all()
    if request.method == "GET":
        return render_template(
            "bulk_select_alerts.html",
            session=session["token"],
            solutions=solutions,
            selected="alerts",
            uploaded=False,
        )


@main.route("/alerts/bulk_select/download", methods=["POST"])
def bulk_select_alerts_download():
    alerts = json.loads(request.form["alerts"])

    alerts_obj_li = []
    for alert in alerts:
        alerts_obj_li.append(Alert.query.filter_by(id=alert))

    "Export a CSV of all sales data"
    output = StringIO()
    writer = csv.writer(output)
    line = ["id", "data", "user_id", "name", "solution_id"]
    writer.writerow(line)
    for alert in alerts:
        alert = Alert.query.filter_by(id=alert).first()
        line = [
            str(alert.id),
            str(alert.data),
            str(alert.user_id),
            str(alert.name),
            str(alert.solution_id),
        ]
        writer.writerow(line)
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=employee_report.csv"},
    )


@main.route("/playbooks", methods=["GET"])
def list_playbooks():
    playbooks = Playbook.query.all()
    return render_template(
        "list_playbooks.html", playbooks=playbooks, selected="playbooks"
    )


@main.route("/playbooks/<int:id>", methods=["GET", "POST"])
def get_playbook(id):
    playbook = Playbook.query.get_or_404(id)
    if request.method == "GET":
        if playbook:
            return render_template("playbook.html", playbook=playbook)
    if request.method == "POST":
        playbook = Playbook.query.filter_by(id=id).first()
        playbook.check_import_app(
            request.form["name"], request.form["playbook"], request.form["var_list"]
        )
        db.session.add(playbook)
        db.session.commit()
        return render_template("playbook.html", playbook=playbook, saved=True)


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
    playbooks = Playbook.query.all()
    var_groups = VariableGroup.query.all()
    if request.method == "GET":
        return render_template(
            "create_solution.html",
            selected="solutions",
            playbooks=playbooks,
            var_groups=var_groups,
            session=session["token"],
        )
    elif request.method == "POST":
        solution = Solution(creator=g.user)
        solution.check_import_app(
            request.form["name"],
            request.form["sol_playbook_select"],
            request.form["sol_var_group_select"],
        )
        db.session.add(solution)
        db.session.commit()
        return render_template(
            "create_solution.html",
            selected="solutions",
            playbooks=playbooks,
            session=session["token"],
        )


@main.route("/solutions/search", methods=["POST"])
def search_solutions():
    query = request.form.get("query")
    if not (query.isspace() or query == ""):
        solutions = Solution.query.whoosh_search(request.form.get("query")).all()
        return render_template(
            "list_solutions.html", solutions=solutions, selected="solutions"
        )
    else:
        return redirect(url_for("main.list_solutions"))


@main.route("/solutions/bulk", methods=["GET", "POST"])
def bulk_solutions():
    if request.method == "GET":
        return render_template("bulk_solutions.html", selected="alerts", uploaded=False)
    elif request.method == "POST":
        if request.files:
            csv_file = request.files["csv"]
            csv_string = csv_file.read().decode("utf8")
            csv_dicts = [
                {k: v for k, v in row.items()}
                for row in csv.DictReader(
                    csv_string.splitlines(), skipinitialspace=True
                )
            ]
            uploaded = []
            for solution_dict in csv_dicts:
                solution = Solution()
                solution.check_import(
                    solution_dict["name"],
                    solution_dict["playbook"],
                    solution_dict["var_list"],
                )
                try:
                    db.session.add(solution)
                    return db.session.commit()
                except exc.IntegrityError:
                    db.session.rollback()
                    return redirect(url_for("main.bulk_solutions"))

                uploaded.append(solution)
            return render_template(
                "bulk_solutions.html", selected="solutions", uploaded=True
            )


@main.route("/var_groups", methods=["GET"])
def list_var_groups():
    var_groups = VariableGroup.query.all()
    return render_template(
        "list_var_groups.html", var_groups=var_groups, selected="var_groups"
    )


@main.route("/var_groups/<int:id>", methods=["GET"])
def var_group(id):
    var_group = VariableGroup.query.get_or_404(id)
    if var_group:
        return render_template("var_group.html", var_group=var_group)


@main.route("/var_groups/create", methods=["GET", "POST"])
def create_var_group():
    if request.method == "GET":
        playbooks = Playbook.query.all()
        return render_template(
            "create_var_group.html",
            selected="var_groups",
            session=session["token"],
            playbooks=playbooks,
        )
    elif request.method == "POST":
        var_group = VariableGroup(creator=g.user)
        variables = {}
        counter = 0
        while True:
            counter += 1
            key = "key_" + str(counter)
            if key in request.form:
                variables[key] = {
                    "value": request.form["value_" + str(counter)],
                    "type": request.form["var_type_option_" + str(counter)],
                }
            else:
                break

        var_group.check_import_app(request.form["name"], variables)
        db.session.add(var_group)
        db.session.commit()
        return render_template("create_var_group.html", selected="var_groups")


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


@main.route("/settings", methods=["GET"])
def settings():
    return render_template(
        "settings.html", selected="settings", session=session["token"]
    )


@main.route("/models", methods=["GET"])
def list_models():
    return render_template(
        "models.html", selected="models", session=session["token"]
    )
    
@main.route("/models/train", methods=["GET"])
def train_models():
    algo_types = AlgorithmsTypes.query.all()
    return render_template(
        "models.html", selected="models", algo_types=algo_types, session=session["token"]
    )

