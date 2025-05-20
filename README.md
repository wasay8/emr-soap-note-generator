```markdown
#  EMR SOAP Note Generator

A clinical documentation assistant that generates structured **SOAP-format medical reports** (Subjective, Objective, Assessment, Plan) from Electronic Medical Record (EMR) data using **GPT-4 via LangChain**. Designed to follow documentation standards used in **North American hospitals**.

---

##  Features

-  Supports structured patient, admission, diagnosis, and lab data
-  Generates formal SOAP notes with accurate medical interpretation
-  Groups lab values into standard panels (CBC, Metabolic, Urinalysis)
-  Uses GPT-4 with LangChain to produce high-quality clinical text
-  Streamlit UI for interactive exploration and report generation

---

##  Tech Stack

- **Python** (Pandas, Streamlit)
- **LangChain** + **OpenAI GPT-4**
- Environment management via `.env`
- Data visualizations using Streamlit’s `st.dataframe`


---

##  Installation

```bash
git clone https://github.com/your-username/emr-soap-note-generator.git
cd emr-soap-note-generator
pip install -r requirements.txt
````

---

##  Environment Variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY_2=your_openai_api_key
```

---

##  Usage

```bash
streamlit run app.py
```

1. Select a Patient ID and Admission ID.
2. View diagnosis and lab data.
3. Click **"Create Report"** in the sidebar to generate a SOAP note.
4. Copy or edit the report as needed.

---

##  File Structure

```
 emr-soap-note-generator/
├── app.py                  # Main Streamlit app
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
├──  data/                # Patient and lab data
```

---

##  Future Improvements

* Add abnormal lab value highlighting
* Auto-compare with reference ranges
* PDF export of generated reports
* FHIR integration support

---

##  Author

**Abdul Wasay Siddiqui**
Data Scientist | Applied ML & Healthcare AI
[LinkedIn](https://www.linkedin.com/in/aws97/) • [Portfolio](#)

