# cdss_pe
This repository contains the implementation code for the Clinical Decision Support System (CDSS) used to assist in the diagnosis of pulmonary embolism, and serves as the project's version-controlled codebase.
Pulmonary Embolism CDSS
1. Overview
CDS PE is a desktop application that assists clinicians in evaluating Pulmonary Embolism (PE) risk using the Wells Score criteria. It guides the user through a structured four-step workflow, including patient selection, data entry, Wells Score calculation, and evidence-based recommendations.
2. How to Use the Interface
The application follows a four-step linear workflow. Navigation is done using the Back and Next buttons at the bottom of each page. The step indicator at the top shows your current position.
3. Workflow
The application follows a four-step assessment process:
Step 1: Patient Selection
What it does: Search for existing patients or register a new one.
Left panel:  Registered Patients
![alt text](image.png)
•	Type a name or MRN in the search box to filter the patient table in real time
•	Click a row to select a patient, then click Load Selected Patient or double-click the row to proceed
•	Risk levels in the table are color-coded: red for HIGH, orange for MODERATE, green for LOW
•	Click View Patient History to open the assessment history dialog for the selected patient

Right panel: Register New Patient
![alt text](image-1.png)