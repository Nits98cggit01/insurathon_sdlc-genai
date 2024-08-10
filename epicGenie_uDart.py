
import streamlit as st
import os
import time
import subprocess
from PIL import Image
import datetime
import base64
from io import BytesIO

from functions import *

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

# Set the Streamlit app configuration
st.set_page_config(page_title="EpicGenie uDART", layout="wide")

logo_path = os.path.join(ROOT_PATH,'warranty_wiz.png')

logo = Image.open(logo_path)
buffer = BytesIO()
logo.save(buffer, format="PNG")
img_str = base64.b64encode(buffer.getvalue()).decode()
# if logo is not None:
#     st.image(logo, width=50)
if logo is not None:
    st.markdown(
        f"""
        <style>
        .logo-container {{
            position: absolute;
            top: 0;
            right: 0;
            padding: 10px;
        }}
        </style>
        <div class="logo-container">
            <img src="data:image/png;base64,{img_str}" width="50">
        </div>
        """,
        unsafe_allow_html=True
    )

colT1, colT2 = st.columns([1, 3])
with colT2:
    st.title(":robot_face: EpicGenie uDART :robot_face:")

def page_1():
    st.info(":robot_face: I will be creating the SDLC flow for you, buckle your seat and get ready for the SDLC journey")
    if st.button("Let's start"):
        st.session_state["page"] = 2
    pass

def page_2():
    st.title(":robot_face: Requirement")
    st.info(f":robot_face: I'll start by identifying your project requirement and defining the scope. I will provide intelligent recommendations to ensure your project is set up for success from the very beginning")
    st.info(f":robot_face: Fill in the below form with your Line of business, the region you are involved with, the sections you need your requirement document to capture and some additional information to cater with")

    # Initialize session state
    if "folder_option" not in st.session_state:
        st.session_state["folder_option"] = None
    if "folder_path" not in st.session_state:
        st.session_state["folder_path"] = None

    # Text inputs
    requirement_name = st.text_input(
    "Line of Business (Mandatory)",
    help="Enter the primary business area you are involved with"
    )
    # region = st.text_input("Region")
    # sections = st.text_input("Sections")
    # specification = st.text_input("Specification")

    countries = ["","United States","United Kingdom", "Continental Europe", "APAC"]
    region = st.selectbox("Region", countries, help="Select the country where your business operates.")
    specification_choice = ["Industry standard","Gen AI enabled","System and user requirement","3rd party interaction with business"]
    specification = st.multiselect("Additional Information",specification_choice, help="Select one or more specifications applicable to your project.")
    section_choice = ["Login page", "UI Configuration", "Coverage selection for vehicle", "Fetching vehicle model factors", "Reporting services such as CLUE Report Record Report Reliability Report Sentiment Analysis", "High level requirement of the Rating on the Factors","Standard based on coverages"]
    sections = st.multiselect("Sections",section_choice, help="Choose one or more sections relevant to your project.")
    
    # Ensure requirement_name is not empty and capture it
    if requirement_name:
        folder_path = os.path.join(ROOT_PATH, requirement_name)

        if os.path.exists(folder_path):
            st.session_state["folder_option"] = st.selectbox(
                "Requirement Name folder already exists. Choose an option:",
                ["Choose an option", "Use the existing folder", "Create a new folder"],
                index=0 if st.session_state["folder_option"] is None else
                ["Choose an option", "Use the existing folder", "Create a new folder"].index(st.session_state["folder_option"])
            )
            if st.session_state["folder_option"] == "Create a new folder":
                new_foldername = st.text_input("New Folder Name", key="new_foldername")
                if st.button("Create New Folder"):
                    new_folder_path = os.path.join(ROOT_PATH, new_foldername)
                    if not os.path.exists(new_folder_path):
                        create_folder_structure(new_folder_path)
                        st.success("New folder created successfully.")
                        st.session_state["folder_path"] = new_folder_path
                    else:
                        st.error("Folder already exists. Please choose another name.")
            elif st.session_state["folder_option"] == "Use the existing folder":
                st.success(f'''Using existing folder "{requirement_name}" from {ROOT_PATH}''')
                st.session_state["folder_path"] = folder_path
                st.session_state["requirement_name"] = requirement_name
                st.session_state["page"] = 4
            else:
                st.warning("You have not chosen the option yet...")
        else:
            if st.button("Create Folder"):
                create_folder_structure(folder_path)
                st.success("Folder created successfully.")
                st.session_state["folder_path"] = folder_path

    st.info(f":robot_face: Requirement phase is completed")
    # Proceed button to navigate to Page 2
    if st.session_state["folder_path"]:
        if st.button("Proceed", help=f':robot_face: Click to proceed with Epic and Feature generation'):
            st.session_state["page"] = 3
            st.session_state["requirement_name"] = requirement_name  # Store the value here
            st.session_state["region"] = region
            st.session_state["sections"] = sections
            st.session_state["specification"] = specification

def page_3():
    st.title(f''':robot_face: Planning''')
    st.info(f''':robot_face: With a clear understanding of your needs, I'll assist you in creating a blueprint for your project, including epics, features, user stories and acceptance criteria''')
    st.subheader("Epic Generation")
    st.info(f":robot_face: - Here is where the Epic and Features :spiral_note_pad: for your user requirement document will be generated. Click the button below to start the journey")

    # Retrieve user input from session state
    requirement_name = st.session_state.get("requirement_name", "")
    region = st.session_state.get("region", "")
    sections = st.session_state.get("sections", "")
    specification = st.session_state.get("specification", "")

    requirement_folder = os.path.join(ROOT_PATH, requirement_name, "requirement")
    epic_chunk_folder = os.path.join(requirement_folder, "epic chunks")


    # Get the folder path from session state
    folder_path = st.session_state.get("folder_path", os.path.join(ROOT_PATH, requirement_name))

    # Display user input fields as non-editable text
    st.text_input("Requirement Name", value=requirement_name, disabled=True)
    st.text_input("Region", value=region, disabled=True)
    st.text_input("Sections", value=sections, disabled=True)
    st.text_input("Specification", value=specification, disabled=True)

    if st.button("Generate Epic and Features"):
        master_prompt = generate_master_prompt(requirement_name, region, sections, specification)
        save_spec_prompt_csv(requirement_name, region, sections, specification, master_prompt)

        # Fetch response from OpenAI
        response_text = fetch_openai_response(master_prompt)
        
        # Save the response text to a file
        save_response_text_to_file(folder_path, requirement_name, response_text)
        st.write(f'Epic fetched')
        split_epic_details(requirement_folder, epic_chunk_folder, requirement_name)
        st.write(f'Epic split done')
        st.success("Generated epic and features successfully!")

        # Store the response and navigate to Page 3
        st.session_state["gpt_response"] = response_text
        st.session_state["page"] = 4

def page_4():
    st.title(f''':robot_face: Planning''')
    st.info(f''':robot_face: With a clear understanding of your needs, I'll assist you in creating a blueprint for your project, including epics, features, user stories and acceptance criteria''')
    st.subheader("Epic Analysis")
    st.info(f":robot_face: - I have created epics and features for your requirement, Dive deeper into your epics. Analyze and structure them into actionable chunks for better clarity and focus, you can edit the below epics and features if required")

    # Retrieve requirement_name from session state
    requirement_name = st.session_state.get("requirement_name", "")

    # Define folder paths
    folder_path = st.session_state.get("folder_path", "")
    requirement_folder = os.path.join(folder_path, "requirement")
    epic_chunk_folder = os.path.join(requirement_folder, "epic chunks")

    # Ensure the epic chunks folder exists
    os.makedirs(epic_chunk_folder, exist_ok=True)

    # Display the epic files
    epic_files = sorted(os.listdir(epic_chunk_folder))

    if not epic_files:
        st.write("No epic files found.")
    else:
        # Show three epics side by side
        columns = st.columns(3)
        for idx, epic_file in enumerate(epic_files):
            # Determine the current column
            col = columns[idx % 3]

            with open(os.path.join(epic_chunk_folder, epic_file), 'r') as file:
                content = file.read()

            # Editable text area for each epic
            with col:
                new_content = st.text_area(epic_file, content, height=200, key=f"text_{epic_file}")

                # Save button for each epic file
                if col.button(f"Save {epic_file}", key=f"save_{epic_file}"):
                    # Only save if the content has changed
                    if new_content != content:
                        # Extract original and new epic names
                        original_first_line = content.split('\n', 1)[0]
                        new_first_line = new_content.split('\n', 1)[0]

                        original_epic_number, original_epic_name = original_first_line.split(':', 1)
                        _, new_epic_name = new_first_line.split(':', 1)

                        original_epic_number = original_epic_number.strip()
                        new_epic_name = new_epic_name.strip()

                        # Determine the new filename
                        new_filename = f'{original_epic_number}_{new_epic_name.replace(" ", "_")}.txt'
                        new_filepath = os.path.join(epic_chunk_folder, new_filename)

                        # Rename the file if the epic name has changed
                        if new_epic_name != original_epic_name.strip():
                            os.rename(os.path.join(epic_chunk_folder, epic_file), new_filepath)
                            st.success(f"File renamed to {new_filename}.")

                        # Save the content to the new file
                        with open(new_filepath, 'w') as file:
                            file.write(new_content)

                        st.success(f"{epic_file} saved successfully.")

                        # Remove the old file if it still exists
                        old_filepath = os.path.join(epic_chunk_folder, epic_file)
                        if old_filepath != new_filepath and os.path.exists(old_filepath):
                            os.remove(old_filepath)
                            st.info(f"Old file {epic_file} deleted.")
                        
                        # Refresh UI after saving
                        # st.query_params(page="3")
                        st.session_state["page"] = 4

                # Delete button for each epic file
                if col.button(f"Delete {epic_file}", key=f"delete_{epic_file}"):
                    os.remove(os.path.join(epic_chunk_folder, epic_file))
                    st.warning(f"{epic_file} deleted.")
                    # Refresh UI after deletion
                    # st.query_params(page="3")
                    st.session_state["page"] = 4

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button(
            "Proceed",
            help=":robot_face: Click to move to the next page where you can review the User story and Acceptance criteria."
        ):
            st.session_state["page"] = 5
    
def page_5():
    st.title(f''':robot_face: Planning''')
    st.info(f''':robot_face: With a clear understanding of your needs, I'll assist you in creating a blueprint for your project, including epics, features, user stories and acceptance criteria''')
    st.subheader("Epic Responses")

    # Retrieve the requirement folder paths
    folder_path = st.session_state.get("folder_path", "")
    requirement_name = st.session_state.get("requirement_name", "")
    requirement_folder = os.path.join(folder_path, "requirement")
    epic_chunk_folder = os.path.join(requirement_folder, "epic chunks")
    epic_response_folder = os.path.join(requirement_folder, "epic response")

    usecase_requirement_file = os.path.join(requirement_folder, f"{requirement_name}_UsecaseRequirement.csv")
    project_folder = os.path.join(ROOT_PATH, requirement_name)

    # Ensure the response folder exists
    os.makedirs(epic_response_folder, exist_ok=True)

    # Get the list of files
    chunk_files = sorted(os.listdir(epic_chunk_folder))
    response_files = sorted(os.listdir(epic_response_folder))

    # Calculate the number of files to process
    files_to_process = [f for f in chunk_files if f not in response_files]
    total_files = len(files_to_process)
    files_per_minute = 4

    # Calculate the time needed
    time_needed = (total_files // files_per_minute) + (1 if total_files % files_per_minute else 0)

    if len(os.listdir(epic_response_folder))==0:
        st.info(f':robot_face: - Here I will be creating the User story and Acceptance criteria for the features, Click the Start Processing Epic button below')
        if st.button("Start Processing Epics"):
            # Start processing each file
            start_time = time.time()
            for idx, epic_file in enumerate(files_to_process):
                # Check for timeout
                elapsed_time = time.time() - start_time
                if elapsed_time / 60 >= time_needed:
                    st.error("Timeout: Some files were not processed in the given time.")
                    break

                # Read epic content
                with open(os.path.join(epic_chunk_folder, epic_file), 'r') as file:
                    epic_content = file.read()

                query = f'''Provide the user story and the detailed acceptance criteria under each feature that covers all the edge cases for the below epic and features:\n{epic_content}
        Suppose if there is a UI for the warranty product field, include the below fields
        Policyholder's Name, Address Line 1, Address Line 2,City,State,Country,Postal Code,Mobile Number,Email,VIN,License Plate,Make,Model,Mileage,First Registration Date,Maker Warranty End Date
        Provide the response in the below template
        Epic 'epic number': epic name
        Feature 'epic number'.'feature number': feature
        User story 'epic number'.'feature number'.'user story number': user story
        Acceptance criteria:
        acceptance criteria
        '''

                # Fetch the response from GPT
                response_text = fetch_openai_response(query)

                # Save the response in the epic_response folder
                response_filepath = os.path.join(epic_response_folder, epic_file)
                with open(response_filepath, 'w') as file:
                    file.write(response_text)

                st.success(f"Processed: {epic_file}")

            if len(os.listdir(epic_response_folder)) == len(chunk_files):
                st.success("User story and acceptance criteria fetched successfully!")
                st.info(f':robot_face: - Voila, I have created the User story and Acceptance criteria for each feature of the epic. Please review my responses and do modify if required')

    else:
        st.info(f':robot_face: - Voila, I have created the User story and Acceptance criteria for each feature of the epic. Please review my responses and do modify if required')
    # Display editable response files with save and delete options
    
    response_files = sorted(os.listdir(epic_response_folder))
    columns = st.columns(3)
    for idx, response_file in enumerate(response_files):
        # Determine the current column
        col = columns[idx % 3]

        with open(os.path.join(epic_response_folder, response_file), 'r') as file:
            content = file.read()

        # Editable text area for each response
        with col:
            new_content = st.text_area(response_file, content, height=200, key=f"text_{response_file}")

            # Save button for each response file
            if col.button(f"Save {response_file}", key=f"save_{response_file}"):
                # Save only if content has changed
                if new_content != content:
                    with open(os.path.join(epic_response_folder, response_file), 'w') as file:
                        file.write(new_content)
                    st.success(f"{response_file} saved successfully.")

            # Delete button for each response file
            if col.button(f"Delete {response_file}", key=f"delete_{response_file}"):
                os.remove(os.path.join(epic_response_folder, response_file))
                st.warning(f"{response_file} deleted.")
                # Refresh UI after deletion
                st.experimental_rerun()

    extract_requirements_from_txt(requirement_folder, epic_response_folder, usecase_requirement_file)
    st.success(f"Use case requirement CSV file has been created successfully")
      
    if not os.path.exists(usecase_requirement_file):
        st.error("Usecase requirement file does not exist.")
        return

    # Load the usecase requirement file into a DataFrame
    df = pd.read_csv(usecase_requirement_file)

    # Generate testerRequirement.csv
    tester_file = os.path.join(project_folder, 'tester', f"{requirement_name}_testerRequirement.csv")
    df_tester = df.copy()
    df_tester['Prompt'] = df.apply(lambda row: f'''Act as an experienced Java tester, you need to create 5-10 test cases  with 100% test coverage for this feature {row["Feature Name"]}, your task is {row["Task"]} and these are the acceptance criteria: {row["Acceptance Criteria"]}
                                                            Make sure the output should be in the below format \n
    Epic name : {row["Epic Name"]}
    Feature name : {row["Feature Name"]}
    Feature id : {row["Feature No"]}
    Test Case Name
    Test Description: 
    Precondition:
    Test Steps:
    - Step description
    - Expected result

    Ensure that all the edge cases are covered for the task with the acceptance criteria.
                                                                '''
                                                            , axis=1)
    df_tester.to_csv(tester_file, index=False)

    st.info(f":robot_face: The User requirement document is now available in your repository")

    st.info(f':robot_face: With this our Planning phase is completed, The User Requirement Document will be generated in your local repo in a few mins')
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button(
            "Accept and Proceed",
            help=":robot_face: Click to proceed with the Development phase"
        ):
            output_word_file = os.path.join(requirement_folder, f"{st.session_state['requirement_name']}_FinalReport.docx")
            merge_txt_files_to_word(epic_response_folder, output_word_file)
            
            st.success("All responses saved!!!")
            st.session_state["page"] = 6

    with col2:
        if st.button(
            "Back",
            help=":robot_face: Click to go back to the Epic analysis page"
        ):
            st.session_state["page"] = 4

def page_6():
    st.title(f''':robot_face: Development''')
    st.info(f''':robot_face: Watch as your vision comes to life. I'll provide live implementation insights and help maintain coding standards to keep your project on track''')
    requirement_name = st.session_state.get("requirement_name", "")  
    requirement_folder = os.path.join(ROOT_PATH, requirement_name)
    automation_folder = os.path.join(requirement_folder, 'automation', 'automation script')
    epic_response_folder = os.path.join(requirement_folder, "requirement", "epic response")
    os.makedirs(automation_folder, exist_ok=True)
    os.makedirs(os.path.join(requirement_folder, 'application'),exist_ok=True)
    application_folder = os.path.join(requirement_folder, 'application')
    src_path = os.path.join(ROOT_PATH,'check_vsc.py')
    destn_path = os.path.join(requirement_folder, 'application')
    
    copy_python_file(src_path, destn_path)
    # st.info(f'The trigger file has been moved to your {application_folder}')
    merge_txt_files(epic_response_folder, application_folder, f"{st.session_state['requirement_name']}.txt")
    # st.info(f'The merged file is now available in your {application_folder}')
    app_name = st.text_input(
    "Application name (Mandatory)",
    help="Give a name to your application"
    )
    lang = ["React JS","streamlit"]
    frontend = st.selectbox("Front end", lang, help="Choose the programming language")
    
    component = ["Springboot","sqlite"]
    backend = st.selectbox("Back end", component, help="Choose the tech stake")

    style_option = ["Material UI","CSS"]
    style = st.selectbox("Style", style_option, help="Choose the styling")

    st.info(f''':robot_face: The create application button will start creating your application in your {application_folder}, grab a :coffee: and experience the art of code development''')
    if st.button('Create application'):
        try:
            trigger_path = os.path.join(application_folder,'check_vsc.py')
            subprocess.run(['python', trigger_path,requirement_name, app_name ,frontend, backend, style], check=True)
            
        except subprocess.CalledProcessError as e:
            st.error("An error occurred during execution.")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button(
            "Proceed",
            help=":robot_face: - Click to move to Testing phase"
        ):
            st.success("All responses saved!!!")
            st.session_state["page"] = 7

    with col2:
        if st.button(
            "Back",
            help=":robot_face: - Click to go back to the Planning phase"
        ):
            
            st.session_state["page"] = 5

def page_7():
    st.title(f''':robot_face: Testing''')
    st.info(f''':robot_face: Quality is key. I will guide you through testing procedures, making sure your product meets all requirements and is free of defects''')
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button(
            "Proceed",
            help=":robot_face: - Click to move to Test case generation"
        ):
            st.session_state["page"] = 8

    with col2:
        if st.button(
            "Back",
            help=":robot_face: - Click to go back to the Development phase"
        ):
            st.session_state["page"] = 6

def page_8():
    st.title(f''':robot_face: Testing''')
    st.info(f''':robot_face: Quality is key. I will guide you through testing procedures, making sure your product meets all requirements and is free of defects''')
    st.info(f':robot_face: - Let me accelerate your testing process by automatically generating test cases from your requirements. I will provide you with detailed scripts for efficiency, Click the button below to start the process')

    def process_with_timer(input_file, script_folder, guide_type, start_index=0):
        # Read the input file
        df = pd.read_csv(input_file)
        num_rows = len(df)
        
        # Calculate time required based on rows
        files_per_minute = 8
        expected_finish_time = (num_rows - start_index) / files_per_minute
        st.info(f":robot_face: Expected finish time: {expected_finish_time:.2f} minutes")

        start_time = time.time()
        processing_time = ((num_rows - start_index) // 5) + (1 if (num_rows - start_index) % 5 != 0 else 0)  # 5 rows per minute

        # Process each row starting from start_index
        for index, row in df.iloc[start_index:].iterrows():
            elapsed_time = (time.time() - start_time) / 60  # Convert to minutes
            if elapsed_time > expected_finish_time:
                st.warning(
                    "The processing time is more than the expected finish time. "
                    "There might be some issue with the AI service. Kindly press the Trigger button and proceed from the previous step."
                )
                if st.button("Trigger", help= f":robot_face: Click this button for regeneration of unprocessed test cases"):
                    st.session_state["page"] = 7  # Go back to page 6
                return

            # Prepare query and filename
            query = row["Prompt"]
            file_name = f"{index + 1}_{row['Feature Name'].replace(' ', '_')}_{guide_type}.txt"
            file_path = os.path.join(script_folder, file_name)
            
            # Skip if file already exists
            if os.path.exists(file_path):
                continue

            # Fetch response from OpenAI
            response = fetch_openai_response(query)
            
            # Save the response to file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(response)
            
            # Update status
            st.write(f"Processing {index + 1}/{num_rows}: {file_name}")

        # Check for unprocessed files
        processed_files = set(os.listdir(script_folder))
        expected_files = set(f"{index + 1}_{row['Feature Name'].replace(' ', '_')}_{guide_type}.txt" for index, row in df.iterrows())
        missing_files = expected_files - processed_files

        # Display success message if all files are processed
        if not missing_files:
            st.success(f"{guide_type} generation successful!")

    # Get paths
    requirement_name = st.session_state.get("requirement_name", "")
    requirement_folder = os.path.join(ROOT_PATH, requirement_name)
    
    # File paths
    tester_file = os.path.join(requirement_folder, 'tester', f"{requirement_name}_testerRequirement.csv")
    developer_script_folder = os.path.join(requirement_folder, 'developer', 'developer script')
    tester_script_folder = os.path.join(requirement_folder, 'tester', 'test case')
    
    # Ensure script folders exist
    os.makedirs(developer_script_folder, exist_ok=True)
    os.makedirs(tester_script_folder, exist_ok=True)

    # Check existing files in the tester script folder
    tester_files = os.listdir(tester_script_folder)
    num_tester_files = len(tester_files)
    tester_df = pd.read_csv(tester_file)
    num_tester_rows = len(tester_df)


    # Generate test case button
    if num_tester_files == num_tester_rows:
        st.success("Test case files exist.")
        st.info(f':robot_face: - The test case files are generated and is now available in your repository')
        
        col1,col2,col3,col4,col5 = st.columns(5)

        with col1:
            with col1:
                if st.button(
                    "Proceed",
                    help=":robot_face: Click to move to the next step to generate regression test case"
                ):
                    st.session_state["page"] = 9

            with col2:
                if st.button(
                    "Back",
                    help=":robot_face: Click to move to previous page"
                ):
                    st.session_state["page"] = 7

        # if st.button("Proceed"):
        #     st.session_state["page"] = 8
    else:
        st.warning(f"Some test cases are not generated. {num_tester_rows - num_tester_files} unprocessed.")
        if st.button("Generate test case"):
            st.info(f':robot_face: - This step might take some time, Grab a :coffee: and :candy:')
            guide_type = "Test case"
            start_index = num_tester_files
            process_with_timer(tester_file, tester_script_folder, guide_type, start_index=start_index)

            if num_tester_files == num_tester_rows:
                st.success("Test cases fully processed. Proceed when ready.")

                col1,col2,col3,col4,col5 = st.columns(5)

                with col1:
                    with col1:
                        if st.button(
                            "Proceed",
                            help=":robot_face: Click to move to the next step to generate regression test case"
                        ):
                            st.session_state["page"] = 9

                    with col2:
                        if st.button(
                            "Back",
                            help=":robot_face: Click to move to previous page"
                        ):
                            st.session_state["page"] = 7

def page_9():
    st.title(f''':robot_face: Testing''')
    st.info(f''':robot_face: Quality is key. I will guide you through testing procedures, making sure your product meets all requirements and is free of defects''')
    st.info(f':robot_face: - From the test cases generated in the previous step, I will identify the regression cases in this step, Click the button below to start')

    requirement_folder = os.path.join(ROOT_PATH, st.session_state.get("requirement_name", ""))
    tester_folder = os.path.join(requirement_folder, 'tester')
    test_case_folder = os.path.join(tester_folder, 'test case')
    regression_folder = os.path.join(tester_folder, 'regression')
    automation_folder = os.path.join(requirement_folder, 'automation', 'automation script')

    # Create regression folder if it does not exist
    os.makedirs(regression_folder, exist_ok=True)
        
    # List all text files in the test case folder
    test_case_files = [f for f in os.listdir(test_case_folder) if f.endswith('.txt')]
    regression_files = [f for f in os.listdir(regression_folder) if f.endswith('.txt')]
    automation_files = [f for f in os.listdir(automation_folder) if f.endswith('_automationScript.txt')]

    if not test_case_files:
        st.warning("No test case files found. Please make sure test case files are present in the 'test case' folder.")
        return

    files_per_minute = 8  # Define the rate of processing files per minute
    process_automation_files = 6

    def process_with_timer(test_case_files, test_case_folder, regression_folder, files_per_minute, start_index=0):
        start_time = time.time()
        total_files = len(test_case_files) - start_index
        time_limit = (total_files / files_per_minute) * 60  # Convert to seconds

        st.info(f":robot_face: Processing {total_files} files. Time limit: {time_limit / 60:.2f} minutes.")

        for index, test_case_file in enumerate(test_case_files[start_index:], start=start_index):
            elapsed_time = (time.time() - start_time) / 60  # Convert to minutes
            if elapsed_time > time_limit / 60:
                st.warning(
                    "The processing time is more than the expected finish time. "
                    "There might be some issue with the AI service. Kindly press the Back button and proceed from the previous step."
                )
                if st.button("Back"):
                    st.session_state["page"] = 8  # Go back to page 7
                return
            
            test_case_path = os.path.join(test_case_folder, test_case_file)

            # Read the content of the test case file
            with open(test_case_path, 'r', encoding='utf-8') as file:
                text_content = file.read()

            # Create the prompt
            prompt = f'''Identify regression cases from the below test cases focusing on key scenarios that cover positive flow only:\n{text_content}
Make sure that regression case should have only 20% of the total test case, so if there are 10 test cases, the regression test case should be only 2'''

            # Generate the response from OpenAI
            response_text = fetch_openai_response(prompt)

            # Modify the filename
            base_name, _ = os.path.splitext(test_case_file)
            regression_file_name = f"{base_name}_Regression.txt"
            regression_file_path = os.path.join(regression_folder, regression_file_name)

            # Save the response to the regression folder
            with open(regression_file_path, 'w', encoding='utf-8') as file:
                file.write(response_text)

            st.write(f'Processed file {index + 1}/{len(test_case_files)}: {test_case_file}')

        st.success("Regression cases generated successfully!")
        st.info(f':robot_face: - Voila, the regression cases are generated and is now available in your repository')
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            if st.button(
                "Proceed",
                help=":robot_face: - Click to move to next page to generate automation script"
            ):
                st.session_state["page"] = 10

        with col2:
            if st.button(
                "Back",
                help=":robot_face: - Click to return to the previous step."
            ):
                st.session_state["page"] = 8

        # if st.button("Proceed"):
        #     st.session_state["page"] = 9

    # Check for unprocessed files and offer to process them
    if len(regression_files) == len(test_case_files):
        st.success("All regression cases are already generated.")
        st.info(f':robot_face: - The regression cases are generated and is now available in your repository')
        
        # col1, col2, col3, col4, col5 = st.columns(5)

        # with col1:
        #     if st.button(
        #         "Proceed",
        #         help=":robot_face: - Click to move to Repository check"
        #     ):
        #         st.session_state["page"] = 10

        # with col2:
        #     if st.button(
        #         "Back",
        #         help=":robot_face: - Click to return to the Test case."
        #     ):
        #         st.session_state["page"] = 8
        # if st.button("Proceed"):
        #     st.session_state["page"] = 9
    else:
        unprocessed_files = set(test_case_files) - set(regression_files)
        num_unprocessed_files = len(unprocessed_files)

        if num_unprocessed_files > 0:
            st.warning(f"Some regression cases are not generated. {num_unprocessed_files} unprocessed.")
            st.info(f':robot_face: - Seems there are some traffic out there, few files are unprocessed, click the button below to process those')
            if st.button("Process unprocessed regression files"):
                st.info(f':robot_face: - This might take some time, sit back, relax and stay tuned')
                start_index = len(regression_files)
                process_with_timer(test_case_files, test_case_folder, regression_folder, files_per_minute, start_index=start_index)
        else:
            # Handle the file processing on button click for the first time
            if st.button("Generate Regression Cases"):
                st.info(f':robot_face: - This might take some time, sit back, relax and stay tuned')
                process_with_timer(test_case_files, test_case_folder, regression_folder, files_per_minute)

    def process_regression(regression_files, regression_folder, automation_folder, process_automation_files):
        start_time = time.time()
        total_files = len(regression_files)
        time_limit = (total_files / process_automation_files) * 60  # Convert to seconds

        st.info(f":robot_face: Processing {total_files} files. Time limit: {time_limit / 60:.2f} minutes.")

        for index, regression_file in enumerate(regression_files):
            elapsed_time = (time.time() - start_time) / 60  # Convert to minutes
            if elapsed_time > time_limit / 60:
                st.warning(
                    "The processing time is more than the expected finish time. "
                    "There might be some issue with the AI service. Kindly press the Back button and proceed from the previous step."
                )
                if st.button("Back",help=":robot_face: Click to go back to Test case generation page"):
                    st.session_state["page"] = 8  # Go back to page 8
                return
            
            regression_path = os.path.join(regression_folder, regression_file)
            # st.write(f"Processing file: {regression_path}")

            # Check if file exists
            if not os.path.exists(regression_path):
                st.error(f"File not found: {regression_path}")
                continue

            # Read the content of the regression file
            with open(regression_path, 'r', encoding='utf-8') as file:
                text_content = file.read()

            # Create the prompt
            automation_prompt = f'''Create automation scripts with BDD framework and Java Selenium for the below regression test case.:\n{text_content}'''

            # Generate the response from OpenAI
            response_text = fetch_openai_response(automation_prompt)

            # Modify the filename
            base_name, _ = os.path.splitext(regression_file)
            if len(base_name) > 80:
                base_name = base_name[:80]
            autoscript_file_name = f"{base_name}_automationScript.txt"
            autoscript_file_path = os.path.join(automation_folder, autoscript_file_name)

            # st.write(f"Saving to: {autoscript_file_path}")

            # Save the response to the automation folder
            with open(autoscript_file_path, 'w', encoding='utf-8') as file:
                file.write(response_text)

            st.write(f'Processed file {index + 1}/{len(regression_files)}: {regression_file}')

        st.success("Automation scripts generated successfully!")
        st.info(f":robot_face: - Voila, the automation scripts are generated and is available in your repository")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            if st.button("Proceed",help=":robot_face: - Click to move to the next page for a final check"):
                st.session_state["page"] = 10
        with col2:
            if st.button("Back",help=f":robot_face: Click to move back to the Test case generation"):
                st.session_state["page"] = 8

        # if st.button("Proceed",help=":robot_face: - Click to move to the next page for a final check"):
        #     st.session_state["page"] = 10

    if len(automation_files) == len(test_case_files):
        st.success("All automation scripts are already generated.")
        st.info(f":robot_face: - The automation scripts are now available in your repository")

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            if st.button("Proceed",help=":robot_face: - Click to move to the next page for a final check"):
                st.session_state["page"] = 10
        with col2:
            if st.button("Back",help=f":robot_face: Click to move back to the Test case generation"):
                st.session_state["page"] = 8
        # transfer_python_file(source_path, destination_path)
        # if st.button("Proceed",help=":robot_face: - Click to move to the next page for a final check"):
        #     st.session_state["page"] = 10
    else:
        regression_base_names = {}
        for f in regression_files:
            base_name, _ = os.path.splitext(f)
            regression_base_names[f] = base_name[:80]

        # Set of processed file base names
        automation_base_names = {os.path.splitext(f)[0].replace('_automationScript', '') for f in automation_files}

        # Determine unprocessed files by their base names
        unprocessed_files = [f for f in regression_files if regression_base_names[f] not in automation_base_names]

        if unprocessed_files:
            st.warning(f"Some automation scripts are not generated. {len(unprocessed_files)} unprocessed.")
            if st.button("Process unprocessed automation files"):
                process_regression(unprocessed_files, regression_folder, automation_folder, files_per_minute)
        else:
            if st.button("Generate Automation Script"):
                process_regression(regression_files, regression_folder, automation_folder, files_per_minute)
   
def page_101():
    st.title("Final Checkup - Repo scanner")
    st.info(f":robot_face: - Let's do a final check up if all files are processed and is available in your repo")
    # Define paths
    if st.button(
                "Back",
                help=":robot_face: Click to go back to the Testing phase - Regression and Automation page"
            ):
                st.session_state["page"] = 9

    requirement_name = st.session_state.get("requirement_name", "")
    requirement_folder = os.path.join(ROOT_PATH, requirement_name)
    epic_details_file = os.path.join(requirement_folder, "requirement", f"{requirement_name}_EpicDetails.txt")
    epic_chunk_folder = os.path.join(requirement_folder, "requirement", "epic chunks")
    epic_response_folder = os.path.join(requirement_folder, "requirement", "epic response")
    final_report_file = os.path.join(requirement_folder, "requirement", f"{requirement_name}_FinalReport.docx")
    usecase_requirement_file = os.path.join(requirement_folder, "requirement", f"{requirement_name}_UsecaseRequirement.csv")
    tester_folder = os.path.join(requirement_folder, "tester")
    tester_requirement_file = os.path.join(tester_folder, f"{requirement_name}_testerRequirement.csv")
    test_case_folder = os.path.join(tester_folder, "test case")
    regression_folder = os.path.join(tester_folder, "regression")
    developer_folder = os.path.join(requirement_folder, "developer")
    developer_file = os.path.join(developer_folder, f"{requirement_name}_developerRequirement.csv")
    developer_script_folder = os.path.join(developer_folder, "developer script")
    automation_folder = os.path.join(requirement_folder, "automation", "automation script")

    # Define checks
    checks = [
        {"step": "Requirement Folder", "path": requirement_folder, "page": None, "is_file": False},
        {"step": "Epic Creation", "path": epic_details_file, "page": 2, "is_file": True},
        {"step": "Epic Chunks Folder", "path": epic_chunk_folder, "page": 2, "is_file": False},
        {"step": "Epic Chunks Files", "path": epic_chunk_folder, "page": 2, "is_file": False, "file_count": True},
        {"step": "Epic Response Folder", "path": epic_response_folder, "page": None, "is_file": False},
        {"step": "Epic Response Files", "path": epic_response_folder, "page": 4, "is_file": False, "file_count_match": epic_chunk_folder},
        {"step": "Final Report", "path": final_report_file, "page": 4, "is_file": True},
        {"step": "Usecase Requirement File", "path": usecase_requirement_file, "page": 5, "is_file": True},
        {"step": "Tester Folder", "path": tester_folder, "page": None, "is_file": False},
        {"step": "Tester Requirement File", "path": tester_requirement_file, "page": 5, "is_file": True, "row_count": True},
        {"step": "Test Case Folder", "path": test_case_folder, "page": None, "is_file": False},
        {"step": "Test Case Files", "path": test_case_folder, "page": 7, "is_file": False, "file_count_match": tester_requirement_file},
        {"step": "Regression Folder", "path": regression_folder, "page": None, "is_file": False},
        {"step": "Regression Files", "path": regression_folder, "page": 8, "is_file": False, "file_count_match": test_case_folder},
        # {"step": "Developer Folder", "path": developer_folder, "page": None, "is_file": False},
        # {"step": "Developer File", "path": developer_file, "page": 5, "is_file": True, "row_count": True},
        # {"step": "Developer Script Folder", "path": developer_script_folder, "page": 7, "is_file": False},
        # {"step": "Developer Script Files", "path": developer_script_folder, "page": None, "file_count_match": developer_file},
        {"step": "Automation Folder", "path": automation_folder, "page": None, "is_file": False},
        {"step": "Automation Files", "path": automation_folder, "page": 9, "file_count_match": regression_folder},
    ]

    # Track completion status
    total_steps = len(checks)
    completed_steps = 0

    # Create table with bold headers
    cols = st.columns([3, 6, 3, 2, 2])
    with cols[0]:
        st.subheader("**Step**")
    with cols[1]:
        st.subheader("**File/Folder Name**")
    with cols[2]:
        st.subheader("**Check**")
    with cols[3]:
        st.subheader("**Status**")
    with cols[4]:
        st.subheader("**Navigation**")

    # Perform checks
    for check in checks:
        step = check["step"]
        path = check["path"]
        is_file = check.get("is_file", False)
        page = check.get("page", None)
        file_count = check.get("file_count", False)
        file_count_match = check.get("file_count_match", None)
        row_count = check.get("row_count", False)

        # Default count_text value
        count_text = "Checking..."

        # Progress bar for each check
        progress_bar = st.progress(0)

        # Simulate progress over 2 seconds
        for percent_complete in range(100):
            time.sleep(0.02)  # Progress over 2 seconds
            progress_bar.progress(percent_complete + 1)

        # Determine existence and counts
        if is_file:
            exists = os.path.isfile(path)
        else:
            exists = os.path.isdir(path)

        if file_count and exists and not is_file:
            files = os.listdir(path)
            count_text = f"{len(files)} files present"

        if file_count_match and exists:
            if os.path.isdir(path):
                match_count = len(os.listdir(path))
            else:
                match_count = sum(1 for _ in open(path)) - 1 if path.endswith('.csv') else 0
            expected_count = len(os.listdir(file_count_match)) if os.path.isdir(file_count_match) else 0
            count_text = f"{match_count} files" + (" (Matched)" if match_count == expected_count else " (Unmatched)")

        if row_count and exists:
            df = pd.read_csv(path)
            count_text = f"{len(df) - 1} rows present"  # Subtract 1 for header

        # Determine status
        status_color = "green" if exists else "red"
        status_text = "Complete" if exists else "Incomplete"
        if exists:
            completed_steps += 1
        
        # Display row
        with cols[0]:
            st.write(step)
        with cols[1]:
            st.write(os.path.basename(path))
        with cols[2]:
            st.write(count_text)
        with cols[3]:
            st.markdown(f"<span style='color: {status_color}; font-weight: bold; font-size: 16px;'>{status_text}</span>", unsafe_allow_html=True)
        with cols[4]:
            if not exists and page is not None:
                if st.button(f"Take me here ({step})"):
                    st.session_state["page"] = page
                    return

        # Ensure the progress bar completes before moving to the next step
        progress_bar.empty()

    # Display balloons if all steps are complete
    if completed_steps == total_steps:
        st.balloons()
        with st.empty():
            st.info(":robot_face: Final checking process completed and all files are generated**")
            st.success("Final checkup complete!")
            time.sleep(2)  # Display message for 2 seconds
        st.balloons()

        

    st.info(f''':robot_face: - Thank You for Using EpicGenie uDART!
I want to express my gratitude for choosing EpicGenie uDART for your requirement management needs. It has been a pleasure guiding you through each step of this journey. I'll surely miss our interactions, but remember, I'm always here whenever you need assistance again. Until next time, take care and happy developing!''')

def page_10():
    st.title("Final Checkup - Repo scanner")
    st.info(f":robot_face: - Let's do a final check up if all files are processed and is available in your repo")
    # Define paths
    
    requirement_name = st.session_state.get("requirement_name", "")
    requirement_folder = os.path.join(ROOT_PATH, requirement_name)
    epic_details_file = os.path.join(requirement_folder, "requirement", f"{requirement_name}_EpicDetails.txt")
    epic_chunk_folder = os.path.join(requirement_folder, "requirement", "epic chunks")
    epic_response_folder = os.path.join(requirement_folder, "requirement", "epic response")
    final_report_file = os.path.join(requirement_folder, "requirement", f"{requirement_name}_FinalReport.docx")
    usecase_requirement_file = os.path.join(requirement_folder, "requirement", f"{requirement_name}_UsecaseRequirement.csv")
    tester_folder = os.path.join(requirement_folder, "tester")
    tester_requirement_file = os.path.join(tester_folder, f"{requirement_name}_testerRequirement.csv")
    test_case_folder = os.path.join(tester_folder, "test case")
    regression_folder = os.path.join(tester_folder, "regression")
    developer_folder = os.path.join(requirement_folder, "developer")
    developer_file = os.path.join(developer_folder, f"{requirement_name}_developerRequirement.csv")
    developer_script_folder = os.path.join(developer_folder, "developer script")
    automation_folder = os.path.join(requirement_folder, "automation", "automation script")

    repocheck_button_style = """
    <style>
    .centered-button {
        display: flex;
        justify-content: center;
    }
    .centered-button button {
        width: 200px;
        height: 50px;
        font-size: 18px;
        margin-top: 20px;
    }
    </style>
    """
    
    # Inject CSS into the Streamlit app
    st.markdown(repocheck_button_style, unsafe_allow_html=True)

    # Add the button with a div for centering
    # st.markdown('<div class="centered-button"><button>Repo Check</button></div>', unsafe_allow_html=True)


    col1, col2, col3, col4 = st.columns([1, 2, 3, 1])
    with col3:
        # Define button logic
        repo_check = st.button("Repo Check")
    
    if repo_check:
    # Define checks
        checks = [
            {"step": "Requirement Folder", "path": requirement_folder, "page": None, "is_file": False},
            {"step": "Epic Creation", "path": epic_details_file, "page": 2, "is_file": True},
            {"step": "Epic Chunks Folder", "path": epic_chunk_folder, "page": 2, "is_file": False},
            {"step": "Epic Chunks Files", "path": epic_chunk_folder, "page": 2, "is_file": False, "file_count": True},
            {"step": "Epic Response Folder", "path": epic_response_folder, "page": None, "is_file": False},
            {"step": "Epic Response Files", "path": epic_response_folder, "page": 4, "is_file": False, "file_count_match": epic_chunk_folder},
            {"step": "Final Report", "path": final_report_file, "page": 4, "is_file": True},
            {"step": "Usecase Requirement File", "path": usecase_requirement_file, "page": 5, "is_file": True},
            {"step": "Tester Folder", "path": tester_folder, "page": None, "is_file": False},
            {"step": "Tester Requirement File", "path": tester_requirement_file, "page": 5, "is_file": True, "row_count": True},
            {"step": "Test Case Folder", "path": test_case_folder, "page": None, "is_file": False},
            {"step": "Test Case Files", "path": test_case_folder, "page": 7, "is_file": False, "file_count_match": tester_requirement_file},
            {"step": "Regression Folder", "path": regression_folder, "page": None, "is_file": False},
            {"step": "Regression Files", "path": regression_folder, "page": 8, "is_file": False, "file_count_match": test_case_folder},
            # {"step": "Developer Folder", "path": developer_folder, "page": None, "is_file": False},
            # {"step": "Developer File", "path": developer_file, "page": 5, "is_file": True, "row_count": True},
            # {"step": "Developer Script Folder", "path": developer_script_folder, "page": 7, "is_file": False},
            # {"step": "Developer Script Files", "path": developer_script_folder, "page": None, "file_count_match": developer_file},
            {"step": "Automation Folder", "path": automation_folder, "page": None, "is_file": False},
            {"step": "Automation Files", "path": automation_folder, "page": 9, "file_count_match": regression_folder},
        ]

        # Track completion status
        total_steps = len(checks)
        completed_steps = 0

        # Create table with bold headers
        cols = st.columns([3, 6, 3, 2, 2])
        with cols[0]:
            st.subheader("**Step**")
        with cols[1]:
            st.subheader("**File/Folder Name**")
        with cols[2]:
            st.subheader("**Check**")
        with cols[3]:
            st.subheader("**Status**")
        with cols[4]:
            st.subheader("**Navigation**")

        # Perform checks
        for check in checks:
            step = check["step"]
            path = check["path"]
            is_file = check.get("is_file", False)
            page = check.get("page", None)
            file_count = check.get("file_count", False)
            file_count_match = check.get("file_count_match", None)
            row_count = check.get("row_count", False)

            # Default count_text value
            count_text = "Checking..."

            # Progress bar for each check
            progress_bar = st.progress(0)

            # Simulate progress over 2 seconds
            for percent_complete in range(100):
                time.sleep(0.02)  # Progress over 2 seconds
                progress_bar.progress(percent_complete + 1)

            # Determine existence and counts
            if is_file:
                exists = os.path.isfile(path)
            else:
                exists = os.path.isdir(path)

            if file_count and exists and not is_file:
                files = os.listdir(path)
                count_text = f"{len(files)} files present"

            if file_count_match and exists:
                if os.path.isdir(path):
                    match_count = len(os.listdir(path))
                else:
                    match_count = sum(1 for _ in open(path)) - 1 if path.endswith('.csv') else 0
                expected_count = len(os.listdir(file_count_match)) if os.path.isdir(file_count_match) else 0
                count_text = f"{match_count} files" + (" (Matched)" if match_count == expected_count else " (Unmatched)")

            if row_count and exists:
                df = pd.read_csv(path)
                count_text = f"{len(df) - 1} rows present"  # Subtract 1 for header

            # Determine status
            status_color = "green" if exists else "red"
            status_text = "Complete" if exists else "Incomplete"
            if exists:
                completed_steps += 1
            
            # Display row
            with cols[0]:
                st.write(step)
            with cols[1]:
                st.write(os.path.basename(path))
            with cols[2]:
                st.write(count_text)
            with cols[3]:
                st.markdown(f"<span style='color: {status_color}; font-weight: bold; font-size: 16px;'>{status_text}</span>", unsafe_allow_html=True)
            with cols[4]:
                if not exists and page is not None:
                    if st.button(f"Take me here ({step})"):
                        st.session_state["page"] = page
                        return

            # Ensure the progress bar completes before moving to the next step
            progress_bar.empty()

        # Display balloons if all steps are complete
        if completed_steps == total_steps:
            st.balloons()
            with st.empty():
                st.info(":robot_face: Final checking process completed and all files are generated**")
                st.success("Final checkup complete!")
                time.sleep(2)  # Display message for 2 seconds
            st.balloons()

        

    st.info(f''':robot_face: - Thank You for Using EpicGenie uDART!
I want to express my gratitude for choosing EpicGenie uDART for your requirement management needs. It has been a pleasure guiding you through each step of this journey. I'll surely miss our interactions, but remember, I'm always here whenever you need assistance again. Until next time, take care and happy developing!''')

    st.title('Deployed services')
    application_link = "http://ec2-44-196-130-112.compute-1.amazonaws.com:3000"
    # amazon_s3_bucket_link = "https://us-east-1.console.aws.amazon.com/s3/buckets/warrantywiz?region=us-east-1&bucketType=general&tab=objects"
    git_link = 'https://github.com/Nits98cggit01/warranty-wiz-app'


    st.subheader("[Application link](%s)" % application_link)
    # st.subheader("[Uploaded folders](%s)" % amazon_s3_bucket_link)
    st.subheader("[Github](%s)" % git_link)
    

    if st.button(
        "Back",
        help=":robot_face: Click to go back to the Testing phase - Regression and Automation page"
    ):
        st.session_state["page"] = 9

def main():
    # Title and introduction
    # st.markdown("### SDLC Flow")

    # Define the phases with their corresponding images and descriptions
    phases = [
        ("Requirement", os.path.join(ROOT_PATH, 'screenshots', 'requirement_gathering.jpg'),
         "We'll start by identifying your project requirement and defining the scope. I will provide intelligent recommendations to ensure your project is set up for success from the very beginning"),
        ("Planning", os.path.join(ROOT_PATH, 'screenshots', 'design.jpg'),
         "With a clear understanding of your needs, I'll assist you in creating a blueprint for your project, ensuring seamless integration with existing systems"),
        ("Development", os.path.join(ROOT_PATH, 'screenshots', 'implementation.jpg'),
         "Watch as your vision comes to life. I'll provide live implementation insights and help maintain coding standards to keep your project on track"),
        ("Testing", os.path.join(ROOT_PATH, 'screenshots', 'testing.jpg'),
         "Quality is key. I will guide you through testing procedures, making sure your product meets all requirements and is free of defects"),
        ("Deployment", os.path.join(ROOT_PATH, 'screenshots', 'deployment.jpg'),
         "Once testing is complete, I'll assist in deploying your product, ensuring a smooth transition from development to production")
    ]

    cols = st.columns(len(phases))
    image_size = (250, 150)  # Set desired size for all images
    
    for i, (phase, img_path, description) in enumerate(phases):
        with cols[i]:
            st.markdown(f"<div style='text-align: center;'><h3>{phase}</h3></div>", unsafe_allow_html=True)
            image = Image.open(img_path).resize(image_size)  # Resize the image to a consistent size
            st.image(image, use_column_width=False)  # Use consistent sizing without stretching
            st.info(f":robot_face: {description}")

    if st.button("Proceed"):
        st.session_state["page"] = 1
    pass

if "page" not in st.session_state:
    st.session_state["page"] = 0

if st.session_state["page"] == 0:
    main()
elif st.session_state["page"] == 1:
    page_1()
elif st.session_state["page"] == 2:
    page_2()
elif st.session_state.get("page") == 3:
    page_3()
elif st.session_state.get("page") == 4:
    page_4()
elif st.session_state.get("page") == 5:
    page_5()
elif st.session_state.get("page") == 6:
    page_6()
elif st.session_state.get("page") == 7:
    page_7()
elif st.session_state.get("page") == 8:
    page_8()
elif st.session_state.get("page") == 9:
    page_9()
elif st.session_state.get("page") == 10:
    page_10()
else:
    pass