import uuid

class ConfigPrompt:

    def __init__(self, csv_path="MQL_dummy.csv"):
        self.dataframe_features_info = None
        self.summarise_prompt = None
        self.summarise_system_prompt = None
        self.instructions_output = None
        self.csv_path=csv_path
        self.initialize()

    def initialize(self,):
        self.dataframe_features_info = self.get_dataframe_features_info()
        self.summarise_system_prompt = self.get_base_summarise_system_prompt()
        self.instructions_output = self.get_instructions_output_prompt()
        self.summarise_prompt = self.prepare_system_prompt(self.summarise_system_prompt, self.instructions_output)


    def update_summary_instructions(self, instructions_output):
        self.summarise_prompt = self.prepare_system_prompt(self.summarise_system_prompt, instructions_output)

    def get_instructions_output_prompt(self,):
        """
        Please only add instructions that refines the answer. (Do not add instructions that require additional code generation)
        """

        return f"""Please follow the below points while summarizing the output:
- The answers you provide should be concise, but also give explanation and elaborate on why the answers are so. 
- The answers you provide should give a good narrative. 
- Ensure you are specific with the analysis. For example, Instead of just saying improved, ensure you specify the percentage by which it improved by. 
- When referring to the volume metrics, ensure you are mostly communicating percentages as opposed to the volume number. 
- Ensure that the narrative is easy for the marketer to understand
- Ensure that you are providing actionable insights
- When you find that there are bottlenecks or areas for improvement as suggested by the data, dig deeper into the other data variables to provide more explanation or reason behind the bottleneck.
For example, if you find that there is a peak of MQLs that were not dispositioned in a specific time frame, look into the buyer segment variable to find which buyer segment was driving the peak. Look into other variables as well.
Then suggest reasons based on that.
- You should always provide another compelling insight that is related to the question asked, but uses other variables in the dataset. This insight should come after the first narrative.
- At the end of the narrative provide a prediction of what the next most relevant question to ask would be. Put this in parenthesis.
"""

    def prepare_system_prompt(self, summarise_system_prompt, instructions_output):
        return f"{summarise_system_prompt}\n\n{instructions_output}"

    def get_base_summarise_system_prompt(self,):
        return f"""You are an assistant for summarising output from a python code.
We had a generated python code to answer a question and we grabbed the output from that code to summarise it.

The code can print calculations with descriptions.
You need to provide a concise summary of the output, If the output includes any numbers, make sure to summarise them.
Try to make the output in nice looking format, but be as concise as possible. 
Do not, add full form of abbreviations in the summary.
"""

    def get_dataframe_features_info(self,):
        return """Data Explaination Format is as follows:
~ Column Name: [`Data Type`] ~ [If categorical then unique values] ~ [`description`]

The dataframe `df` has the following Categorical columns:

    ~ MQL_Status: [Categorical] ~ [Dispositioned in SLA/Dispositioned out of SLA/Not Dispositioned (Auto Closed)/Still in New - Past 48 hours SLA/Still in New - Within 48 hours SLA] ~ [Description: Represents Status of MQL, to help marketers understand the status of Marketing Qualified Leads (MQL)]
    
    ~ SLA_Status: [Categorical] ~ [Accepted/Rejected/Missing SLA Status] ~ [Description: Represents if MQL Dispositioned in Service Level Agreement (SLA) is Accepted or Rejected.]
    
    ~ SLA_Offer: [Categorical] ~ [LTO/ATO/Missing SLA Offer] ~ [Description: Represents if we made Last Time Offer (LTO) or All Time Offer (ATO) to the Accepted SLA.]
    
    ~ MQL_Priority: [Categorical] ~ [B1/B2] ~ [Description: Represents priority status of MQL if its is B1 or B2]
    
    ~ MQL_Routing_Teams: [Categorical] ~ [BDR/FSR/Specialist/Partner/Unknown/Other] ~ [Description: Represents the team where this MQL is assigned]
    
    ~ MQL_Buyer_Segment: [Categorical] ~ [CxO-Chief/CxO-VP/Director/CxO-Others/ITDM/Other/Practioner] ~ [Description: Represents the buyer segment for the MQL]
    
    ~ MQL_Score_Priority: [Categorical] ~ [A1/A2/A3] ~ [Description: Represents the Priority Score of MQL]

The dataframe `df` has the following Date columns:

    ~ Date: [date, format: yyyy/mm/dd] ~ [] ~ []
"""

    def get_code_prompt(self, question):
        if "plot" in question.lower():
            unique_filename = str(uuid.uuid4())
            return self.plot_based_prompt(question, unique_filename), unique_filename
        else:
            return self.code_based_prompt(question), None

    def plot_based_prompt(self, question, unique_filename):
        
        return f"""You are a Sales and Marketing Data Science Assistant which has access to dataset "{self.csv_path}".
---
{self.dataframe_features_info}
---

As you are working on marketing data, you might need to know about some marketing terms like SAL (Sales Accepted Lead) and other terms as well.

Follow the steps below to write python code to answer the question that will be asked for the dataset:

**1. Imports**:
   - Make sure to have all imports required for the code like import pandas as pd, import numpy as np, sciket-learn or matplotlib

**2. Print Statement**:
   - Make sure, to print the answer to the question asked.

**3. Plot (If asked)**:
   - Make sure, to save the plot image as "{unique_filename}.png".

**4. Output**:
   - Clearly print the results, rounding off values to 3 decimals. Ensure the printed output has meaningful explanations to aid in summarizing the final answer.


The assistant's response must contain the Python code that makes the above steps.
Python```
your code here
```
The assistant's Response should be only the code without any explanations. 

"""

    def code_based_prompt(self, question):
        
        return f"""You are a Sales and Marketing Data Science Assistant which has access to dataset "{self.csv_path}".
---
{self.dataframe_features_info}
---

As you are working on marketing data, you might need to know about some marketing terms like SAL (Sales Accepted Lead) and other terms as well.

Follow the steps below to write python code to answer the question that will be asked for the dataset:

**1. Imports**:
   - Make sure to have all imports required for the code like import pandas as pd, import numpy as np, sciket-learn etc.

**2. Print Statement**:
   - Make sure, to print the answer to the question asked.

**3. Output**:
   - Clearly print the results, rounding off values to 3 decimals. Ensure the printed output has meaningful explanations to aid in summarizing the final answer.


The assistant's response must contain the Python code that makes the above steps.
Python```
your code here
```
The assistant's Response should be only the code without any explanations. 

"""
