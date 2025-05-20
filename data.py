import streamlit as st
import pandas as pd
import os
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from dotenv import load_dotenv
load_dotenv()

# Load the data
df_patients = pd.read_csv("PatientCorePopulatedTable.txt", sep="\\t")
df_admissions = pd.read_csv("AdmissionsCorePopulatedTable.txt", sep="\\t")
df_diagnoses = pd.read_csv("AdmissionsDiagnosesCorePopulatedTable.txt", sep="\\t")
df_labs = pd.read_csv("LabsCorePopulatedTable.txt", sep="\\t")

# Split 'LabName' into 'Lab Category' and 'Test Name'
df_labs[['Lab Category', 'LabName']] = df_labs['LabName'].str.split(':', n=1, expand=True)
df_labs['Lab Category'] = df_labs['Lab Category'].str.strip().str.upper()
df_labs['LabName'] = df_labs['LabName'].str.strip()

st.set_page_config(layout="wide")
st.title("EMR Data Viewer")

# Patient Selection
patient_id = st.selectbox("Select Patient ID", df_patients['PatientID'].unique())
admissions_for_patient = df_admissions[df_admissions['PatientID'] == patient_id]
admission_id = st.selectbox("Select Admission ID", admissions_for_patient['AdmissionID'].unique())

# Layout Columns
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader(" Patient Info")
    st.write(df_patients[df_patients['PatientID'] == patient_id].style.hide(axis="index"))

with col2:
    st.subheader("Admission Info")
    st.write(admissions_for_patient[admissions_for_patient['AdmissionID'] == admission_id])

with col3:
    st.subheader(" Diagnosis Info")
    st.write(df_diagnoses[
        (df_diagnoses['PatientID'] == patient_id) & 
        (df_diagnoses['AdmissionID'] == admission_id)
    ])

st.subheader(" Lab Results")
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
        return " ERROR: OPENAI_API_KEY not found in environment."

    llm = ChatOpenAI(temperature=0.4, model="gpt-4", openai_api_key=openai_key)
    messages = [
        SystemMessage(content="You are a clinical assistant generating EMR reports."),
        HumanMessage(content=prompt)
    ]

    response = llm(messages)
    return response.content

# Sidebar action
st.sidebar.subheader(" Generate Clinical Report")
if st.sidebar.button("Create Report"):
    with st.spinner("Generating report using GPT-4..."):
        report = generate_llm_report_langchain(patient_id, admission_id, df_diagnoses, df_labs)
        st.success("✅ Report Generated")
        st.subheader(" Clinical Report")
        st.text_area("Generated Report", value=report, height=400)


