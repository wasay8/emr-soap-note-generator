
# import streamlit as st
# import pandas as pd
# import os
# from langchain.chat_models import ChatOpenAI
# from langchain.schema import SystemMessage, HumanMessage
# from dotenv import load_dotenv
# load_dotenv()


# # Load the data
# df_patients = pd.read_csv("/Users/abdulwasaysiddiqui/Desktop/Symbian Health/EMR Report/100-patients/PatientCorePopulatedTable.txt", sep="\t")
# df_admissions = pd.read_csv("/Users/abdulwasaysiddiqui/Desktop/Symbian Health/EMR Report/100-patients/AdmissionsCorePopulatedTable.txt", sep="\t")
# df_diagnoses = pd.read_csv("/Users/abdulwasaysiddiqui/Desktop/Symbian Health/EMR Report/100-patients/AdmissionsDiagnosesCorePopulatedTable.txt", sep="\t")
# df_labs = pd.read_csv("/Users/abdulwasaysiddiqui/Desktop/Symbian Health/EMR Report/100-patients/LabsCorePopulatedTable.txt", sep="\t")

# # Separating LabName and TestName
# # Split 'LabName' into 'Lab Category' and 'Test Name'
# df_labs[['Lab Category', 'Test Name']] = df_labs['LabName'].str.split(':', n=1, expand=True)

# # Optional: Strip leading/trailing whitespace
# df_labs['Lab Category'] = df_labs['Lab Category'].str.strip().str.upper()
# df_labs['Test Name'] = df_labs['Test Name'].str.strip()
# df_labs.drop(columns=['LabName'], inplace=True)



# st.set_page_config(layout="wide")  # Enable wide mode

# st.title("📋 EMR Data Viewer")

# # Step 1: Select Patient ID
# patient_id = st.selectbox("Select Patient ID", df_patients['PatientID'].unique())

# # Step 2: Select Admission ID
# admissions_for_patient = df_admissions[df_admissions['PatientID'] == patient_id]
# admission_id = st.selectbox("Select Admission ID", admissions_for_patient['AdmissionID'].unique())

# # Layout: Split into 3 columns
# col1, col2, col3 = st.columns(3)

# # Column 1: Patient Info
# with col1:
#     st.subheader("🧍 Patient Info")
#     st.write(df_patients[df_patients['PatientID'] == patient_id].style.hide(axis="index"))

# # Column 2: Admission Info
# with col2:
#     st.subheader("🏥 Admission Info")
#     st.write(admissions_for_patient[admissions_for_patient['AdmissionID'] == admission_id])

# # Column 3: Diagnosis Info
# with col3:
#     st.subheader("🩺 Diagnosis Info")
#     st.write(df_diagnoses[
#         (df_diagnoses['PatientID'] == patient_id) & 
#         (df_diagnoses['AdmissionID'] == admission_id)
#     ])

# # Full-width for Labs
# st.subheader("🧪 Lab Results")
# st.dataframe(df_labs[
#     (df_labs['PatientID'] == patient_id) & 
#     (df_labs['AdmissionID'] == admission_id)
# ], use_container_width=True)




# # Step 3: Generate LLM Report
# def generate_llm_report_langchain(patient_id, admission_id, df_diagnoses, df_labs):
#     diagnosis_rows = df_diagnoses[
#         (df_diagnoses['PatientID'] == patient_id) &
#         (df_diagnoses['AdmissionID'] == admission_id)
#     ]
#     lab_rows = df_labs[
#         (df_labs['PatientID'] == patient_id) &
#         (df_labs['AdmissionID'] == admission_id)
#     ].sort_values("LabDateTime")

#     diagnosis_str = "\n".join([
#         f"- {row['PrimaryDiagnosisCode']}: {row['PrimaryDiagnosisDescription']}"
#         for _, row in diagnosis_rows.iterrows()
#     ])

#     lab_str = "\n".join([
#         f"- {row['LabName']}: {row['LabValue']} {row['LabUnits']} at {row['LabDateTime']}"
#         for _, row in lab_rows.iterrows()
#     ])

# #     prompt = f"""
# # The following is a patient's medical record during one hospital admission.
# # Patient ID: {patient_id}
# # Admission ID: {admission_id}

# # Diagnoses:
# # {diagnosis_str}

# # Lab Results:
# # {lab_str}

# # Write a detailed clinical report of this patient's condition on the basis of lab results and diagnosis. Use a official formal format used in North American Standard by hospitals.
# # """

# #     prompt = f"""
# # You are a clinical documentation assistant helping draft hospital-grade medical notes in the SOAP format (Subjective, Objective, Assessment, Plan), following North American clinical standards.

# # Below is data from a single patient’s hospital admission:

# # Patient Demographics:
# # - Patient ID: {patient_id}
# # - Admission ID: {admission_id}


# # Diagnosis:
# # {diagnosis_str}

# # Lab Results:
# # {lab_str}

# # Instructions:
# # - Structure the report strictly in SOAP format:
# #   - **Subjective:** Mention if available. If no subjective symptoms provided, clearly state "No subjective complaints documented."
# #   - **Objective:** Summarize vital signs (if available), diagnosis, and grouped lab results (CBC, CMP, Urinalysis). Highlight abnormal values with normal reference ranges.
# #   - **Assessment:** Interpret the abnormal findings clinically in relation to the diagnosis. Identify any possible conditions (e.g., anemia, infection, organ dysfunction).
# #   - **Plan:** Suggest next steps, such as further tests, imaging, consults, or clinical follow-up.
# # - Maintain a clinical, formal tone used in hospital documentation.
# # - Do not restate the input verbatim.

# # Generate the final report using professional medical terminology suitable for use in an EMR system.
# # """

#     prompt = f"""
#     You are a clinical documentation assistant responsible for generating formal medical reports in the SOAP format (Subjective, Objective, Assessment, Plan) for electronic health records (EHR) in North American hospitals.

# You are provided with structured data from a single patient admission, including diagnosis, lab results, demographics, and admission dates.

# ---

# **Patient Demographics:**
# - Patient ID: {patient_id}
# - Admission ID: {admission_id}

# **Diagnosis:**
# {diagnosis_str}

# **Lab Results:**
# {lab_str}

# ---

# **Instructions:**

# Generate a clinical note in the following format:

# ---

# **SUBJECTIVE:**  
# - If no symptoms or patient complaints are provided, write: “No subjective complaints documented.”

# **OBJECTIVE:**  
# - Start with the confirmed diagnosis.  
# - Summarize and group lab findings under standard panels (CBC, CMP/Metabolic, Urinalysis).  
# - Report abnormal values **with normal reference ranges** for clinical context.  
# - Highlight clinical significance where appropriate using concise medical terminology.

# **ASSESSMENT:**  
# - Interpret abnormal findings **in relation to the diagnosis** and general patient context.  
# - Avoid speculation. Use cautious, medically accurate phrases such as:
#   - “Findings may be consistent with…”
#   - “Could suggest a possible…”
# - Identify any concerns like infection, anemia, liver dysfunction, or glucose abnormalities.

# **PLAN:**  
# - Recommend next clinical actions in priority order.  
# - Include further tests, imaging, specialist consults, and monitoring strategies.  
# - Use specific and time-based recommendations (e.g., “Repeat CBC in 48 hours”, “Order iron panel”, etc.)

# ---
# **Additional Notes:**
# - Use a formal clinical tone suitable for hospital documentation.
# - Do not repeat input data verbatim.
# - Structure output cleanly with headers.
# - Avoid generic language like “abnormal labs” without specifying which and why.

# Generate only the completed SOAP report below.

#     """
#     openai_key = os.getenv("OPENAI_API_KEY_2")
#     if not openai_key:
#         return "❌ ERROR: OPENAI_API_KEY not found in environment."

#     llm = ChatOpenAI(temperature=0.4, model="gpt-4", openai_api_key=openai_key)
#     messages = [
#         SystemMessage(content="You are a clinical assistant generating EMR reports."),
#         HumanMessage(content=prompt)
#     ]

#     response = llm(messages)
#     return response.content



# # Sidebar section
# st.sidebar.subheader("📝 Generate Clinical Report")

# if st.sidebar.button("Create Report"):
#     with st.spinner("Generating report using GPT-4..."):
#         report = generate_llm_report_langchain(
#             patient_id, admission_id, df_diagnoses, df_labs
#         )
#         st.success("✅ Report Generated")
#         st.subheader("📄 Clinical Report")
#         st.text_area("Generated Report", value=report, height=400)



# Updating the complete Streamlit code based on your latest request


import streamlit as st
import pandas as pd
import os
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from dotenv import load_dotenv
load_dotenv()

# Load the data
df_patients = pd.read_csv("/Users/abdulwasaysiddiqui/Desktop/Symbian Health/EMR Report/100-patients/PatientCorePopulatedTable.txt", sep="\\t")
df_admissions = pd.read_csv("/Users/abdulwasaysiddiqui/Desktop/Symbian Health/EMR Report/100-patients/AdmissionsCorePopulatedTable.txt", sep="\\t")
df_diagnoses = pd.read_csv("/Users/abdulwasaysiddiqui/Desktop/Symbian Health/EMR Report/100-patients/AdmissionsDiagnosesCorePopulatedTable.txt", sep="\\t")
df_labs = pd.read_csv("/Users/abdulwasaysiddiqui/Desktop/Symbian Health/EMR Report/100-patients/LabsCorePopulatedTable.txt", sep="\\t")

# Split 'LabName' into 'Lab Category' and 'Test Name'
df_labs[['Lab Category', 'LabName']] = df_labs['LabName'].str.split(':', n=1, expand=True)
df_labs['Lab Category'] = df_labs['Lab Category'].str.strip().str.upper()
df_labs['LabName'] = df_labs['LabName'].str.strip()

st.set_page_config(layout="wide")
st.title("📋 EMR Data Viewer")

# Patient Selection
patient_id = st.selectbox("Select Patient ID", df_patients['PatientID'].unique())
admissions_for_patient = df_admissions[df_admissions['PatientID'] == patient_id]
admission_id = st.selectbox("Select Admission ID", admissions_for_patient['AdmissionID'].unique())

# Layout Columns
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🧍 Patient Info")
    st.write(df_patients[df_patients['PatientID'] == patient_id].style.hide(axis="index"))

with col2:
    st.subheader("🏥 Admission Info")
    st.write(admissions_for_patient[admissions_for_patient['AdmissionID'] == admission_id])

with col3:
    st.subheader("🩺 Diagnosis Info")
    st.write(df_diagnoses[
        (df_diagnoses['PatientID'] == patient_id) & 
        (df_diagnoses['AdmissionID'] == admission_id)
    ])

st.subheader("🧪 Lab Results")
st.dataframe(df_labs[
    (df_labs['PatientID'] == patient_id) & 
    (df_labs['AdmissionID'] == admission_id)
], use_container_width=True)

# Generate report logic
def generate_llm_report_langchain(patient_id, admission_id, df_diagnoses, df_labs):
    diagnosis_rows = df_diagnoses[
        (df_diagnoses['PatientID'] == patient_id) &
        (df_diagnoses['AdmissionID'] == admission_id)
    ]
    lab_rows = df_labs[
        (df_labs['PatientID'] == patient_id) &
        (df_labs['AdmissionID'] == admission_id)
    ].sort_values("LabDateTime")

    diagnosis_str = "\\n".join([
        f"- {row['PrimaryDiagnosisCode']}: {row['PrimaryDiagnosisDescription']}"
        for _, row in diagnosis_rows.iterrows()
    ])

    lab_grouped_str = ""
    for category in ['CBC', 'METABOLIC', 'URINALYSIS']:
        category_rows = lab_rows[lab_rows['Lab Category'] == category]
        if not category_rows.empty:
            lab_grouped_str += f"\\n**{category} Panel:**\\n"
            for _, row in category_rows.iterrows():
                lab_grouped_str += f"- {row['LabName']}: {row['LabValue']} {row['LabUnits']} at {row['LabDateTime']}\\n"

    prompt = """
You are a clinical documentation assistant responsible for generating formal medical reports in the SOAP format (Subjective, Objective, Assessment, Plan) for electronic health records (EHR) in North American hospitals.

You are provided with structured data from a single patient admission, including diagnosis, lab results, demographics, and admission dates.

---

Patient Demographics:
- Patient ID: {patient_id}
- Admission ID: {admission_id}

Diagnosis:
{diagnosis_str}

Lab Results:
{lab_grouped_str}

---

Instructions:

Generate a clinical note in the following format:

---

SUBJECTIVE:
- If no symptoms or patient complaints are provided, write: “No subjective complaints documented.”

OBJECTIVE:
- Start with the confirmed diagnosis.  
- Summarize and group lab findings under standard panels (CBC, CMP/Metabolic, Urinalysis).  
- Report abnormal values **with normal reference ranges** for clinical context.  
- Highlight clinical significance where appropriate using concise medical terminology.

ASSESSMENT:
- Interpret abnormal findings **in relation to the diagnosis** and general patient context.  
- Avoid speculation. Use cautious, medically accurate phrases such as:
  - “Findings may be consistent with…”
  - “Could suggest a possible…”
- Identify any concerns like infection, anemia, liver dysfunction, or glucose abnormalities.

PLAN:  
- Recommend next clinical actions in priority order.  
- Include further tests, imaging, specialist consults, and monitoring strategies.  
- Use specific and time-based recommendations (e.g., “Repeat CBC in 48 hours”, “Order iron panel”, etc.)

---
Additional Notes:
- Use a formal clinical tone suitable for hospital documentation.
- Do not repeat input data verbatim.
- Structure output cleanly with headers.
- Avoid generic language like “abnormal labs” without specifying which and why.

Generate only the completed SOAP report below.
"""

    openai_key = os.getenv("OPENAI_API_KEY_2")
    if not openai_key:
        return "❌ ERROR: OPENAI_API_KEY not found in environment."

    llm = ChatOpenAI(temperature=0.4, model="gpt-4", openai_api_key=openai_key)
    messages = [
        SystemMessage(content="You are a clinical assistant generating EMR reports."),
        HumanMessage(content=prompt)
    ]

    response = llm(messages)
    return response.content

# Sidebar action
st.sidebar.subheader("📝 Generate Clinical Report")
if st.sidebar.button("Create Report"):
    with st.spinner("Generating report using GPT-4..."):
        report = generate_llm_report_langchain(patient_id, admission_id, df_diagnoses, df_labs)
        st.success("✅ Report Generated")
        st.subheader("📄 Clinical Report")
        st.text_area("Generated Report", value=report, height=400)


