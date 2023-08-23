from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from happytransformer import HappyTextToText, TTSettings
from sentence_transformers import SentenceTransformer, util
import pandas as pd
from pandasai import PandasAI
# from pandasai.llm.starcoder import Starcoder
from pandasai.llm import Starcoder
import json
from django.conf import settings
import os
# from pandasai import SmartDataframe


def index(request):
    return  render(request,'index.html')
def chatbot(request):
    return render(request,'chat.html')
from django.core.files.storage import FileSystemStorage






### ---------------------------------------- File upload and Accespting --------------------------------------------------




df = None  # Define the df variable in the outer scope

def upload_file(request):
    global df  # Use the global keyword to access the outer scope df variable
    
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        # Check if the file extension is allowed
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        if not any(uploaded_file.name.endswith(ext) for ext in allowed_extensions):
            return render(request, 'upload.html', {'error_message': 'Invalid file format'})

        # Save the file to the media directory
        media_root = settings.MEDIA_ROOT
        file_path = os.path.join(media_root, uploaded_file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # Read the uploaded file into the df variable
        try:
            df = pd.read_csv(file_path)  # Modify this based on your actual file format
        except Exception as e:
            return render(request, 'upload.html', {'error_message': f'Error reading file: {e}'})
        dataset_size = len(df)
        
        # Pass the dataset size to the template context
        context = {
            'dataset_size': dataset_size,
        }
        print('jkjlkj',context)
        return render(request, 'index.html', context) 
    
    return render(request, 'upload.html')

###----------------------------------------------------- End of File upload and Accespting --------------------------------------------------



### ----------------------------------------------------- Dataset Printing -------------------------------------------------------------------

def read_data_from_file1(file_path):
    if file_path.endswith('.csv'):
        data = pd.read_csv(file_path)
    elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        data = pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format")

    return data


def get_most_recent_file():
    media_folder = os.path.join(settings.MEDIA_ROOT)
    files = [f for f in os.listdir(media_folder) if os.path.isfile(os.path.join(media_folder, f))]
    most_recent_file = max(files, key=lambda f: os.path.getmtime(os.path.join(media_folder, f)))
    return os.path.join(media_folder, most_recent_file)

def show_data(request):
    file_path = get_most_recent_file()
    data = read_data_from_file1(file_path)
    context = {'data': data}
    return render(request, 'data_display.html', context)

###----------------------------------------------------- End of Dataset Printing -------------------------------------------------------------




### ----------------------------------------------------- Input Preprocessing ----------------------------------------------------------------
def read_data_from_file(file_path):
    if file_path.endswith('.csv'):
        data = pd.read_csv(file_path)
        llm = Starcoder(api_token="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")
        data = SmartDataframe(data, config={"llm": llm, 'verbose': True})

    elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        data = pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format")

    return data


def process_question(input_sentence):
    # Define reference questions
    reference_questions = [
    "print piechart over gender column",
    "who is the highest aged person",
    "which is the most frequent address?",
    "What are the common medicines used to treat Influenza?",
    "Can you list some medications for Hypertension?",
    "What is the recommended medicine for treating Diabetes?",
    "Which medications are commonly used for Asthma?",
    "What are the standard treatments for Allergies?",
    "How is patient information organized in the dataset?",
    "Can you provide an example of a patient's information, including their name, age, and visited departments?",
    "Find patients who are between the ages of 30 and 40 and have been diagnosed with Heartburn.",
    "What are the age and weight ranges associated with the '21-30' category?",
    "Which medicines are commonly prescribed for Coronary Artery Disease?",
    "List some medications used to treat Multiple Sclerosis.",
    "What are the recommended medicines for treating Gout?",
    "Find medicines suitable for Premenstrual Syndrome (PMS).",
    "Provide a list of doctor departments available in the dataset.",
    "Which doctors are associated with the 'Neurology' department?",
    "Find a doctor who specializes in Gastroenterology and is available on a specific date and time.",
    "Can you give me information about the manufacturer 'MedLife Solutions'?",
    "List some medicine manufacturers mentioned in the dataset.",
    "Find medications manufactured by 'HealthVita' for the treatment of Gastroesophageal Reflux Disease (GERD).",
    "What are the age and weight ranges for patients aged 51-60?",
    "Which age group has the minimum weight of 25 and the maximum weight of 40?",
    "How many medicines are associated with treating Diabetes?",
    "Find the diseases for which 'Sildenafil' is prescribed.",
    "Can you list some common departments found in medical institutions?",
    "Provide a brief explanation of what 'Andropause (Male Menopause)' is.",
    "Retrieve information about a patient with the name 'John Smith'.",
    "Find patients who visited the 'Cardiology' department for 'Coronary Artery Disease'.",
    "Can you give details about the patient who is 25 years old and has visited the 'Neurology' department?",
    "What medicines are commonly prescribed for 'Atrial Fibrillation' and 'Hypertension'?",
    "List the diseases for which 'Lisinopril' is a recommended medicine.",
    "Find diseases treated using 'Zolpidem' and 'Trazodone' medications.",
    "Provide a list of doctors who work in the 'Oncology' department.",
    "Can you find doctors available on a specific 'Date of Visit' and 'Time of Visit'?",
    "How many patients are between the ages of 41 and 50?",
    "List patients with weights ranging from 60 to 80 kilograms.",
    "Categorize the diseases into groups based on their treatment.",
    "List some diseases related to the nervous system.",
    "Which medicine manufacturer is associated with 'Raloxifene'?",
    "Find medicines available from 'MedicoPharm' for 'Hypothyroidism'.",
    "Are there any patients who visited multiple departments on a single 'Date of Visit'?",
    "Find patients who have been treated for 'Hypertension' and 'Diabetes'.",
    "How frequently is 'Metformin' prescribed to patients with 'Diabetes'?",
    "List the medicines prescribed most frequently across all diseases.",
    "Suggest suitable medicines for a patient aged 65 with a weight of 70 kilograms.",
    "Which age group has the highest recommended weight range?",
    "Provide information about the prevalence of 'HIV/AIDS' and 'Lung Cancer' in the dataset.",
    "Find diseases that are most commonly treated across different departments.",
    "Are there any alternative medicines for 'Influenza' treatment besides 'Oseltamivir' and 'Zanamivir'?",
    "List similar medicines for 'Gastroenteritis' apart from 'Ondansetron' and 'Loperamide'.",
    "Provide a description of what 'Oncology' deals with in the medical field.",
    "Which department specializes in treating conditions related to the heart?",
    "Compare the medicines commonly used for 'Rheumatoid Arthritis' and 'Osteoarthritis'.",
    "What are the differences in treatment options for 'Alzheimer's Disease' and 'Parkinson's Disease'?",
    "List the active ingredients present in 'Benzoyl Peroxide'.",
    "Can you provide details about the composition of 'Calcipotriene'?",
    "What is the recommended dosage for 'Interferon Beta' in treating 'Multiple Sclerosis'?",
    "Provide instructions for taking 'Lisinopril' medication.",
    "Are there any common side effects associated with 'Allopurinol'?",
    "List potential adverse effects of 'Artificial Tears' eye drops.",
    "Are there any combination treatments for 'Diabetes' that include 'Metformin' and 'Insulin'?",
    "List medicines used together for managing 'Coronary Artery Disease'.",
    "Find medicines used for 'Gastroesophageal Reflux Disease (GERD)' available on the market.",
    "Are there any shortages of 'Levothyroxine' due to its use for 'Hypothyroidism' treatment?",
    "Provide insights into which age groups are more susceptible to 'Gout'.",
    "Which diseases are more prevalent in patients aged 50 and above?",
    "What is the approximate cost of 'Tamoxifen' and 'Anastrozole' for 'Breast Cancer' treatment?",
    "Do health insurance plans typically cover the cost of 'Antiretroviral Therapy' for 'HIV/AIDS'?",
    "How effective is 'Zanamivir' in treating 'Influenza' compared to 'Oseltamivir'?",
    "Provide information about the success rate of 'Pembrolizumab' in 'Lung Cancer' treatment.",
    "List other medications that should not be taken concurrently with 'Warfarin'.",
    "Are there any potential interactions between 'Duloxetine' and 'Alprazolam'?",
    "Are there any novel treatments being explored for 'Parkinson's Disease'?",
    "What are the latest advancements in managing 'Diabetes' beyond 'Metformin' and 'Insulin'?",
    "Suggest appropriate medications for a patient aged 15 with a weight of 35 kilograms.",
    "Recommend medicines suitable for a patient in their 40s who is diagnosed with 'Depression.'"
    ]

    # Step 1: Receive the input sentence
    user_input = input_sentence.strip()

    # Step 2: Correct any spelling and grammar mistakes (using HappyTextToText)
    happy_tt = HappyTextToText("T5", "vennify/t5-base-grammar-correction")
    args = TTSettings(num_beams=5, min_length=1)
    result = happy_tt.generate_text("grammar: " + user_input, args=args)
    corrected_user_input = result.text

    # Load the SentenceTransformer model for similarity calculation
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

    # Calculate similarity scores with all reference questions
    user_input_embedding = model.encode(corrected_user_input, convert_to_tensor=True)
    reference_question_embeddings = model.encode(reference_questions, convert_to_tensor=True)
    similarity_scores = util.pytorch_cos_sim(user_input_embedding, reference_question_embeddings)[0]
    print(corrected_user_input)
    for i,score in enumerate(similarity_scores):
        if score > 0.4:  # 40% similarity threshold
            # Step 3: Replace the following code with your data loading and processing logic
            file_path = get_most_recent_file()  # Replace with your file path logic
            data = read_data_from_file1(file_path)  # Replace with your data loading logic

            # Step 4: Forward the question to the question answering model (using PandasAI)
            API_key = "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"
            llm = Starcoder(api_token=API_key)
            pandas_ai = PandasAI(llm, conversational=False, verbose=True)

            # Assuming you have a DataFrame 'data_frame' from your data loading
            response = pandas_ai.run(data, prompt=corrected_user_input)
            print('typeeeeeeeeee',type(response))
            print(response,'resssssssssssssssssssss')
            if isinstance(response, int) or isinstance(response, float):
                # If the response is int or float, convert it to str
                response_html = str(response)
            elif isinstance(response, str):
                # Response is already a string, no conversion needed
                response_html = response
            elif isinstance(response, pd.DataFrame):
                # Response is a DataFrame, render it as a table
                response_html = response.to_html(classes='table table-bordered', index=False)
            elif isinstance(response, pd.Series):
                # Response is a Series, convert it to a DataFrame and then render as a table
                response_df = pd.DataFrame({'': response.index, 'Count': response.values})
                response_html = response_df.to_html(classes='table table-bordered', index=False)
            else:
                # Response is not handled, convert it to a string
                response_html = str(response)

            # Return a JSON response
            return JsonResponse({'response': response_html})

            # if isinstance(response, int) or isinstance(response, float) or isinstance(response, str):
            #     # If the response is int, float, or str, return it directly
            #     response_data = {"response": response}
            # elif isinstance(response, pd.Series):
            #     # If the response is a Pandas Series, convert it to a DataFrame and then to JSON
            #     response_data = {"response": response.to_frame().reset_index().to_json(orient='table')}
            #     return JsonResponse(response_data)
            # elif isinstance(response, pd.DataFrame):
            #     # If the response is a DataFrame, convert it to JSON
            #     response_data = {"response": response.to_json(orient='table')}
            #     return JsonResponse(response_data)
            # else:
            #     # Handle other types of responses as needed
            #     response_data = {"response": str(response)}
            #     print('lastjlskdjflskdjlfsk', response_data)
                    # return JsonResponse(response)  # Return JSON response for other response types


    # No matching question found
    error_message = "Your question doesn't meet the similarity threshold."
    return JsonResponse({"error": error_message})



@csrf_exempt  # To disable CSRF protection for this view (for demonstration purposes)
def get_response(request):
    if request.method == "POST":
        msg = request.POST.get("msg", "")
        response = process_question(msg)

        return response  # Return the JSON response directly

    return JsonResponse({"error": "Invalid request method"})
