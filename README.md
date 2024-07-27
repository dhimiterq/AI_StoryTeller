# AI_StoryTeller

Story narration using an AI chatbot with memory and vocal narration capability

## Description

This application implements storytelling using generative AI.
A stable difussion server communicates with the backend via websockets to receives images
encoded as binary packets which are then sent via websockets to the frontend. Vocal narration is added using Piper and 
an agentic AI with memory is used for a customized chatbot.


# Configuration

1. Install Comfyui server and download darksushimix stable diffusion model.
   ```
   wget https://civitai.com/api/download/models/56071
   ```
2. Start Comfyui server and confirm by opening http://127.0.0.1:8188
3. Install Ollama and llama3.1 or mistral/phi3.

  ```
  ollama run llama3.1
  ollama run phi3
  ollama run mistral
  ```
Edit the selected model under langgraph_agent.py

4. Install app requirements

  ```
  conda activate aistory
  pip3 install -r requirements.txt
  pip3 install --upgrade requests
  pip3 install numexpr
  pip3 install piper-tts
  python main.py 
  python3 main.py  --disable-smart-memory --listen 0.0.0.0  #alternate options for starting ComfyUI
  ```

5. Start fastapi server

```
python app.py
```




# Support:
If you find this project helpful and would like to support its development, you can buy me a coffee on Ko-Fi:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Q5Q210TA62)
[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/dhimiterqendri)
