import requests
from urllib.parse import urljoin
import json


class AwxController:
    def __init__(self, fqdn, username, password):
        self.api = {
            "ping": "/api/v2/ping/",
            "instances": "/api/v2/instances/",
            "instance_groups": "/api/v2/instance_groups/",
            "config": "/api/v2/config/",
            "settings": "/api/v2/settings/",
            "me": "/api/v2/me/",
            "dashboard": "/api/v2/dashboard/",
            "organizations": "/api/v2/organizations/",
            "users": "/api/v2/users/",
            "projects": "/api/v2/projects/",
            "project_updates": "/api/v2/project_updates/",
            "teams": "/api/v2/teams/",
            "credentials": "/api/v2/credentials/",
            "credential_types": "/api/v2/credential_types/",
            "credential_input_sources": "/api/v2/credential_input_sources/",
            "applications": "/api/v2/applications/",
            "tokens": "/api/v2/tokens/",
            "metrics": "/api/v2/metrics/",
            "inventory": "/api/v2/inventories/",
            "inventory_scripts": "/api/v2/inventory_scripts/",
            "inventory_sources": "/api/v2/inventory_sources/",
            "inventory_updates": "/api/v2/inventory_updates/",
            "groups": "/api/v2/groups/",
            "hosts": "/api/v2/hosts/",
            "job_templates": "/api/v2/job_templates/",
            "jobs": "/api/v2/jobs/",
            "job_events": "/api/v2/job_events/",
            "ad_hoc_commands": "/api/v2/ad_hoc_commands/",
            "system_job_templates": "/api/v2/system_job_templates/",
            "system_jobs": "/api/v2/system_jobs/",
            "schedules": "/api/v2/schedules/",
            "roles": "/api/v2/roles/",
            "notification_templates": "/api/v2/notification_templates/",
            "notifications": "/api/v2/notifications/",
            "labels": "/api/v2/labels/",
            "unified_job_templates": "/api/vs2/unified_job_templates/",
            "unified_jobs": "/api/v2/unified_jobs/",
            "activity_stream": "/api/v2/activity_stream/",
            "workflow_job_templates": "/api/v2/workflow_job_templates/",
            "workflow_jobs": "/api/v2/workflow_jobs/",
            "workflow_approvals": "/api/v2/workflow_approvals/",
            "workflow_job_template_nodes": "/api/v2/workflow_job_template_nodes/",
            "workflow_job_nodes": "/api/v2/workflow_job_nodes/",
        }
        self.fqdn = fqdn
        self.auth = (username, password)

    def get(self, function):
        resp = self.send_request("get", self.api[function])
        if resp:
            return resp
        else:
            print("Get operation failed")

    def run_job(self, template_id: str, extra_vars: dict = None, job_tags: dict = None):
        """ {"target": "mo-app02.doxtechno.com"} """
        data = {}

        if extra_vars:
            data["extra_vars"] = extra_vars
        if job_tags:
            data["job_tags"] = job_tags

        url = urljoin(self.api["job_templates"], str(template_id) + "/launch/")
        resp = self.send_request("POST", url=url, data=data)
        # resp = self.send_request("OPTIONS", url=url, data=extra_vars)
        print(json.dumps(resp, indent=4))
        if resp:
            job_id = resp["job"]
            url = resp["url"]
            while True:
                resp = self.send_request("GET", url=url)
                status = resp["status"]
                if "successful" in status or "failed" in status:
                    break
            print(f"Job {job_id} was {status}")
            if "successful" in resp:
                return (True, resp)
            else:
                return (False, resp)

    def send_request(
        self, method, url, auth=None, headers=None, data=None, verify=False
    ):
        """ Handles sending requests """
        url = urljoin(self.fqdn, url)
        if "get" in method.lower():
            response = requests.get(
                url=url, auth=self.auth, headers=headers, verify=verify
            )
        elif "post" in method.lower():
            response = requests.post(
                url=url, auth=self.auth, headers=headers, json=data, verify=verify
            )
        elif "put" in method.lower():
            response = requests.put(
                url=url, auth=self.auth, headers=headers, json=data, verify=verify
            )
        elif "delete" in method.lower():
            response = requests.delete(
                url=url, auth=self.auth, headers=headers, verify=verify
            )
        elif "options" in method.lower():
            response = requests.options(
                url=url, auth=self.auth, headers=headers, verify=verify
            )

        content = None
        try:
            content = json.loads(response.content.decode("utf8"))
        except json.JSONDecodeError:
            content = response.content.decode("utf8")

        if int(response.status_code) >= 200 and int(response.status_code) <= 399:
            if not content:
                print("Response was null")
            else:
                return content
        else:
            print(
                f"Error sending requests [{response.status_code}] with error message [{content}]\nRequest:\nurl:{str(url)}"
            )


if __name__ == "__main__":
    awx = AwxController("http://mo-awx.doxtechno.com", "admin", "Gl88jZKaPr8AZpBc0daY")
    test = awx.run_job(22, {"target": "mo-rab01.doxtechno.com"}, "create-publisher",)
