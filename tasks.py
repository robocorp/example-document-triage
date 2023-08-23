from robocorp.tasks import task
from robocorp import vault, storage, workitems

from RPA.DocumentAI.Base64AI import Base64AI
from RPA.Robocorp.Process import Process

import json

@task
def log_input_work_items():
    """Iterate through all input work items and print their payload"""

    for item in workitems.inputs:
        print("\nReceived payload:\n", item.payload)


@task
def triage_documents():
    """Take email attachments from incoming work items, and categorise them
    with Base64.ai API, then send to difference handlers based on category."""

    # Setup Base64.ai connection
    docai_secrets = vault.get_secret("Base64")
    docai = Base64AI()
    docai.set_authorization(docai_secrets["email"], docai_secrets["api-key"])

    # Configure Robocorp Process API
    cr_secrets = vault.get_secret("controlroom")
    process = Process()
    process.set_apikey(cr_secrets["apikey"])
    process.set_workspace_id(cr_secrets["ws_id"])

    # Get configuration JSON from Asset Storage
    config = storage.get_json("DOCAI_Dispatch")

    for item in workitems.inputs:

        # Download only the the files that have a supported type
        paths = []
        for name in item.files:
            suffix = name.split(".")[-1]
            if suffix in ("png", "jpg", "jpeg", "pdf"):
                path = item.download_file(name)
                paths.append(path)

        # Process all the supported files one by one
        for path in paths:

            # Send to Base64.ai API for extraction
            result = docai.scan_document_file(path)
 
            # NOTE
            # Here you could look at the confidence value of the
            # document categorisation, and decide if it's good
            # enough for acting on it automatically.

            # Decide where to send the document for further processing
            process_id = _get_process(result[0]["model"]["type"], config)
            if process_id:
                print(f"starting process: {process_id}")
                process.set_process_id(process_id)

                # Save document extraction result as a file (as it's usually
                # too big to be work item payload)
                filename = "result.json"
                with open(filename, 'w') as file:
                    json.dump(result[0], file, indent=4)

                # Create input work item, also include original file
                item_id = process.create_input_work_item(
                    payload=result[0]["model"], 
                    files=[filename, path]
                )

                # Start the process
                process.start_configured_process(config_type="work_items",  extra_info=item_id)
            else:
                print(f"Unsupported document type {result[0]['model']['type']}")


def _get_process(model, config):
    """Fetches the configuration Asset from Control Room that
    determines the document type to process mapping."""

    # Check if any value in JSON matches with the model, then return
    # key, which is the process_id.
    process_id = None
    for key in config:
        if model.startswith(key):
            process_id = config[key]
            break

    return process_id