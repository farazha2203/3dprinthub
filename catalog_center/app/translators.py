from __future__ import annotations
import html, json
from urllib import parse, request

from .ai_providers import AIProviderClient, _json_request, response_output_text

def google_translate(text: str, api_key: str, target="fa") -> str:
    if not text.strip(): return ""
    if not api_key.strip(): raise RuntimeError("Google Cloud Translation API key is empty.")
    endpoint="https://translation.googleapis.com/language/translate/v2?key="+parse.quote(api_key.strip())
    body=parse.urlencode({"q":text,"source":"en","target":target,"format":"text"}).encode()
    req=request.Request(endpoint,data=body,headers={"Content-Type":"application/x-www-form-urlencoded"},method="POST")
    with request.urlopen(req,timeout=60) as response:
        data=json.loads(response.read().decode())
    return html.unescape(data["data"]["translations"][0]["translatedText"])

def openai_translate(text: str, api_key: str, model="") -> str:
    if not text.strip(): return ""
    if not api_key.strip(): raise RuntimeError("OpenAI API key is empty.")
    client=AIProviderClient("openai",api_key,model)
    selected=client.choose_model(model)
    payload={
      "model":selected,
      "instructions":"Translate the supplied 3D printing product text from English to fluent Persian. Preserve measurements, brand names, material names, model identifiers, and technical terms. Return only the Persian translation.",
      "input":text
    }
    data=_json_request(f"{client.spec.base_url}/responses",api_key,payload=payload,method="POST",timeout=120)
    result=response_output_text(data)
    if not result: raise RuntimeError("OpenAI returned no translation text.")
    return result
