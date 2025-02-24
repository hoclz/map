<customUI xmlns="http://schemas.microsoft.com/office/2006/01/customui">
  <ribbon>
    <tabs>
      <tab id="customTab" label="HCZ Research">
      
        <!-- Hospitalization Group -->
        <group id="group1" label="Hospitalization">
          <button id="openAsthma" label="Numerator" 
                  onAction="RibbonCallback_OpenAsthma" imageMso="DataImport"
                  description="Open the Asthma Numerator report." />
          <button id="openPopulation" label="Denominator" 
                  onAction="RibbonCallback_OpenPopulation" imageMso="DataExport"
                  description="Open the Asthma Denominator report." />
        </group>

        <!-- HCZ Research Papers Group -->
        <group id="group2" label="HCZ IDPH Research">
          <dropDown id="dropdownDocument" label="Select Document"
                    onAction="RibbonCallback_DocumentChanged">
            <item id="asm1" label="Asthma: J45 Data Extraction" />
            <item id="asm2" label="Asthma: SAS UserForm" />
            <item id="asm3" label="Asthma: Asthma Report" />
            <item id="asm4" label="Asthma: 10 Regions Num" />
            <item id="asm5" label="Asthma: 10 Regions Den" />
            <item id="asm6" label="Asthma: Age Adjusted Rate" />
            <item id="asm7" label="Asthma: Data At Glance" />
            <item id="asm8" label="Asthma: Tweaking The Code" />
            <item id="dem1" label="Dementia: Regional Num 1" />
            <item id="dem2" label="Dementia: Question 1" />
            <item id="dem3" label="Dementia: Question 2" />
            <item id="dem4" label="Dementia: Report 4" />
            <item id="dem5" label="Dementia: Report 5" />
            <item id="inj1" label="Injury: Report 1" />
            <item id="inj2" label="Injury: Report 2" />
            <item id="inj3" label="Injury: Report 3" />
            <item id="inj4" label="Injury: Report 4" />
            <item id="inj5" label="Injury: Report 5" />
            <item id="covid1" label="COVID: Dashboard Information" />
            <item id="covid2" label="COVID: Report 2" />
            <item id="covid3" label="COVID: Report 3" />
            <item id="covid4" label="COVID: Report 4" />
            <item id="covid5" label="COVID: Report 5" />
          </dropDown>

          <dropDown id="dropdownFileExtension" label="Select File Type"
                    onAction="RibbonCallback_FileTypeChanged">
            <item id="docx" label="DOCX" />
            <item id="pdf" label="PDF" />
            <item id="txt" label="TXT" />
          </dropDown>

          <button id="openFile" label="Open Selected File" 
                  onAction="RibbonCallback_OpenSelectedFile" imageMso="FileOpen"
                  description="Open the document based on your selections." />
        </group>

        <!-- HCZ Viz Research Group -->
        <group id="group3" label="HCZ Viz Research">
          <dropDown id="dropdownVizDocument" label="Select Visualization"
                    onAction="RibbonCallback_VizDocumentChanged">
            <item id="viz1" label="Asthma: 2023 AA Rate Regional NHA" />
            <item id="viz2" label="Asthma: 2023 AA Rate Regional NHB" />
            <item id="viz3" label="Asthma: 2023 AA Rate Regional NHW" />
            <item id="viz4" label="Asthma: 2023 AA Rate Regional HISP" />
            <item id="viz5" label="Asthma: 23 AA Rate Region/Demographic" />
            <item id="viz6" label="Asthma: 22 AA Rate Region/Demographic" />
            <item id="viz7" label="Asthma: 21 AA Rate Region/Demographic" />
            <item id="viz8" label="Asthma: 20 AA Rate Region/Demographic" />
            <item id="viz9" label="Asthma: 2016-2023 AA Rate Regional Trends" />
            <item id="viz10" label="Injury: Firearm Safe Strategies Grantees" />
            <item id="demvz1" label="Dementia: 16-23 AA Rate Heatmap" />
            <item id="demvz2" label="Dementia: 16-23 AA Rate Bar Chart" />
            <item id="demvz3" label="Dementia: 16-23 AA Rate Trends" />
          </dropDown>

          <dropDown id="dropdownVizFileType" label="Select Output Format"
                    onAction="RibbonCallback_VizFileTypeChanged">
            <item id="png" label="PNG" />
          </dropDown>

          <button id="exportViz" label="Export Visualization" 
                  onAction="RibbonCallback_ExportViz" imageMso="FileSaveAs"
                  description="Export the selected visualization in chosen format." />
        </group>

        <!-- HCZ FCFA Research Group -->
        <group id="group4" label="HCZ FCFA Research">
          <dropDown id="dropdownFCFADocument" label="Select FCFA Research Paper"
                    onAction="RibbonCallback_FCFADocumentChanged">
            <item id="fcfa1" label="FCFA: Physical Money Printing" />
            <item id="fcfa2" label="FCFA: Scientifique-Definition" />
            <item id="fcfa3" label="FCFA: Citations des chefs d’État" />
            <item id="fcfa4" label="FCFA: Durée de creation de la monnaie" />
            <item id="fcfa5" label="FCFA: Mise en garde- Fassassi Yacouba" />      
            <item id="fcfa6" label="BOOK: AVANT PROPOS" />
            <item id="fcfa7" label="BOOK: Introduction" />
            <item id="fcfa8" label="BOOK: ACRONYME" />
            <item id="fcfa9" label="BOOK: CONCLUSION" />
            <item id="fcfa10" label="BOOK: Cover Page" />
            <item id="fcfa11" label="BOOK: DEDICAE" />
            <item id="fcfa12" label="BOOK: DOS DE COUVERTURE" />
            <item id="fcfa13" label="BOOK: Citations de M. HCZ" />
            <item id="fcfa14" label="BOOK: REMERCIEMENTS" />
            <item id="fcfa15" label="FCFA: Science Cartesienne" />
            <item id="fcfa16" label="FCFA: Tableaux Important" />
            <item id="fcfa17" label="FCFA: planche_à_billets_Mythe_ou_Réalité" />
            <item id="fcfa18" label="FCFA: Du Financement de l’Etat du Benin" />
            <item id="fcfa19" label="FCFA: Template" />
            <item id="fcfa20" label="FCFA: Usage de nouveau vocabulaire" />
            <item id="fcfa21" label="FCFA: testing" />
          </dropDown>

          <dropDown id="dropdownFCFAFileType" label="Select Report Format"
                    onAction="RibbonCallback_FCFAFileTypeChanged">
            <item id="docx_fcfa" label="DOCX" />
            <item id="pdf_fcfa" label="PDF" />
          </dropDown>

          <button id="openFCFAFile" label="Open Selected FCFA Research Paper" 
                  onAction="RibbonCallback_OpenFCFAFile" imageMso="FileOpen"
                  description="Open the selected FCFA research paper in the chosen format." />
        </group>

        <!-- HCZ AI Research Project -->
        <group id="group5" label="HCZ AI Research Project">
          <dropDown id="dropdownAIDocument" label="Select AI Research Paper"
                    onAction="RibbonCallback_AIDocumentChanged">
            <item id="ai1" label="AI: First AI Project Objective" />
            <item id="ai2" label="AI: UserForm1" />
            <item id="ai3" label="AI: Predictive Analytics in Medicine" />
            <item id="ai4" label="AI: Large Language Models Research" />
            <item id="ai5" label="AI: Computer Vision Applications" />
          </dropDown>

          <dropDown id="dropdownAIFileType" label="Select Report Format"
                    onAction="RibbonCallback_AIFileTypeChanged">
            <item id="docx_ai" label="DOCX" />
            <item id="pdf_ai" label="PDF" />
          </dropDown>

          <button id="openAIFile" label="Open Selected AI Research Paper" 
                  onAction="RibbonCallback_OpenAIFile" imageMso="FileOpen"
                  description="Open the selected AI research paper in the chosen format." />
        </group>

      </tab>
    </tabs>
  </ribbon>
</customUI>


############  dashboard.py  ################

import streamlit as st

st.title("Illinois Asthma Hospitalization Rates")

# Dropdowns for selection
year = st.selectbox("Select Year", ["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"])
race = st.selectbox("Select Race", ["NHA", "NHB", "NHW", "HISP"])

# API request to Flask for the latest map
map_url = f"http://127.0.0.1:5000/update_map?year={year}&race={race}"

# Display the updated map dynamically
st.image(map_url, caption=f"Asthma Hospitalization for {race} in {year}")
