import docker
from docker.errors import ImageNotFound
import os
import subprocess
import re


from langchain.chat_models import ChatOpenAI
from langchain.schema.messages import HumanMessage, SystemMessage, AIMessage
def ask_chatgpt(query, system_message, model="gpt-3.5-turbo-0125"):
    with open("openai_token.txt") as opt:
        token = opt.read()
    chat = ChatOpenAI(openai_api_key=token, model=model)

    messages = [
        SystemMessage(
            content= system_message
                    ),
        HumanMessage(
            content=query
            )  
    ]
    #response_format={ "type": "json_object" }
    response = chat.invoke(messages)

    return response.content

import xml.etree.ElementTree as ET
import yaml

def xml_to_dict(element):
    """ Recursively converts XML elements to a dictionary. """
    if len(element) == 0:
        return element.text
    return {
        element.tag: {
            child.tag: xml_to_dict(child) for child in element
        }
    }

def convert_xml_to_yaml(xml_content):
    """ Converts XML content (as a string) to a YAML string. """
    # Parse the XML content from the string
    root = ET.fromstring(xml_content)
    
    # Convert XML to a dictionary
    xml_dict = xml_to_dict(root)
    
    # Convert the dictionary to a YAML string
    yaml_str = yaml.dump(xml_dict, default_flow_style=False)
    
    return yaml_str

def send_command_to_shell(container, command):
    try:
        # Send a command to the shell session
        exec_result = container.exec_run(f"bash -c '{command}'")
        
        output = exec_result.output.decode('utf-8')
        print(f"Command output:\n{output}")
        return output
    
    except Exception as e:
        return f"An error occurred while sending the command: {e}"

def create_screen_session(contianer):
    command = "apt update && apt install -y screen"
    execute_command_in_container(container, command)
    command = "screen -dmS my_screen_session"
    execute_command_in_container(container, command)

def remove_progress_bars(text):
        system_prompt= "You will be given the output of execution a command on a linux terminal. Some of the executed commands such as installation commands have a progress bar which can be long and not very usefull. Your task is to remove the text of progress bars and only keep the important part such as the last progress value for each progress bar (e.g, percentange or something like that). Any text in the output that is not part of the progress bar should remain the same such as success message at the end or error that interrupted the process or the information about what is being installed."
        
        query= "Here is the output of a command that you should clean:\n"+ text

        return ask_chatgpt(query, system_prompt)

def remove_ansi_escape_sequences(text):
    """
    Removes ANSI escape sequences from a given string.
    
    Parameters:
    text (str): The string containing ANSI escape sequences.
    
    Returns:
    str: The cleaned string without ANSI escape sequences.
    """
    # Regular expression to match ANSI escape sequences
    ansi_escape = re.compile(r'\x1b\[[0-9;?]*[a-zA-Z]')
    
    # Removing ANSI escape sequences
    clean_text = ansi_escape.sub('', text)
    
    return clean_text

def check_image_exists(image_name):
    client = docker.from_env()
    try:
        client.images.get(image_name)
        print(f"Image '{image_name}' exists.")
        return True
    except ImageNotFound:
        print(f"Image '{image_name}' does not exist.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def textify_output(output):
    # Decode bytes to string
    output_str = output

    # Regular expression pattern to match ANSI escape sequences
    ansi_escape = re.compile(r'\x1b\[([0-9;]*[A-Za-z])')

    # Remove ANSI escape sequences
    clean_output = ansi_escape.sub('', output_str)

    # Remove extra whitespace characters like \r and \n
    clean_output = clean_output
    return clean_output

def extract_test_sections(maven_output):
    # Regular expressions to match the start and end of test sections
    test_section_start = re.compile(r'Tests run: \d+, Failures: \d+, Errors: \d+, Skipped: \d+')
    test_section_end = re.compile(r'\[INFO\] .*')

    # Find all the indices where the test sections start and end
    starts = [match.start() for match in test_section_start.finditer(maven_output)]
    ends = [match.start() for match in test_section_end.finditer(maven_output)]

    # Ensure each start has a corresponding end
    sections = []
    for start in starts:
        end = next((e for e in ends if e > start), None)
        if end:
            sections.append(maven_output[start:end])
    
    # If no test sections are detected, return the original output
    if not sections:
        return maven_output

    # Join all extracted sections into a single string
    return "\n".join(sections)

def build_image(dockerfile_path, tag):
    client = docker.from_env()
    try:
        log_text = ""
        print(f"Building Docker image from {dockerfile_path} with tag {tag}...")
        image, logs = client.images.build(path=dockerfile_path, tag=tag, rm=True, nocache=True)
        for log in logs:
            if 'stream' in log:
                log_text += log['stream'].strip()
        return "Docker image built successfully.\n"
    except Exception as e:
        print(f"An error occurred while building the Docker image: {e}")
        return None
import docker

def start_container(image_tag):
    client = docker.from_env()
    try:
        print(f"Running container from image {image_tag}...")
        container = client.containers.run(image_tag, detach=True, tty=True)
        print(f"Container {container.short_id} is running.")
        print("CREATING SCREEN SESSION")
        create_screen_session(container)
        return container
    except Exception as e:
        print(f"ERRRRRRRRRRRR: An error occurred while running the container: {e}")
        return None

def execute_command_in_container_old(container, command):
    try:
        print(f"Executing command '{command}' in container {container.short_id}...")
        exec_result = container.exec_run(command, tty=True)
        print(f"Command output:\n{exec_result.output.decode('utf-8')}")
        clean_output = remove_progress_bars(textify_output(exec_result.output.decode('utf-8')))
        test_sections = extract_test_sections(clean_output)
        return test_sections
    except Exception as e:
        return f"An error occurred while executing the command: {e}"
        return None

def execute_command_in_container(container, command):
    try:
        # Wrap the command in a shell execution context
        shell_command = "/bin/sh -c \"{}\"".format(command)
        print(f"Executing command '{command}' in container {container.short_id}...")

        # Execute the command without a TTY, but with streaming output
        exec_result = container.exec_run(shell_command, tty=False)

        # Decode and process the output
        output = exec_result.output.decode('utf-8')
        print(f"Command output:\n{output}")
        
        # Further processing of the output, if needed
        clean_output = remove_progress_bars(textify_output(output))
        test_sections = extract_test_sections(clean_output)
        
        return test_sections

    except Exception as e:
        return f"An error occurred while executing the command: {e}"

# Example usage:
# Start a container
#container = start_container('your_image_tag')
def stop_and_remove(container):
    ontainer.stop()
    container.remove()
    return "Container stopped and removed successfully"
    
def run_container(image_tag, script_path):
    client = docker.from_env()
    try:
        print(f"Running container from image {image_tag}...")
        container = client.containers.run(image_tag, detach=True, tty=True)
        print(f"Container {container.short_id} is running.")
        
        # Use docker cp to copy the script into the cloned repository folder inside the container
        script_name = os.path.basename(script_path)
        container_id = container.short_id
        subprocess.run(['docker', 'cp', script_path, f'{container_id}:/app/code2flow/{script_name}'])
        print(f"Copied {script_name} to /app/code2flow/ in the container.")

        # Execute the script inside the container
        exec_result = container.exec_run(f"sh /app/code2flow/{script_name}", stderr=True, stdout=True)
        stdout = exec_result.output.decode()
        exit_code = exec_result.exit_code
        print(f"Script executed with exit code {exit_code}. Output:")
        print(stdout)
        
        return exit_code, stdout
    except Exception as e:
        print(f"An error occurred while running the container: {e}")
        return None, None
    finally:
        container.remove(force=True)
        print(f"Container {container.short_id} has been removed.")

import tarfile
import io

def create_file_tar(file_path, file_content):
    data = io.BytesIO()
    with tarfile.TarFile(fileobj=data, mode='w') as tar:
        tarinfo = tarfile.TarInfo(name=file_path)
        tarinfo.size = len(file_content)
        tar.addfile(tarinfo, io.BytesIO(file_content.encode('utf-8')))
    data.seek(0)
    return data

def write_string_to_file(container, file_content, file_path):
    try:
        # Create a tarball with the file
        tar_data = create_file_tar(file_path, file_content)

        # Copy the tarball into the container
        container.put_archive('/', tar_data)

        # Verify the file was written
        exit_code, output = container.exec_run(f"cat {file_path}")
        if exit_code == 0:
            print(f"File content in container: {output.decode('utf-8')}", file_path)
        else:
            print(f"Failed to verify the file in the container: {output.decode('utf-8')}")
    finally:
        # Stop and remove the container
        pass

def read_file_from_container(container, file_path):
    """
    Reads the content of a file within a Docker container and returns it as a string.

    Args:
    - container: The Docker container instance.
    - file_path: The path to the file inside the container.

    Returns:
    - The content of the file as a string.
    """
    # Construct the command to read the file content
    command = f'cat {file_path}'

    # Execute the command within the container
    exit_code, output = container.exec_run(cmd=command, tty=True)
    
    if exit_code == 0:
        if file_path.lower().endswith("xml"):
            return convert_xml_to_yaml(output.decode('utf-8'))
        return output.decode('utf-8')
    else:
        return f'Failed to read {file_path} in the container. Output: {output.decode("utf-8")}'

if __name__ == "__main__":
    dockerfile_dir = "."  # Directory containing your Dockerfile
    image_tag = "commons-math_image:rundex"

    container = start_container(image_tag)
    write_string_to_file(container, "test string 1234", "/app/commons-maths/FILE_SHOULD_EXSIST.1234")
    print(read_file_from_container(container, "/app/commons-maths/FILE_SHOULD_EXSIST.1234"))