from awx import AwxController
from app.controller import AppController
import requests, json


def job1(JOBS_KEY, AWX_FQDN, AWX_USER, AWX_PASS, APP_URL, APP_USER, APP_PASS):
    awx = AwxController(AWX_FQDN, AWX_USER, AWX_PASS)
    awx_playbooks = awx.get("job_templates")
    app = AppController(APP_URL)
    app.login(username=APP_USER, password=APP_PASS)

    app_playbooks = app.get_playbooks()
    if app_playbooks is not None:
        saved_count = len(app_playbooks)
    else:
        saved_count = 0

    awx_count = awx_playbooks["count"]
    awx_playbooks = awx_playbooks["results"]

    if awx_count > saved_count:
        if app_playbooks is not None:
            for awx_sol in awx_playbooks:
                found = False
                for app_sol in app_playbooks:
                    if awx_sol["url"] == app_sol["template_url"]:
                        found = True
                if not found:
                    app.create_playbooks(awx_sol)
        else:
            for awx_sol in awx_playbooks:
                app.create_playbooks(awx_sol)
