# ExecutionAgent 🚀  
Automate Building, Testing, and Validation of GitHub Projects in Isolated Containers  

ExecutionAgent is a robust tool leveraging a large language model (LLM) to autonomously **clone, build, install**, and **run test cases** for projects hosted on GitHub—all inside an isolated container. With support for multiple languages and configurations, ExecutionAgent aims to streamline development and quality assurance workflows.  
<div style="text-align: center;">
  <img src="execution_agent.png" alt="Alt text" width="300" height="300">
</div>

---

## 📦 Dev Container Setup  
To get started in a VSCode Dev Container:  
1. Install the [Remote - Containers](https://code.visualstudio.com/docs/remote/containers) extension.  
2. Clone this repository.  
3. Open the repository in VSCode, and it will prompt you to reopen in the dev container. Alternatively, use a command to open the current folder in a dev container.  
4. Write your OpenAI token to the text file `openai_token.txt` at the root of the repo.

---

## ✨ Key Features  
- **Dual Mode Execution**: Run ExecutionAgent with a batch file or directly with a GitHub repository URL.  
- **Autonomous Workflow**: Clone, build, and test GitHub projects with no human intervention (we will add human-in-the-loop soon).
- **Language Support**: Multiple languages like Python, C, C++, Java, JavaScript, and more.  
- **Dev Container Integration**: Preconfigured for VSCode Dev Containers for seamless development.  
- **Metrics** (based on evaluation set of 50 projects):  
  - Build Success Rate: **80%**  
  - Test Success Rate: **65%**  

---

## 🚀 How It Works  

### 1️⃣ Single Repository Mode  
You can directly process a single GitHub repository using the `--repo` option:  
```bash
./ExecutionAgent.sh --repo <github_repo_url> -l <num_value>
```  
Example:  
```bash
./ExecutionAgent.sh --repo https://github.com/pytest-dev/pytest -l 50
```  

When this mode is used, ExecutionAgent will:  
1. Extract the project name from the URL.  
2. Determine the repository's primary programming language by calling `get_main_language.py`.  
3. Clone the repository and set up metadata.  
4. Launch the main loop of ExecutionAgent to build the project and run its test cases.  

The `-l` option allows you to specify the number of cycles which corresponds to the number of actions the agent can execute. By default, if `-l` is not provided, it will be set to 40. If you want to set a different number, simply pass the desired value after `-l`. For example, `-l 50` will use 50 instead of the default value.  

### 2️⃣ Batch File Mode  
Prepare a batch file listing projects to process in the format:  
`<project_name> <github_url> <language>`  

Example (notice how for now we leave one empty line after each entry):  
```plaintext
scipy https://github.com/scipy/scipy Python

pytest https://github.com/pytest-dev/pytest Python
```

Run ExecutionAgent with the batch file:  
```bash
./ExecutionAgent.sh --repo /path/to/batch_file.txt
```  
ExecutionAgent will process each project listed in the file, performing the same steps as the single repository mode. The `-l` option can also be applied here by adding it to the command when running the script.
NOTE: currently, `ExecutionAgent.sh` requires the `--repo` flag even in batch mode, and will error if not present.

To show the results of the last experiment for a specific project, you can call:
```sh
#
python3.10 show_results.py <project_name>
# example python3.10 show_results.py pytest
```

To clean all the logs and unset the api token, you can use the following command (WARNING: ALL THE LOGS AND EXECUTION RESULTS WOULD BE DELETED)
```sh
./clean.sh
```

---

## 🔧 Configuration 

**More options on configuring the agent would be coming soon**

### Control the Number of Iterations:
By default, the number of attempts `ExecutionAgent` will make is 3. After each attempt, `ExecutionAgent` learns from the previous one and adjust its strategy.
In each attempt, the agent executes a number of commands (or cycles) defined by the parameter `l` mentioned above (default = 40).

To set the number of attempts, you need to change line 17 (local max_retries=2) to any number you want (the total number of attempts would be max_retries +1).

### Keep or Delete a docker container
You can set this option in the file `customize.json`. Default value is `"FALSE"` (containers would be deleted). The other option is `"True"` which keeps the containers.

This options useful for the ones who want to reuse the container already built by the agent.

---

## 📊 Results Summary  

| **Metric**              | **Success Rate** |  
|--------------------------|------------------|  
| Build Success Rate       | 80%              |  
| Test Execution Rate      | 65%              |  

Results are logged under `experimental_setups/experiment_XX`, where `XX` is an incremented number for each invocation of ExecutionAgent.  

## 📁 Output Folder Structure Explanation  

The folder structure under `experimental_setups/experiment_XX` is organized to keep track of the various outputs and logs generated during the execution of the `ExecutionAgent`. Below is a breakdown of the key directories and their contents:  

- **files**: Contains files generated by the ExecutionAgent, such as `Dockerfile`, installation scripts, or any configuration files necessary for setting up the container environment.  
  - Example: `Dockerfile`, `INSTALL.sh`   

- **logs**: Stores raw logs capturing the input prompts and the corresponding outputs from the model during execution. These logs are essential for troubleshooting and understanding the behavior of the agent.  
  - Example: `cycles_list_marshmallow`, `prompt_history_marshmallow`  

- **responses**: Holds the responses generated by the model during the execution process in a structured JSON format. These responses include details about the generated build or test configurations and results.  
  - Example: `model_responses_marshmallow`  

- **saved_contexts**: Contains the saved states of the agent object at each iteration of the execution process. These snapshots are useful for debugging, tracking changes, and extracting subcomponents of the prompt across different cycles.  
  - Example: `cycle_1`, `cycle_10`, etc.  


---

## 📜 Research Paper  
Dive into the technical details and evaluation in our [paper](https://software-lab.org/publications/ExecutionAgent_2024-12-14.pdf).  

---

## 📬 Feedback  
Have suggestions or found a bug? Open an issue or contact us at [my_email](mailto:fi_bouzenia@esi.dz).
