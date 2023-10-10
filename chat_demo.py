import os
import openai
import pandas as pd
import numpy as np
from tqdm import tqdm
import time
from joblib import Parallel, delayed
import cv2
from code_executor import CodeExecutor, CodeExecutionStatus
from config_prompts import ConfigPrompt

class DemoGoogle:
    
    def __init__(self, api_key = None):
        if api_key:
            openai.api_key = api_key
        self.version = "Demo Version"
        self.ConfigPrompt = ConfigPrompt(csv_path="MQL_dummy.csv")
        self.CodeExecutor = CodeExecutor()
        
    def prepare_question(self, question):
        question_prompt, filename = self.ConfigPrompt.get_code_prompt(question)
        messages = [{"role": "system", "content": question_prompt}] + [
                    {"role": "user", "content": f"Question: {question}"}]
        return messages, filename
    
    def prepare_summary(self, question, output):
        messages = [{"role": "system", "content": self.ConfigPrompt.summarise_prompt}] + [
                    {"role": "user", "content": f"Question: [{question}], Code output: [{output}]."}]
        return messages
    
    def execute_prompt(self, prompt):
        completion = openai.ChatCompletion.create(model="gpt-4", temperature=0, messages=prompt)
        response = completion.choices[0].message.content
        return response

    def get_summary(self, question, code_output):
        question = self.prepare_summary(question, code_output)
        return self.execute_prompt(question)

    def get_exe_output(self, question):
        response = self.execute_prompt(question)
        output = self.CodeExecutor.execute(response)
        status = output["status"]
        output = output["output"]
        return response, status, output

    def get_output(self, question, n=5):
        response, status, output = self.get_exe_output(question)
        for i in range(0, n):
            response, status, output = self.get_exe_output(question)
            if status == CodeExecutionStatus.SUCCESS:
                return response, status, output
        return response, status, output

    def clear_plot(self, unique_filename):
        if os.path.isfile(unique_filename):
            os.remove(unique_filename)

    def chat(self, question):
        question, filename = self.prepare_question(question)
        response, status, output = self.get_output(question)

        isPlot = False
        if filename:
            isPlot = True
        if status == CodeExecutionStatus.SUCCESS:
            if isPlot:
                filename = f"{filename}.png"
                if os.path.isfile(filename):
                    return status, output, filename, isPlot
                return status, "Question is too broad or confusing. Please ask again.", filename, isPlot
            else:
                summary = self.get_summary(question, output)
                return status, summary, filename, isPlot
        else:
            return status, "Question is too broad or confusing. Please ask again.", filename, isPlot
        
