# Document AI Triage bot

This example shows how to implement a single-task process that is triggered with email inputs, reads all attachments, tries determining their type using [Base64.ai](https://base64.ai/) Intelligent Document Processing solution, and then forwards them to other Processes for the further actions.

You'll learn several key concepts of Robocorp platform:

- Triggering processes with emails
- Using [Base64.ai](https://base64.ai/) Intelligent Document Processing API
- Using [Vault](https://robocorp.com/docs/development-guide/variables-and-secrets/vault) for credentials and [Asset Storage](https://robocorp.com/docs/control-room/asset-storage) for configuration data
- Creating input [Work Items](https://robocorp.com/docs/control-room/unattended/work-data-management) and using [Process library](https://robocorp.com/docs/libraries/rpa-framework/rpa-robocorp-process) to trigger other processes through [Control Room](https://robocorp.com/docs/control-room)

TODO: ADD A VIDEO HERE

## Setup

While the setup might seem to have multiple steps, it's all obvious once you have done it the first time! Just follow along. The following things need to be in place in order for you to run this bot yourself:

### Create some accounts, unless you have them

- Control Room account. [Sign up](https://cloud.robocorp.com/) for free.
- Base64.ai API account. [Sign up](https://base64.ai/) for free.

### Create document handler processes where the documents are sent to

You need to create document handler Processes in Control Room. This project includes a Task `log_input_work_items` that can be used to create a simple Process that only watches for incoming work items and logs their content. Follow these steps:

- Upload this project to the Control Room
- Go to Processes, and create 3 Processes from the same Robot/Task with only one step each Process. Name them differently for example like this:
  - `DOCAI: Handle Invoices`
  - `DOCAI: Handle KYC`  
  - `DOCAI: Handle ACORD`
- Take a note of the process ID of each of these processes, as well as your workspace ID. You can see them easily for example from the API Helper at the top right corner of the Control Room.

**OPTIONAL:** You can also create the `triage_documents` task as a Process in the Control Room, if you want to test the [email triggering](https://robocorp.com/docs/control-room/unattended/email-trigger). Create the Process for example with a name `DOCAI: Triage incoming attachments`, and make sure to take note of the email address when setting the details up. Alternatively, you can just run the triage from your development environment using the included test Work Items.

TODO: ADD A PICTURE

### Create necessary Vault and Asset Storage items

- Following Vault items:
  - Vault called `Base64` with credentials called: `email` and `api-key`
  - Vault called `controlroom` with credentials called: `apikey` and `ws_id`. Create the API key in Control Room, and give permissions to minimum start processes. The second one is your workspace ID.
- One Asset Storage item called `DOCAI_Dispatch` that is of type `JSON` and has the following content. Here you should use the Process IDs that your created for different document types.

```json
{
  "finance/invoice": "efba04f7-30d3-4fef-8511-30e7e518c4b6",
  "insurance/acord": "41bd9493-3aef-4542-973b-4df01a9d67ef",
  "driver_license": "b08cefcc-ca81-41a0-8185-255bc9a88162"
}
```

## The process

The code itself has documents explaining the main steps, but in principle these are the main steps:

- Sets up connection to Base64.ai and Robocorp Control Room Process API and get the doc type to process configuration from Asset Storage
- Iterate over all work items
  - Get all attachment files that have acceptable file extension
  - Iterate over all files
    - Send file to Base64.ai API for extraction
    - Based on document type returned from API, check if there is a match in config and get the Process ID
    - If yes, create a input Work Item with a file and start a Process

## Running it

Testing the process on your local machine, you can use one of the example work items provided with the project. Just hit the VS Code command palette, Run Robot and choose the correct work iten. There is one with just one file, and another with several attachments.

Running the process in the Control Room, just send an email to the address you'll find in the process configuration.

Happy triaging!

