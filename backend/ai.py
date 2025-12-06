from transformers import  AutoProcessor, AutoModelForImageTextToText, AutoModelForSeq2SeqLM, AutoTokenizer, BitsAndBytesConfig
import torch
import requests
from langchain_openai import ChatOpenAI
import requests

def translate_text(text: str, target_lang='pl'):
    url = "https://translate.googleapis.com/translate_a/single"
    
    params = {
        "client": "gtx",      # <--- To jest klucz! 'gtx' to klient publiczny
        "sl": "auto",         # Source Language: auto-wykrywanie
        "tl": target_lang,    # Target Language: na jaki język (np. 'pl')
        "dt": "t",            # Data Type: 't' oznacza translation
        "q": text             # Tekst do przetłumaczenia
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status() 
        
        data = response.json()
        
        translated_text = "".join([sentence[0] for sentence in data[0] if sentence[0]])
        
        return translated_text

    except Exception as e:
        print(f"Error with translation: {e}")
        return text

def get_vlm(vlm_path: str, device: str = "cuda", cache_path: str = "D:/Hackathon/notebook"):
    processor = AutoProcessor.from_pretrained(vlm_path, cache_dir=cache_path)

    vlm_model = AutoModelForImageTextToText.from_pretrained(
        vlm_path,
        dtype=torch.bfloat16,
    ).to(device)
    return processor, vlm_model

def get_pllum(api: str):
    base_url = "https://apim-pllum-tst-pcn.azure-api.net/vllm/v1"
    model_name = "CYFRAGOVPL/pllum-12b-nc-chat-250715"

    llm = ChatOpenAI(
        model=model_name,
        api_key="EMPTY",
        base_url=base_url,
        temperature=0.7,
        max_tokens=300,
        default_headers={
            "Ocp-Apim-Subscription-Key": api
        }
    )
    return llm

def inference_vlm(processor, vlm, images, prompt: str, max_length: int):
    messages = [
        {
            "role": "user",
            "content": [
                *[{"type": "image", "image": img} for img in images],
                {"type": "text", "text": prompt},
            ],
        }
    ]

    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(vlm.device)

    generated_ids = vlm.generate(
        **inputs,
        do_sample=False,
        max_new_tokens=max_length,
    )

    prompt_len = inputs["input_ids"].shape[-1]
    gen_only = generated_ids[:, prompt_len:]

    output = processor.batch_decode(
        gen_only,
        skip_special_tokens=True,
    )[0].strip()
    return output

def inference_pllum(pllum, prompt: str):
    response = pllum.invoke(prompt)
    return response

def process_images(processor, vlm, images):
    DESC_PROMPT = "Can you describe with details how the lost item shown on this image looks like? Focus on the item, do not describe the background."
    DESC_MAX_RESPONSE_LENTGH = 512

    CL_PROMPT = '''
    Classify this lost item into one of the categories below. Reply only with the number:

    0 – Documents/Wallets
    1 – Electronics
    2 – Clothes/Accessories
    3 – Keys
    4 – Jewelry/Watches
    5 – Cash
    6 – Other
    '''
    CL_MAX_RESPONSE_LENTGH = 32
    
    classes = ["dokumenty_i_portfele", "elektronika", "odziez_i_akcesoria", "klucze", "bizuteria_i_zegarki", "pieniadze", "inne"]
    eng_desc = inference_vlm(processor, vlm, images, DESC_PROMPT, DESC_MAX_RESPONSE_LENTGH)
    print('we have english description')
    class_index = inference_vlm(processor, vlm, images, CL_PROMPT, CL_MAX_RESPONSE_LENTGH)
    print('agi achieved internally')
    pl_desc = translate_text(eng_desc)
    return {"kategoria": classes[int(class_index)], "opis": pl_desc}
