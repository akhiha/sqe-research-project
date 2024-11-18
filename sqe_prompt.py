from openai import OpenAI
import sys
import json
import os
import tqdm

client = OpenAI(api_key="GIVE-YOUR-KEY")



PROMPT = """
Here is a class diagram for a particular software
{uml}
Here is a vulnerability along with its description
** {title} ** :

{description}

Does the class diagram contain this particular vunerability ? If so, highlight the part where the vulnerability exists. 
I want you to follow the analysis steps mentioned below.
** Analysis ** :
{analysis}

If the specified vulnerability is not found then give "Vulnerability not Found".
"""


def get_chatgpt_response(uml, title, analysis, description):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": PROMPT.format(**locals())}
        ]
    )

    return completion.choices[0].message.content



class VulnerabilityTester:
    def __init__(self, desc_files, target_dir):
        self.desc_files = desc_files
        self.parse_desc_files()
        
    def parse_desc_files(self):
        self.desc_mapping = {}
        for fname in self.desc_files:
            fcomps = fname.split('/')
            self.desc_mapping[fcomps[1].split('.')[0]] = fname
    
    def run_vulnerability(self, vul, uml_files):
        vul_desc = json.loads(open(self.desc_mapping[vul]).read())
        title = vul_desc["title"]
        description = vul_desc["description"]
        analysis = vul_desc["analysis"]
        
        print(f"Running Vul test for {vul}")
        for filename in tqdm.tqdm(uml_files):
            fname = filename.split('/')[-1]
            with open(os.path.join(target_dir, vul, f"{fname}.md"), "w") as w:
                uml = open(filename).read()
                #print("="*20)
                #print(f"{filename} -- {vul}")
                #print(PROMPT.format(**locals()))
                res = get_chatgpt_response(uml, title, analysis, description)
                w.write(res)

    
    

    
if __name__ == "__main__":
    uml_file_list = open(sys.argv[1]).readlines()
    uml_file_list = [x.strip() for x in uml_file_list] 
    
    desc_folder = sys.argv[2]
    desc_files = [os.path.join(desc_folder,x) for x in os.listdir(desc_folder) if x.endswith(".json")]
    
    print(uml_file_list)
    print(desc_files)
    
    target_dir = sys.argv[3]
    
    vul_name = sys.argv[4]
    v = VulnerabilityTester(desc_files, target_dir)
    v.run_vulnerability(vul_name, uml_file_list)

    
#    title = desc["title"]
#    analysis = desc["analysis"]
#    description = desc["description"]
    
    #print(get_chatgpt_response(uml, title, analysis, description))
    
